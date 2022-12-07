from django.contrib.auth import get_user_model

from rest_framework.permissions import IsAuthenticated, SAFE_METHODS

from users.choices_types import ProfileRoles
User = get_user_model()


class IsSuperuser(IsAuthenticated):
    def has_permission(self, request, view):
        perm = super().has_permission(request, view)
        return bool(perm and request.user.role == ProfileRoles.SUPERUSER)


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


class IsSuperuserOrAdministratorAllOrCuratorReadOnly(IsAuthenticated):
    def has_permission(self, request, view):
        perm = super().has_permission(request, view)
        return bool(perm and (request.user.role in (ProfileRoles.SUPERUSER, ProfileRoles.ADMINISTRATOR) or
                              (request.method in SAFE_METHODS and request.user.role == ProfileRoles.CURATOR))
                    )


class IsSuperuserAllOrAdministratorActiveCoursesAllOrCuratorActiveCoursesReadOnly(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        perm = super().has_permission(request, view)
        return bool(perm and (
                request.user.role == ProfileRoles.SUPERUSER or
                (request.user.role == ProfileRoles.ADMINISTRATOR and (
                        request.method in SAFE_METHODS or
                        (obj.is_active and obj.admin == request.user))) or
                (request.user.role == ProfileRoles.CURATOR and request.method in SAFE_METHODS and obj.is_active)
        ))
