from django.urls import path

from courses.views import CoursesListAPIView, CourseAPIView, CoursesShortListAPIView, CoursesSwitchStatusAPIView, \
    CourseLearnersListAPIView, CourseLearnerSwitchAccessAPIView

app_name = 'courses'

urlpatterns = [
    path('', CoursesListAPIView.as_view(), name='courses-list'),
    path('short-list/', CoursesShortListAPIView.as_view(), name='courses-short-list'),
    path('<str:slug>/', CourseAPIView.as_view(), name='course-detail'),
    path('<str:slug>/learners/', CourseLearnersListAPIView.as_view(), name='course-learners-list'),
    path('<str:slug>/learners/<str:user_slug>/switch-status/', CourseLearnerSwitchAccessAPIView.as_view(),
         name='course-learner-switch-status'),
    path('<str:slug>/switch-status/', CoursesSwitchStatusAPIView.as_view(), name='course-switch-status'),
    ]
