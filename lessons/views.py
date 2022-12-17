from rest_framework import generics
from rest_framework.permissions import AllowAny

from lessons.models import Lesson
from lessons.serializers import LessonsListSerializer


class LessonsListAPIView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonsListSerializer
    permission_classes = (AllowAny, )
