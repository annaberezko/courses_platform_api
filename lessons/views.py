from django.contrib.postgres.aggregates import ArrayAgg
from rest_framework import generics

from courses.models import Course
from courses_platform_api.mixins import ImageMixin
from courses_platform_api.permissions import IsSuperuserAllOrOwnerAllOrCuratorActiveCoursesReadOnlyLearnerReadOnly, \
    LessonPermission
from lessons.models import Lesson, Material
from lessons.serializers import LessonsListSerializer, LessonSerializer, MaterialSerializer


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

    def perform_create(self, serializer):
        slug = self.kwargs['slug']
        if course := Course.objects.get(slug=slug):
            Lesson.objects.create(**serializer.validated_data, course=course)


class LessonAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (LessonPermission, )

    def get_queryset(self):
        if self.request.method == 'GET':
            pk = self.kwargs['pk']
            return Lesson.objects.values('free_access', 'name', 'video', 'text', 'home_task').\
                annotate(materials_list=ArrayAgg('materials__file')).filter(pk=pk)
        return super().get_queryset()


class MaterialAPIView(generics.CreateAPIView):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = (LessonPermission, )

    def perform_create(self, serializer):
        pk = self.kwargs['pk']
        if lesson := Lesson.objects.get(pk=pk):
            Material.objects.create(**serializer.validated_data, lesson=lesson)


class MaterialDetailAPIView(MaterialAPIView, generics.RetrieveUpdateDestroyAPIView):
    lookup_url_kwarg = 'material_pk'

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.file:
            ImageMixin.remove(instance.file)
        serializer.save()

    def perform_destroy(self, instance):
        if instance.file:
            ImageMixin.remove(instance.file)
        instance.delete()
