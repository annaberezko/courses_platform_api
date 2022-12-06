from django.contrib.auth import get_user_model
from django.db.models import Value
from django.db.models.functions import Concat
from rest_framework import generics, status
from rest_framework.response import Response

from courses.models import Course, Permission
from courses.serializers import CoursesListSerializer, CourseSerializer
from courses_platform_api.permissions import IsSuperuserOrAdministratorAllOrCuratorReadOnly, \
    IsSuperuserOrAdministratorWithCourseAccessAllOrCuratorWithCourseAccessReadOnly
from users.choices_types import ProfileRoles
from users.models import Lead

User = get_user_model()


class CoursesListAPIView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    permission_classes = (IsSuperuserOrAdministratorAllOrCuratorReadOnly, )
    serializer_class = CourseSerializer

    def get_queryset(self):
        if self.request.method == 'GET':
            role = self.request.user.role
            pk = self.request.user.pk
            queryset = Course.objects.values('id', 'name', 'cover', 'description', 'sequence').\
                annotate(admin=Concat('admin__first_name', Value(' '), 'admin__last_name')).distinct()
            if role == ProfileRoles.CURATOR:
                admin_list = Lead.objects.values_list('lead_id').filter(user_id=pk)
                return queryset.filter(admin_id__in=admin_list, access=True)
            return queryset.filter(admin_id=pk) if role == ProfileRoles.ADMINISTRATOR else queryset
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
        if self.request.user.role == ProfileRoles.ADMINISTRATOR and not self.permission_for_creation():
            return Response({'error': 'You can create only one course'}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CourseAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    permission_classes = (IsSuperuserOrAdministratorWithCourseAccessAllOrCuratorWithCourseAccessReadOnly, )
    serializer_class = CourseSerializer
    lookup_field = 'slug'
