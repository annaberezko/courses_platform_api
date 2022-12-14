from django_filters.rest_framework import FilterSet, CharFilter


class UsersFilter(FilterSet):
    course_search = CharFilter(field_name='permission__course__slug')
    role_search = CharFilter(field_name='role')
