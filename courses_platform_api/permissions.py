from rest_framework.permissions import IsAuthenticated, SAFE_METHODS

from users.choices_types import ProfileRoles


class IsSuperuserOrAdministrator(IsAuthenticated):
    def has_permission(self, request, view):
        perm = super().has_permission(request, view)
        return bool(perm and request.user.role in (
            ProfileRoles.SUPERUSER,
            ProfileRoles.ADMINISTRATOR
        ))


class IsSuperuserOrAdministratorOrCurator(IsAuthenticated):
    def has_permission(self, request, view):
        perm = super().has_permission(request, view)
        return bool(perm and request.user.role in (
            ProfileRoles.SUPERUSER,
            ProfileRoles.ADMINISTRATOR,
            ProfileRoles.CURATOR
        ))


class IsSuperuserOrAdministratorReadWriteOrCuratorReadOnly(IsAuthenticated):
    def has_permission(self, request, view):
        perm = super().has_permission(request, view)
        return bool(perm and (request.user.role in (ProfileRoles.SUPERUSER, ProfileRoles.ADMINISTRATOR) or
                              (request.method in SAFE_METHODS and request.user.role == ProfileRoles.CURATOR))
                    )

