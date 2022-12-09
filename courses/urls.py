from django.urls import path

from courses.views import CoursesListAPIView, CourseAPIView, CoursesShortListAPIView, CoursesSwitchStatusAPIView

app_name = 'courses'

urlpatterns = [
    path('', CoursesListAPIView.as_view(), name='courses-list'),
    path('short-list/', CoursesShortListAPIView.as_view(), name='courses-short-list'),
    path('<str:slug>/', CourseAPIView.as_view(), name='course-detail'),
    path('<str:slug>/switch-status/', CoursesSwitchStatusAPIView.as_view(), name='switch-status'),
    ]
