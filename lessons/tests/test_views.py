from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APITestCase, APIClient

from courses.models import Permission, Course
from courses_platform_api.choices_types import ProfileRoles
from lessons.models import Lesson, Question, Option

User = get_user_model()


class LessonInitialMixin(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(email='super@super.super', password='strong')
        self.user1 = User.objects.create_user(email='user1@user.com', password='strong', role=ProfileRoles.ADMINISTRATOR)
        self.user2 = User.objects.create_user(email='user2@user.com', password='strong', role=ProfileRoles.ADMINISTRATOR)
        self.user3 = User.objects.create_user(email='user3@user.com', password='strong', role=ProfileRoles.ADMINISTRATOR)
        self.user4 = User.objects.create_user(email='user4@user.com', password='strong', role=ProfileRoles.CURATOR)
        self.user5 = User.objects.create_user(email='user5@user.com', password='strong', role=ProfileRoles.LEARNER)

        self.course1 = Course.objects.create(admin=self.user1, name="Course 1")
        self.course2 = Course.objects.create(admin=self.user2, name="Course 2")
        self.course3 = Course.objects.create(admin=self.user1, name="Course 3")
        self.course4 = Course.objects.create(admin=self.user2, name="Course 4", is_active=False)

        self.lesson1 = Lesson.objects.create(course=self.course1, free_access=True)
        self.lesson2 = Lesson.objects.create(course=self.course1)

        self.permission1 = Permission.objects.create(user=self.user1, access=True)
        self.permission2 = Permission.objects.create(user=self.user5, access=True, course=self.course1)

        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'super@super.super', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")


class LessonsListAPIViewTestCase(LessonInitialMixin):
    def setUp(self):
        super().setUp()
        self.url = reverse('v1.0:courses:lessons:lesson-list', args=[self.course1.slug])
        self.data = {
            'name': 'New Lesson'
        }

        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'super@super.super', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

    def test_lessons_list_unauthorized_permission_no_access(self):
        client = APIClient()
        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_lessons_list_learner_permission_post_method_no_access(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user5@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lessons_list_curator_permission_post_method_no_access(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user4@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lessons_list_admin_permission_auto_course_id(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user1@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.values('name').last()['name'], self.data['name'])
        self.assertEqual(Lesson.objects.values('course').last()['course'], self.course1.id)

    def test_lessons_list_superuser_permission(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'super@super.super', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class LessonAPIViewTestCase(LessonInitialMixin):
    def setUp(self):
        super().setUp()
        self.url = reverse('v1.0:courses:lessons:lesson-detail', args=[self.course1.slug, self.lesson1.pk])
        self.data = {
            'free_access': True,
            'name': 'New Lesson Name',
            'video': '',
            'text': 'New text',
            'home_task': 'Task detail text'
        }

    def test_lesson_unauthorized_permission_no_access(self):
        client = APIClient()
        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_lesson_learner_permission_post_method_no_access(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user5@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_curator_permission_post_method_no_access(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user4@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_admin_not_owner_no_access(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user2@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_admin_owner_retrieve_update(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user1@user.com', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.put(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class QuestionsListAPIViewTestCase(LessonInitialMixin):
    def setUp(self):
        super().setUp()
        self.url = reverse('v1.0:courses:lessons:lesson-test', args=[self.course1.slug, self.lesson1.pk])
        self.data = {
            "question": "Is it the best question text?",
            "options": [
                {
                    "option": "Option 1",
                    "correct": True
                },
                {
                    "option": "Option 2"
                },
                {
                    "option": "Option 3"
                }
            ]
        }
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'super@super.super', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

    def test_lesson_test_question_creation(self):
        response = self.client.post(self.url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_question_update_data(self):
        self.test_lesson_test_question_creation()
        question = Question.objects.last()
        self.url = reverse('v1.0:courses:lessons:lesson-test-detail', args=[self.course1.slug, self.lesson1.pk, question.pk])

        options = Option.objects.all().order_by('id')
        new_data = {
            "question": "Is it the new question text?",
            "options": [
                {
                    "id": options[0].id,
                    "option": "Option 1 new"
                },
                {
                    "id": options[1].id,
                    "option": "Option 2",
                    "correct": True
                },
                {
                    "option": "Option 4"
                }
            ]
        }
        response = self.client.put(self.url, new_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        options = Option.objects.all().order_by('id')
        self.assertEqual(Question.objects.last().question, "Is it the new question text?")
        self.assertEqual(options.count(), 4)
        self.assertEqual(options[0].option, "Option 1 new")
        self.assertEqual(options[0].correct, False)

        url = reverse('v1.0:courses:lessons:option-detail', args=[
            self.course1.slug,
            self.lesson1.pk,
            question.pk,
            options[3].pk
        ])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Option.objects.all().count(), 3)
