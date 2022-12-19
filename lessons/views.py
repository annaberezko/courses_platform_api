from django.contrib.postgres.aggregates import ArrayAgg
from rest_framework import generics

from courses.models import Course
from courses_platform_api.permissions import IsSuperuserAllOrOwnerAllOrCuratorActiveCoursesReadOnlyLearnerReadOnly, \
    LessonPermission
from lessons.models import Lesson
from lessons.serializers import LessonsListSerializer, LessonSerializer


class LessonsListAPIView(generics.ListCreateAPIView):
    serializer_class = LessonsListSerializer
    permission_classes = (IsSuperuserAllOrOwnerAllOrCuratorActiveCoursesReadOnlyLearnerReadOnly, )

    def get_queryset(self):
        slug = self.kwargs['slug']
        course = Course.objects.get(slug=slug)
        return Lesson.objects.filter(course=course)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LessonSerializer
        return self.serializer_class


class LessonAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (LessonPermission, )

    def get_queryset(self):
        pk = self.kwargs['pk']

        return Lesson.objects.values('free_access', 'name', 'video', 'text', 'home_task').\
            annotate(materials_list=ArrayAgg('materials__file')).filter(pk=pk)