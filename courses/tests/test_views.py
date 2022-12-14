from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from courses.models import Course, Permission
from courses_platform_api.choices_types import ProfileRoles
from users.models import Lead

User = get_user_model()


class CoursesListAPIViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('v1.0:courses:course-list')
        self.user = User.objects.create_superuser(email='super@super.super', password='strong')
        self.user1 = User.objects.create_user(email='user1@user.com', password='strong', role=ProfileRoles.ADMINISTRATOR)
        self.user2 = User.objects.create_user(email='user2@user.com', password='strong', role=ProfileRoles.ADMINISTRATOR)
        self.user3 = User.objects.create_user(email='user3@user.com', password='strong', role=ProfileRoles.ADMINISTRATOR)
        self.user4 = User.objects.create_user(email='user4@user.com', password='strong', role=ProfileRoles.CURATOR)
        self.user5 = User.objects.create_user(email='user5@user.com', password='strong', role=ProfileRoles.CURATOR)
        self.user6 = User.objects.create_user(email='user6@user.com', password='strong')
        self.permission = Permission.objects.create(user=self.user1, access=True)
        self.lead1 = Lead.objects.create(user=self.user4, lead=self.user1)
        self.lead2 = Lead.objects.create(user=self.user5, lead=self.user1)
        self.lead3 = Lead.objects.create(user=self.user5, lead=self.user2)
        self.course1 = Course.objects.create(admin=self.user1, name="Course 1")
        self.course2 = Course.objects.create(admin=self.user2, name="Course 2")
        self.course3 = Course.objects.create(admin=self.user1, name="Course 3")
        self.course4 = Course.objects.create(admin=self.user1, name="Course 4")
        self.course5 = Course.objects.create(admin=self.user2, name="Course 5", is_active=False)

        self.permission1 = Permission.objects.create(user=self.user6, course=self.course1, access=True)
        self.permission2 = Permission.objects.create(user=self.user6, course=self.course2)

        self.data = {
            'name': 'New Course'
        }

        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'super@super.super', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

    def test_courses_list_unauthorized_permission_no_access(self):
        client = APIClient()
        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_courses_list_learner_permission_post_method_no_access(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user6@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_courses_list_learner_permission_get_method_accesses(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user6@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['access'], True)
        self.assertEqual(response.data['results'][1]['access'], False)

    def test_courses_list_superuser_see_all_courses(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)
        self.assertTrue(type(response.data['results'][0]['admin']) is str)

    def test_courses_list_administrator_see_only_his_courses(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user1@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        self.assertTrue(type(response.data['results'][0]['admin']) is str)

    def test_courses_list_administrator_without_courses_see_empty_list(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user3@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_courses_list_curator_with_one_admin_see_only_his_administrator_courses(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user4@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        self.assertTrue(type(response.data['results'][0]['admin']) is str)

    def test_courses_list_curator_with_two_admin_see_only_his_administrators_courses(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user5@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 4)
        self.assertTrue(type(response.data['results'][0]['admin']) is str)

    def test_curator_permission_no_access_to_post_method(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user4@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_create_new_course_empty_data_error(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_superuser_create_new_course_without_user_error(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_superuser_create_new_course(self):
        self.data.update({'admin_id': self.user3.id})
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_superuser_create_new_course_with_all_data(self):
        self.data.update({
            'admin_id': self.user3.id,
            'cover': "",
            'description': 'Course description',
            'sequence': True
        })
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_administrator_create_many_courses_if_he_is_active(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user1@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        self.data.update({'admin_id': self.user1.id})
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_administrator_create_only_one_course_if_he_is_not_active(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user3@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        self.data.update({'admin_id': self.user3.id})
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CourseAPIViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(email='super@super.super', password='strong')
        self.user1 = User.objects.create_user(email='user1@user.com', password='strong', role=ProfileRoles.ADMINISTRATOR)
        self.user2 = User.objects.create_user(email='user2@user.com', password='strong', role=ProfileRoles.ADMINISTRATOR)
        self.user3 = User.objects.create_user(email='user3@user.com', password='strong', role=ProfileRoles.ADMINISTRATOR)
        self.user4 = User.objects.create_user(email='user4@user.com', password='strong', role=ProfileRoles.CURATOR)
        self.user5 = User.objects.create_user(email='user5@user.com', password='strong', role=ProfileRoles.CURATOR)
        self.user6 = User.objects.create_user(email='user6@user.com', password='strong')
        self.lead1 = Lead.objects.create(user=self.user4, lead=self.user1)
        self.lead2 = Lead.objects.create(user=self.user5, lead=self.user1)
        self.lead3 = Lead.objects.create(user=self.user5, lead=self.user2)
        self.course1 = Course.objects.create(admin=self.user1, name="Course 1")
        self.course2 = Course.objects.create(admin=self.user2, name="Course 2")
        self.course3 = Course.objects.create(admin=self.user1, name="Course 3")
        self.course4 = Course.objects.create(admin=self.user1, name="Course 4")
        self.course5 = Course.objects.create(admin=self.user2, name="Course 5", is_active=False)

        self.permission1 = Permission.objects.create(user=self.user6, course=self.course1, access=True)
        self.permission2 = Permission.objects.create(user=self.user6, course=self.course5, access=True)

        self.url = reverse('v1.0:courses:course-detail', args=[self.course1.slug])
        self.data = {
            'name': 'New Course'
        }

    def test_course_detail_page_unauthorized_permission_no_access(self):
        client = APIClient()
        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_course_detail_page_learner_permission_put_delete_method_no_access(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user6@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.patch(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    def test_course_detail_page_learner_permission_get_method_accesses(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user6@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.url = reverse('v1.0:courses:course-detail', args=[self.course5.slug])
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_course_detail_page_curator_permission_put_delete_method_no_access(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user4@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.patch(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_course_detail_page_curator_permission_get_method_accesses(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user4@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_course_detail_page_administrator_permission_all_method_access(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user1@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(self.url, data={'name': 'New course name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_course_detail_page_with_no_access_field_administrator_permission_only_get_method_access(self):
        url = reverse('v1.0:courses:course-detail', args=[self.course5.slug])
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user2@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.patch(url, data={'name': 'New course name'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_course_detail_page_curator_permission_get_only_for_access_field_only(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user5@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        url = reverse('v1.0:courses:course-detail', args=[self.course5.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CoursesSwitchStatusAPIViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(email='super@super.super', password='strong')
        self.user1 = User.objects.create_user(email='user1@user.com', password='strong', role=ProfileRoles.ADMINISTRATOR)
        self.user2 = User.objects.create_user(email='user2@user.com', password='strong', role=ProfileRoles.CURATOR)
        self.user3 = User.objects.create_user(email='user3@user.com', password='strong')
        self.course1 = Course.objects.create(admin=self.user1, name="Course 1")
        self.course2 = Course.objects.create(admin=self.user1, name="Course 2")

        self.url = reverse('v1.0:courses:course-switch-status', args=[self.course1.slug])

    def test_course_switch_status_unauthorized_permission_no_access(self):
        client = APIClient()
        response = client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_course_switch_status_learner_permission_no_access(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user3@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_course_switch_status_administrator_permission_no_access(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user2@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_course_switch_status_administrator_profile_not_accesses(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user1@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_active'], False)
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data)
        url = reverse('v1.0:courses:course-switch-status', args=[self.course2.slug])
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_active'], False)
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_active'], True)
        Permission.objects.create(user=self.user1, access=True)
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user1@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_active'], True)


class CourseLearnersMixin(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(email='super@super.super', password='strong')
        self.user1 = User.objects.create_user(email='user1@user.com', password='strong',
                                              role=ProfileRoles.ADMINISTRATOR)
        self.user2 = User.objects.create_user(email='user2@user.com', password='strong', role=ProfileRoles.CURATOR)
        self.user3 = User.objects.create_user(email='user3@user.com', password='strong')
        self.user4 = User.objects.create_user(email='user4@user.com', password='strong')
        self.user5 = User.objects.create_user(email='user5@user.com', password='strong')
        self.user6 = User.objects.create_user(email='user6@user.com', password='strong', first_name="Aaa")
        self.user7 = User.objects.create_user(email='user7@user.com', password='strong')
        self.user8 = User.objects.create_user(email='user8@user.com', password='strong')
        self.user9 = User.objects.create_user(email='user9@user.com', password='strong')
        self.user10 = User.objects.create_user(email='user10@user.com', password='strong')
        self.course1 = Course.objects.create(admin=self.user1, name="Course 1")

        self.permission1 = Permission.objects.create(user=self.user3, course=self.course1, access=True)
        self.permission2 = Permission.objects.create(user=self.user4, course=self.course1, access=True)
        self.permission3 = Permission.objects.create(user=self.user5, course=self.course1, access=True)
        self.permission4 = Permission.objects.create(user=self.user6, course=self.course1, access=True)
        self.permission5 = Permission.objects.create(user=self.user7, course=self.course1)
        self.permission6 = Permission.objects.create(user=self.user8, course=self.course1)


class CourseLearnersListAPIViewTestCase(CourseLearnersMixin):
    def setUp(self):
        super().setUp()
        self.url = reverse('v1.0:courses:course-learner-list', args=[self.course1.slug])

    def test_course_learners_list_unauthorized_permission_no_access(self):
        client = APIClient()
        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_course_learners_list_learner_permission_no_access(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user3@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_course_learners_list_curator_permission_no_access(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user2@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_course_learners_list_administrator_permission(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user1@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)

        response = self.client.get(self.url + '?access=True')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 4)

        response = self.client.get(self.url + '?ordering=-full_name')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['full_name'], 'Aaa ')


class CourseLearnerSwitchAccessAPIViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(email='super@super.super', password='strong')
        self.user1 = User.objects.create_user(email='user1@user.com', password='strong', role=ProfileRoles.ADMINISTRATOR)
        self.user2 = User.objects.create_user(email='user2@user.com', password='strong', role=ProfileRoles.CURATOR)
        self.user3 = User.objects.create_user(email='user3@user.com', password='strong')
        self.course1 = Course.objects.create(admin=self.user1, name="Course 1")
        self.permission1 = Permission.objects.create(user=self.user3, course=self.course1, access=True)

        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user1@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

        self.url = reverse('v1.0:courses:course-learner-switch-status', args=[self.course1.slug, self.user3.slug])

    def test_switch_only_access_status(self):
        response = self.client.put(self.url, {'access': False})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Permission.objects.values('access').get(course=self.course1, user=self.user3), False)

        response = self.client.put(self.url, {'access': True, 'date_end': '2025-01-01'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Permission.objects.values('date_end').get(course=self.course1, user=self.user3), '2025-01-01')


class SubscribeToCourseAPIViewAPIViewTestCase(CourseLearnersMixin):
    def setUp(self):
        super().setUp()
        self.url = reverse('v1.0:courses:subscribe-to-course', args=[self.course1.slug])

    def test_course_subscribe_unauthorized_permission_no_access(self):
        client = APIClient()
        response = client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_course_subscribe_superuser_permission_no_access(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'super@super.super', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_course_subscribe_administrator_permission_no_access(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user1@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_course_subscribe_curator_permission_no_access(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user2@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_course_subscribe_learner_without_access(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user9@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_course_subscribe_learner_with_access_do_nothing(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user3@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
