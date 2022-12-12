from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APITestCase, APIClient

from courses.models import Course, Permission
from users.choices_types import ProfileRoles
from users.models import InvitationToken, Lead

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
        self.assertTrue(InvitationToken.objects.filter(user=self.user).first())

    def test_security_code_empty_data(self):
        data = {}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'][0], 'This field is required.')
        self.assertEqual(response.data['security_code'][0], 'This field is required.')


class RecoveryPasswordTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('v1.0:users:recovery-password')
        self.user = User.objects.create_user(email='user@user.user', password='Vtam!ndpr123')
        self.token = str(InvitationToken.objects.create(user=self.user))

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
        self.assertEqual(response.data['error'][0], 'Old password can not be used.')


class UserSignUpAPIViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('v1.0:users:sign-up')
        self.data = {
            'email': 'user@user.user',
            'password': '12Jsirvm&*knv4',
            'confirm_password': '12Jsirvm&*knv4'
        }

    def test_create_user_profile_without_full_name(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_profile_without_first_name(self):
        self.data.update({'last_name': 'Last name'})
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['last_name'])

    def test_create_user_profile_without_last_name(self):
        self.data.update({'first_name': 'First name'})
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['first_name'])

    def test_create_user_profile_with_full_name(self):
        self.data.update({'first_name': 'First name'})
        self.data.update({'last_name': 'Last name'})
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['first_name'])
        self.assertTrue(response.data['last_name'])

    def test_ensure_without_email_will_not_create_user_profile(self):
        self.data.pop('email')
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'][0], 'This field is required.')

    def test_ensure_without_password_will_not_create_user_profile(self):
        self.data.pop('password')
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0], 'This field is required.')

    def test_ensure_without_confirm_password_will_not_create_user_profile(self):
        self.data.pop('confirm_password')
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['confirm_password'][0], 'This field is required.')

    def test_ensure_when_password_not_the_same_with_confirm_password_will_not_create_user_profile(self):
        self.data['confirm_password'] = "12Jsirvm&*knv4_no"
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_already_exist_ensure_rase_validation_error(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'][0], "user with this email address already exists.")


class UsersListAPIViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('v1.0:users:users-list')
        self.user = User.objects.create_superuser(email='super@super.super', password='strong')
        self.user1 = User.objects.create_superuser(email='user1@user.com', password='strong')
        self.user2 = User.objects.create_user(email='user2@user.com', password='strong', role=ProfileRoles.ADMINISTRATOR)
        self.user3 = User.objects.create_user(email='user3@user.com', password='strong', role=ProfileRoles.ADMINISTRATOR)
        self.user4 = User.objects.create_user(email='user4@user.com', password='strong', role=ProfileRoles.CURATOR)
        self.user5 = User.objects.create_user(email='user5@user.com', password='strong', role=ProfileRoles.CURATOR)
        self.user6 = User.objects.create_user(email='user6@user.com', password='strong', role=ProfileRoles.CURATOR)
        self.user7 = User.objects.create_user(email='user7@user.com', password='strong', first_name="User", last_name="Aaa")
        self.user8 = User.objects.create_user(email='user8@user.com', password='strong', first_name="User", last_name="Bbb")
        self.user9 = User.objects.create_user(email='user9@user.com', password='strong', first_name="Aaa", last_name="Bbb")
        self.user10 = User.objects.create_user(email='user10@user.com', password='strong', first_name="Bbb", last_name="Aaa")
        self.user11 = User.objects.create_user(email='user11@user.com', password='strong', first_name="Bbb", last_name="Abb")
        self.user12 = User.objects.create_user(email='user12@user.com', password='strong')
        self.lead1 = Lead.objects.create(user=self.user4, lead=self.user2)
        self.lead2 = Lead.objects.create(user=self.user5, lead=self.user3)
        self.lead3 = Lead.objects.create(user=self.user6, lead=self.user3)
        self.course1 = Course.objects.create(admin=self.user2, name="Course 1")
        self.course2 = Course.objects.create(admin=self.user3, name="Course 2")
        self.course3 = Course.objects.create(admin=self.user3, name="Course 3")
        self.permission1 = Permission.objects.create(user=self.user7, course=self.course1, access=True)
        self.permission2 = Permission.objects.create(user=self.user8, course=self.course1)
        self.permission3 = Permission.objects.create(user=self.user7, course=self.course2)
        self.permission4 = Permission.objects.create(user=self.user8, course=self.course3)
        self.permission5 = Permission.objects.create(user=self.user9, course=self.course2)
        self.permission6 = Permission.objects.create(user=self.user10, course=self.course2)
        self.permission7 = Permission.objects.create(user=self.user11, course=self.course2)
        self.permission8 = Permission.objects.create(user=self.user12, course=self.course2)

        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'super@super.super', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

        self.data = {
            'email': 'user@user.user',
            'password': '12Jsirvm&*knv4',
            'confirm_password': '12Jsirvm&*knv4',
            'role': 2,
            'first_name': 'UserFirst',
            'last_name': 'UserLast',
            'phone': 777777777,
            'instagram': 'googleaccaunt',
            'facebook': 'facebookaccount',
        }

    def test_users_list_unauthorized_permission_no_access(self):
        client = APIClient()
        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_users_list_learner_permission_no_access(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user7@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_superuser_see_all_roles_except_superusers(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 11)
        self.assertTrue(type(response.data['results'][0]['role']) is str)

    def test_list_administrator_without_access_see_5_his_learners(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user2@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_list_administrator_with_access_see_his_curators_and_learners(self):
        Permission.objects.create(user=self.user3, access=True)
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user3@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 8)

    def test_list_user_with_filter_by_course_search(self):
        Permission.objects.create(user=self.user3, access=True)
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user3@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url + '?course_search=' + self.course2.slug)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)

    def test_list_administrator_without_access_see_only_five_curators_and_courses(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user3@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)
        self.assertTrue(type(response.data['results'][0]['role']) is str)

    def test_list_curator_see_all_belows_roles_and_dont_see_users_contact_data(self):
        self.assess = Permission.objects.create(user=self.user2, access=True)
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user4@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse('phone' in response.data['results'][0])
        self.assertEqual(response.data['count'], 1)
        self.assertTrue(type(response.data['results'][0]['role']) is str)

    def test_list_curator_see_all_his_accesses_admin_members_list(self):
        self.assess = Permission.objects.create(user=self.user3, access=True)
        self.lead1 = Lead.objects.create(user=self.user4, lead=self.user3)
        Permission.objects.filter(user=self.user7, course=self.course2).update(access=True)
        Permission.objects.filter(user=self.user8, course=self.course3).update(access=True)
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user4@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_list_curator_dont_see_list_of_members_when_administrator_dont_have_access(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user4@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_users_list_ordering_by_fullname_desc(self):
        response = self.client.get(self.url + '?ordering=-full_name')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['full_name'], "User Bbb")
        self.assertEqual(response.data['results'][1]['full_name'], "User Aaa")
        self.assertEqual(response.data['results'][2]['full_name'], "Bbb Abb")
        self.assertEqual(response.data['results'][3]['full_name'], "Bbb Aaa")

    def test_superuser_create_administrator_and_send_invitation_mail(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 1)

    def test_superuser_create_curator_and_send_invitation_mail(self):
        self.data['role'] = 3
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 1)

    def test_curator_permission_no_access_to_post_method(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user4@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_administrator_create_curator_send_email_and_set_lead(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user2@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        self.data['role'] = 3
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(Lead.objects.filter(user__email=self.data['email'], lead=self.user2).exists())


class RolesListAPIViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('v1.0:users:roles-list')
        self.user = User.objects.create_superuser(email='super@super.super', password='strong')
        self.user2 = User.objects.create_user(email='user2@user.com', password='strong', role=ProfileRoles.ADMINISTRATOR)
        self.user3 = User.objects.create_user(email='user3@user.com', password='strong', role=ProfileRoles.CURATOR)
        self.user4 = User.objects.create_user(email='user4@user.com', password='strong')
        self.client = APIClient()

    def test_roles_list_unauthorized_permission_no_access(self):
        client = APIClient()
        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_roles_list_learner_permission_no_access(self):
        client = APIClient()
        res = client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user4@user.com', 'password': 'strong'})
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_roles_list_curator_permission_no_access(self):
        client = APIClient()
        res = client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user3@user.com', 'password': 'strong'})
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_roles_list_administrator_permission_no_access(self):
        client = APIClient()
        res = client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user2@user.com', 'password': 'strong'})
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_roles_list_superuser_see_all_roles_except_superuser(self):
        client = APIClient()
        res = client.post(reverse('v1.0:token_obtain_pair'), {'email': 'super@super.super', 'password': 'strong'})
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['roles_list']), 3)


class AdministratorsListAPIViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('v1.0:users:administrators-list')
        self.user = User.objects.create_superuser(email='super@super.super', password='strong')
        self.user1 = User.objects.create_user(email='user1@user.com', password='strong', role=ProfileRoles.ADMINISTRATOR)
        self.user2 = User.objects.create_user(email='user2@user.com', password='strong', role=ProfileRoles.ADMINISTRATOR)
        self.user3 = User.objects.create_user(email='user3@user.com', password='strong', role=ProfileRoles.ADMINISTRATOR)
        self.user4 = User.objects.create_user(email='user4@user.com', password='strong', role=ProfileRoles.CURATOR)
        self.user5 = User.objects.create_user(email='user5@user.com', password='strong', role=ProfileRoles.CURATOR)
        self.user6 = User.objects.create_user(email='user6@user.com', password='strong')
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'super@super.super', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        self.response = self.client.get(self.url)

    def test_administrators_list_unauthorized_permission_no_access(self):
        client = APIClient()
        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_administrators_list_administrator_permission_no_access(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user1@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_administrators_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserAPIViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(email='super@super.super', password='strong')
        self.user1 = User.objects.create_user(email='user1@user.com', password='strong', role=ProfileRoles.ADMINISTRATOR)
        self.user2 = User.objects.create_user(email='user2@user.com', password='strong', role=ProfileRoles.ADMINISTRATOR)
        self.user3 = User.objects.create_user(email='user3@user.com', password='strong', role=ProfileRoles.CURATOR)
        self.user4 = User.objects.create_user(email='user4@user.com', password='strong', role=ProfileRoles.CURATOR)
        self.user5 = User.objects.create_user(email='user5@user.com', password='strong')
        self.user6 = User.objects.create_user(email='user6@user.com', password='strong')
        self.course = Course.objects.create(admin=self.user1, name="Course 1")
        self.permission1 = Permission.objects.create(user=self.user1, access=True)
        self.permission2 = Permission.objects.create(user=self.user5, course=self.course, access=True)
        self.permission3 = Permission.objects.create(user=self.user6, course=self.course)

        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user1@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

        self.url = reverse('v1.0:users:user-detail', args=[self.user6.slug])
        self.response = self.client.get(self.url)

        self.data = {
            'first_name': 'UserFirst',
            'last_name': 'UserLast',
            'phone': 777777777,
            'instagram': 'googleaccaunt',
            'facebook': 'facebookaccount',
        }

    def test_user_detail_unauthorized_permission_no_access(self):
        client = APIClient()
        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_detail_learner_permission_no_access(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user5@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_detail_curator_read_only(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user4@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_detail_admin_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(type(response.data['role']) is str)

    def test_user_detail_admin_patch(self):
        response = self.client.patch(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user6 = User.objects.filter(slug=self.user6.slug).values_list('first_name', 'last_name')[0]
        self.assertFalse(self.user6.first_name == user6[0])
        self.assertFalse(self.user6.last_name == user6[1])
        response = self.client.patch(self.url, {'role': ProfileRoles.CURATOR})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(User.objects.filter(pk=self.user6.id, role=ProfileRoles.CURATOR).exists())
        response = self.client.patch(self.url, {'email': 'new_email@user.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(User.objects.filter(pk=self.user6.id, email='new_email@user.com').exists())
        response = self.client.patch(self.url, {'phone': '88888888'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.patch(self.url, {'phone': '12345678901234567'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.patch(self.url, {'phone': '1234567890123456'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(self.url, {'phone': '999999999'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_detail_admin_delete(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
