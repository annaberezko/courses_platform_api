from django.urls import path, include

from courses.views import CoursesListAPIView, CourseAPIView, CoursesShortListAPIView, CoursesSwitchStatusAPIView, \
    CourseLearnersListAPIView, CourseLearnerSwitchAccessAPIView, CourseCuratorsListAPIView

app_name = 'courses'

urlpatterns = [
    path('', CoursesListAPIView.as_view(), name='course-list'),
    path('short-list/', CoursesShortListAPIView.as_view(), name='course-short-list'),
    path('<str:slug>/', CourseAPIView.as_view(), name='course-detail'),
    path('<str:slug>/lessons/', include('lessons.urls')),
    path('<str:slug>/curators/', CourseCuratorsListAPIView.as_view(), name='course-curator-list'),
    path('<str:slug>/learners/', CourseLearnersListAPIView.as_view(), name='course-learner-list'),
    path('<str:slug>/learners/<str:user_slug>/switch-status/', CourseLearnerSwitchAccessAPIView.as_view(),
         name='course-learner-switch-status'),
    path('<str:slug>/switch-status/', CoursesSwitchStatusAPIView.as_view(), name='course-switch-status'),
    ]
