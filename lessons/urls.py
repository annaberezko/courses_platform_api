from django.urls import path

from lessons.views import LessonsListAPIView

app_name = 'lessons'

urlpatterns = [
    path('', LessonsListAPIView.as_view(), name='lessons-list'),
    ]