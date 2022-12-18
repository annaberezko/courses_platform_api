from django.db.models import OuterRef, Subquery

from courses.models import Permission
from courses_platform_api.choices_types import ProfileRoles
from users.models import Lead


class CourseMixin:
    @staticmethod
    def list_by_role(role, user, queryset):
        if role == ProfileRoles.LEARNER:
            learner_permissions_list = Permission.objects.filter(user_id=user, course_id=OuterRef('pk'))
            courses_list = Permission.objects.values_list('course_id').filter(user_id=user)
            return queryset.filter(is_active=True, id__in=courses_list). \
                annotate(
                access=Subquery(learner_permissions_list.values('access')),
                date_end=Subquery(learner_permissions_list.values('date_end'))
            )
        if role == ProfileRoles.CURATOR:
            admin_list = Lead.objects.values_list('lead_id').filter(user_id=user)
            return queryset.filter(admin_id__in=admin_list, is_active=True)
        return queryset.filter(admin_id=user) if role == ProfileRoles.ADMINISTRATOR else queryset
