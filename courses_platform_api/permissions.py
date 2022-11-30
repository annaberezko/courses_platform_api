from rest_framework.permissions import IsAuthenticated

from users.choices_types import ProfileRoles


class IsSuperuserOrAdministrator(IsAuthenticated):
    def has_permission(self, request, view):
        perm = super().has_permission(request, view)
        return bool(perm and request.user.role in (ProfileRoles.SUPERUSER, ProfileRoles.ADMINISTRATOR))
