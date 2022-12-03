from django.db.models import Value
from django.db.models.functions import Concat
from rest_framework import generics

from courses.models import Course
from courses.serializers import CoursesListSerializer, CourseSerializer
from courses_platform_api.permissions import IsSuperuserOrAdministratorAllOrCuratorReadOnly
from users.choices_types import ProfileRoles
from users.models import Lead


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
                return queryset.filter(admin_id__in=admin_list)
            return queryset.filter(admin_id=pk) if role == ProfileRoles.ADMINISTRATOR else queryset
        return super().get_queryset()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CoursesListSerializer
        return super().get_serializer_class()

class CourseAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    permission_classes = (IsSuperuserOrAdministratorAllOrCuratorReadOnly, )
    serializer_class = CoursesListSerializer
