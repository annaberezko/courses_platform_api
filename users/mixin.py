from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import OuterRef, F, Value
from django.db.models.functions import JSONObject, Concat
from rest_framework import generics

from courses.models import Permission
from users.choices_types import ProfileRoles


class UserMixin:
    @staticmethod
    def annotation():
        courses_list = Permission.objects.filter(user_id=OuterRef("pk"), course__isnull=False). \
                annotate(data=JSONObject(access=F('access'), name=F('course__name'), slug=F('course__slug'))).\
                values_list("data").order_by('course__name', '-access')

        annotation = {
            "full_name": Concat('first_name', Value(' '), 'last_name'),
            "courses_list": ArraySubquery(courses_list)
        }
        return annotation


class UsersListAdministratorLimitPermissionAPIView(generics.ListAPIView):
    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        if self.request.user.role == ProfileRoles.ADMINISTRATOR and not self.request.auth['profile_access']:
            return queryset[:5]
        return queryset
