from django.urls import path

from lessons.views import LessonsListAPIView, LessonAPIView

app_name = 'lessons'

urlpatterns = [
    path('', LessonsListAPIView.as_view(), name='lesson-list'),
    path('<int:pk>/', LessonAPIView.as_view(), name='lesson-detail'),
    ]
