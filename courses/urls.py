from django.urls import path

from courses.views import CoursesListAPIView, CourseAPIView

app_name = 'courses'

urlpatterns = [
    path('', CoursesListAPIView.as_view(), name='courses-list'),
    path('<str:slug>/', CourseAPIView.as_view(), name='course-detail')
    ]
