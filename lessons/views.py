from django.contrib.postgres.aggregates import ArrayAgg
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course
from courses_platform_api.mixins import ImageMixin
from courses_platform_api.permissions import IsSuperuserAllOrOwnerAllOrCuratorActiveCoursesReadOnlyLearnerReadOnly, \
    LessonPermission, IsLessonLearnerAll
from lessons.models import Lesson, Material, Question, Option, Answer, Result, ImageTask, Task
from lessons.serializers import LessonsListSerializer, LessonSerializer, MaterialSerializer, QuestionSerializer, \
    OptionSerializer, ImageTaskSerializer, TaskSerializer


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

    def perform_destroy(self, instance):
        materials = Material.objects.filter(lesson=instance)
        for material in materials:
            ImageMixin.remove(material.file)
        instance.delete()


class MaterialAPIView(generics.CreateAPIView):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = (LessonPermission, )

    def perform_create(self, serializer):
        pk = self.kwargs['pk']
        if lesson := Lesson.objects.get(pk=pk):
            Material.objects.create(**serializer.validated_data, lesson=lesson)


class MaterialDetailAPIView(MaterialAPIView, generics.RetrieveUpdateDestroyAPIView):
    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.file:
            ImageMixin.remove(instance.file)
        serializer.save()

    def perform_destroy(self, instance):
        if instance.file:
            ImageMixin.remove(instance.file)
        instance.delete()


class QuestionsListAPIView(generics.ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = (LessonPermission, )

    def get_queryset(self):
        if self.request.method == 'GET':
            lesson = self.kwargs['pk']
            return Question.objects.filter(lesson_id=lesson)
        return super().get_queryset()


class QuestionAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = (LessonPermission, )
    lookup_url_kwarg = 'test_pk'


class OptionAPIView(generics.DestroyAPIView):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer
    permission_classes = (LessonPermission, )
    lookup_url_kwarg = 'option_pk'


class TestResultAPIView(APIView):
    permission_classes = (IsLessonLearnerAll, )

    @staticmethod
    def check_test(user, pk):
        questions_list = Question.objects.filter(lesson_id=pk)
        right_answers = 0
        for question in questions_list:
            options = Option.objects.values_list('id').filter(question=question, correct=True)
            if len(options) > 0 and len(options) == Answer.objects.filter(user_id=user, answer__in=options).count():
                right_answers += 1
        result = int(right_answers / len(questions_list) * 100)
        Result.objects.create(lesson_id=pk, user_id=user, result=result)
        return result

    def post(self, request, pk, *args, **kwargs):
        user = request.user.pk
        if Result.objects.filter(lesson_id=pk, user_id=user).exists():
            return Response({"error": "You can take the test only once."}, status=status.HTTP_403_FORBIDDEN)
        for answer in request.data:
            Answer.objects.get_or_create(user_id=user, answer_id=request.data[answer])
        result = self.check_test(user, pk)
        return Response({"result": result}, status=status.HTTP_201_CREATED)


# class TasksListAPIView(generics.CreateAPIView):
#     """
#     Create new task learner
#     """
#     queryset = Task.objects.all()
#     serializer_class = TaskSerializer
#     permission_classes = (IsLessonLearnerAll, )

    # def get_queryset(self):
    #     if self.request.method == 'GET':
    #         lesson = self.kwargs['pk']
    #         return Question.objects.filter(lesson_id=lesson)
    #     return super().get_queryset()


class TaskAPIView(generics.CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsLessonLearnerAll, )


class ImageTaskAPIView(generics.DestroyAPIView):
    queryset = ImageTask.objects.all()
    serializer_class = ImageTaskSerializer
    permission_classes = (IsLessonLearnerAll, )
    lookup_url_kwarg = 'image_pk'
