from users.choices_types import ProfileRoles
from users.models import Lead


class CourseMixin:
    @staticmethod
    def list_by_role(role, admin, queryset):
        if role == ProfileRoles.CURATOR:
            admin_list = Lead.objects.values_list('lead_id').filter(user_id=admin)
            return queryset.filter(admin_id__in=admin_list, is_active=True)
        return queryset.filter(admin_id=admin) if role == ProfileRoles.ADMINISTRATOR else queryset
