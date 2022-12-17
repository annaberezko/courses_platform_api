from django.contrib.auth import get_user_model
from django.db.models import Value
from django.db.models.functions import Concat

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.mixins import CourseMixin
from courses.models import Course, Permission
from courses.serializers import CoursesListSerializer, CourseSerializer
from courses_platform_api.mixins import ImageMixin
from courses_platform_api.permissions import IsSuperuserOrAdministratorAllOrCuratorReadOnly, \
    IsSuperuserAllOrAdministratorActiveCoursesAllOrCuratorActiveCoursesReadOnly, IsSuperuserOrAdministratorOwner
from users.choices_types import ProfileRoles

User = get_user_model()


class CoursesListAPIView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = (IsSuperuserOrAdministratorAllOrCuratorReadOnly, )

    def get_queryset(self):
        if self.request.method == 'GET':
            pk = self.request.user.pk
            role = self.request.user.role
            queryset = Course.objects.values('slug', 'name', 'cover', 'description', 'sequence', 'is_active').\
                annotate(admin=Concat('admin__first_name', Value(' '), 'admin__last_name')).distinct()
            return CourseMixin.list_by_role(role, pk, queryset)
        return super().get_queryset()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CoursesListSerializer
        return super().get_serializer_class()

    def permission_for_creation(self):
        if Permission.objects.filter(user=self.request.user, access=True).exists():
            return True
        return not Course.objects.filter(admin=self.request.user).count()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role = self.request.user.role
        if role == ProfileRoles.ADMINISTRATOR and not self.permission_for_creation():
            return Response({'error': 'You can create only one course'}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CourseAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = (IsSuperuserAllOrAdministratorActiveCoursesAllOrCuratorActiveCoursesReadOnly, )
    lookup_field = 'slug'

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.cover:
            ImageMixin.remove(instance.cover)
        serializer.save()

    def perform_destroy(self, instance):
        if instance.cover:
            ImageMixin.remove(instance.cover)
        instance.delete()


class CoursesShortListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        pk = self.request.user.pk
        role = self.request.user.role
        queryset = Course.objects.values('slug', 'name').order_by('name')
        courses_list = CourseMixin.list_by_role(role, pk, queryset)
        return Response({'courses_list': courses_list}, status=status.HTTP_200_OK)


class CoursesSwitchStatusAPIView(generics.UpdateAPIView):
    queryset = Course.objects.all()
    permission_classes = (IsSuperuserOrAdministratorOwner, )
    lookup_field = 'slug'

    def put(self, request, *args, **kwargs):
        """
        Permission for administrator:
        Status is_active = false can do in any cases
        Status is_active = true can do only for one course in list
        """
        instance = self.get_object()
        pk = self.request.user.pk
        role = self.request.user.role
        if role == ProfileRoles.ADMINISTRATOR and not self.request.auth['profile_access'] \
                and not instance.is_active and Course.objects.filter(admin=pk, is_active=True).exists():
            return Response(status=status.HTTP_403_FORBIDDEN)
        instance.switch_status()
        return Response({'is_active': instance.is_active}, status=status.HTTP_200_OK)
