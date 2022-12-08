from django_filters.rest_framework import FilterSet, CharFilter


class UsersCourseFilter(FilterSet):
    course_search = CharFilter(field_name='permission__course__slug')
