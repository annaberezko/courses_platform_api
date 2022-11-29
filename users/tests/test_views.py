from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APITestCase, APIClient

from users.models import InvitationToken

User = get_user_model()


class TokenObtainPairViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('v1.0:token_obtain_pair')
        self.user = User.objects.create_superuser(email='super@super.super', password='strong')

    def test_ensure_that_client_provide_correct_data(self):
        response = self.client.post(self.url, {'email': 'super@super.super', 'password': 'strong'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)

    def test_ensure_that_client_provide_incorrect_data(self):
        response = self.client.post(self.url, {'email': 'uper@super.super', 'password': 'strong'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ensure_that_client_doesnt_provide_any_data(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ensure_that_inactive_user_have_no_access(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post(self.url, {'email': 'super@super.super', 'password': 'strong'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ResetPasswordRequestEmailTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('v1.0:users:forgot-password')
        self.user = User.objects.create_user(email='user@user.user')

    def test_forgot_password_email_not_in_the_system(self):
        data = {'email': 'no@no.no'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'There is no account with that email.')

    def test_forgot_password_email_in_the_system_check_response(self):
        data = {'email': self.user.email}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(User.objects.get(email=self.user.email).security_code), 6)

    def test_forgot_password_if_request_data_is_empty(self):
        data = {}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'][0], 'This field is required.')


class NewSecurityCodeTestCase(APITestCase):
    def test_send_security_code_again_code_change(self):
        user = User.objects.create_user(email='user@user.user')
        security_code = user.generate_security_code()
        self.assertEqual(len(security_code), 6)
        self.assertFalse(user.security_code == security_code)


class ResetPasswordSecurityCodeTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('v1.0:users:security-code')
        self.user = User.objects.create_user(email='user@user.user', security_code='123456')

    def test_security_code_email_not_in_the_system(self):
        data = {'email': 'no@no.no', 'security_code': '000000'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'There is no user with that email.')

    def test_security_code_wrong_code(self):
        data = {'email': self.user.email, 'security_code': '000000'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'],
                         'Incorrect security code. Check your secure code or request for a new one.')

    def test_security_code_generate_token(self):
        data = {'email': self.user.email, 'security_code': self.user.security_code}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)
        self.assertEqual(len(mail.outbox), 1)

    def test_security_code_empty_data(self):
        data = {}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'][0], 'This field is required.')
        self.assertEqual(response.data['security_code'][0], 'This field is required.')


class CreateNewPasswordTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('v1.0:users:create-new-password')
        self.user = User.objects.create_user(email='user@user.user', password='Vtam!ndpr123')
        self.token = str(InvitationToken.objects.filter(user=self.user).first())

    def test_create_new_password_add_email_field(self):
        data = {'token': self.token, 'password': 'User-password123', 'confirm_password': 'User-password123'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)

    def test_create_new_password_wrong_token(self):
        data = {'token': 'wrong-token', 'password': 'User-password123', 'confirm_password': 'User-password123'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'][0], 'Invalid token.')

    def test_create_new_password_compare_passwords_not_the_same(self):
        data = {'token': self.token, 'password': 'User-password123', 'confirm_password': 'User-password321'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'][0], 'Passwords do not match.')

    def test_create_new_password_correct(self):
        data = {'token': self.token, 'password': 'User-password123', 'confirm_password': 'User-password123'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.user.password == data['password'])

    def test_create_new_password_empty_data(self):
        data = {}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['token'][0], 'This field is required.')
        self.assertEqual(response.data['password'][0], 'This field is required.')
        self.assertEqual(response.data['confirm_password'][0], 'This field is required.')

    def test_create_new_password_after_successful_request_token_was_removed_from_the_system(self):
        data = {'token': self.token, 'password': 'User-password123', 'confirm_password': 'User-password123'}
        self.assertTrue(InvitationToken.objects.filter(user=self.user).exists())
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(InvitationToken.objects.filter(user=self.user).exists())
        user = User.objects.get(id=self.user.id)
        self.assertTrue(user.check_password(data['password']))

    def test_ensure_password_is_valid(self):
        data = {'token': self.token, 'password': '12Jsirvm&*knv4', 'confirm_password': '12Jsirvm&*knv4'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_ensure_minimum_length_is_invalid(self):
        data = {'token': self.token, 'password': '12Jsir*', 'confirm_password': '12Jsir*'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0],
                         "This password is too short. It must contain at least %d characters." % 8)

    def test_ensure_maximum_length_is_invalid(self):
        data = {'token': self.token, 'password': '12Jsir*r' * 100, 'confirm_password': '12Jsir*r' * 100}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0], "This password must contain at most %d characters." % 128)

    def test_ensure_password_include_no_uppercase_letters(self):
        data = {'token': self.token, 'password': 'disnt&ie)1',
                'confirm_password': 'disnt&ie)1'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0], "The password must contain at least 1 uppercase letter, A-Z.")

    def test_ensure_password_include_no_lowercase_letters(self):
        data = {'token': self.token, 'password': '174HDOR9SH&%JD',
                'confirm_password': '174HDOR9SH&%JD'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0], "The password must contain at least 1 lowercase letter, a-z.")

    def test_ensure_password_include_no_symbols(self):
        data = {'token': self.token, 'password': 'irnxyYNDR5375',
                'confirm_password': 'irnxyYNDR5375'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0], "The password must contain at least 1 special character: " +
                         "()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?")

    def test_ensure_password_include_no_digits(self):
        data = {'token': self.token, 'password': 'Yjduc&%jeu', 'confirm_password': 'Yjduc&%jeu'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0], "The password must contain at least 1 digit, 0-9.")

    def test_ensure_old_password_not_used_as_new(self):
        data = {'token': self.token, 'password': 'Vtam!ndpr123', 'confirm_password': 'Vtam!ndpr123'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'][0], 'This password can not be used.')
