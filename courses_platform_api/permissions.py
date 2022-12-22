from django.contrib.auth import get_user_model

from rest_framework.permissions import IsAuthenticated, SAFE_METHODS

from courses.models import Course, Permission
from courses_platform_api.choices_types import ProfileRoles
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


class IsSuperuserOrOwner(IsAuthenticated):
    def has_permission(self, request, view):
        perm = super().has_permission(request, view)
        slug = request.resolver_match.kwargs['slug']

        return bool(perm and (
                request.user.role == ProfileRoles.SUPERUSER or
                (request.user.role == ProfileRoles.ADMINISTRATOR and
                 Course.objects.filter(slug=slug, admin=request.user).exists())
        ))

    def has_object_permission(self, request, view, obj):
        perm = super().has_permission(request, view)
        return bool(perm and (
                request.user.role == ProfileRoles.SUPERUSER or
                (request.user.role == ProfileRoles.ADMINISTRATOR and obj.admin == request.user)
        ))


class IsSuperuserOrAdministratorAllOrCuratorReadOnly(IsAuthenticated):
    def has_permission(self, request, view):
        perm = super().has_permission(request, view)
        return bool(perm and (
                request.user.role in (ProfileRoles.SUPERUSER, ProfileRoles.ADMINISTRATOR) or
                (request.method in SAFE_METHODS and request.user.role == ProfileRoles.CURATOR)
        ))


class IsSuperuserAllOrAdministratorActiveCoursesAllOrCuratorActiveCoursesReadOnly(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        perm = super().has_permission(request, view)
        return bool(perm and (
                request.user.role == ProfileRoles.SUPERUSER or
                (request.user.role == ProfileRoles.ADMINISTRATOR and obj.admin == request.user and obj.is_active) or
                (request.user.role == ProfileRoles.CURATOR and request.method in SAFE_METHODS and obj.is_active)
        ))


class IsSuperuserAllOrOwnerAllOrCuratorActiveCoursesReadOnlyLearnerReadOnly(IsAuthenticated):
    def has_permission(self, request, view):
        """
        For list of courses we use has_permission
        For list of lessons we use has_object_permission
        """
        if 'slug' in view.kwargs:
            slug = view.kwargs['slug']
            course = Course.objects.get(slug=slug)
            return self.has_object_permission(request, view, course)

        perm = super().has_permission(request, view)
        return bool(perm and (
                request.user.role in (ProfileRoles.SUPERUSER, ProfileRoles.ADMINISTRATOR) or
                (request.method in SAFE_METHODS and request.user.role in (ProfileRoles.CURATOR, ProfileRoles.LEARNER))
        ))

    def has_object_permission(self, request, view, obj):
        perm = super().has_permission(request, view)

        return bool(perm and (
                request.user.role == ProfileRoles.SUPERUSER or
                (request.user.role == ProfileRoles.ADMINISTRATOR and obj.admin == request.user and obj.is_active) or
                (request.user.role in (ProfileRoles.LEARNER, ProfileRoles.CURATOR) and request.method in SAFE_METHODS
                 and obj.is_active)
        ))


class LearnerPermission(IsAuthenticated):
    def has_permission(self, request, view):
        perm = super().has_permission(request, view)
        return bool(perm and request.user.role == ProfileRoles.LEARNER)


class LessonPermission(IsAuthenticated):
    """
    Superuser see and edit all permissions
    Administrator owner see and edit all lessons, when course is_active = True
    Curator read only, when course is_active = True
    Learner read only, when course is_active = True and lesson free_access = True
    or learner permission to this course access = True
    """
    def has_object_permission(self, request, view, obj):
        perm = super().has_permission(request, view)
        role = request.user.role
        slug = view.kwargs['slug']
        course = Course.objects.get(slug=slug)

        if role == ProfileRoles.LEARNER:
            course_permission = Permission.objects.filter(course=course, user=request.user, access=True).exists()
            learner_access = course_permission or obj['free_access']

        return bool(perm and (
                role == ProfileRoles.SUPERUSER or
                (role == ProfileRoles.ADMINISTRATOR and course.admin == request.user and course.is_active) or
                (role == ProfileRoles.CURATOR and request.method in SAFE_METHODS and course.is_active) or
                (role == ProfileRoles.LEARNER and request.method in SAFE_METHODS and learner_access)
        ))
