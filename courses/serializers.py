from django.contrib.auth import get_user_model
from rest_framework import serializers

from courses.models import Course, Permission
User = get_user_model()


class CourseSerializer(serializers.ModelSerializer):
    slug = serializers.CharField(read_only=True)
    admin = serializers.CharField(read_only=True)
    admin_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Course
        fields = ('slug', 'admin', 'admin_id', 'name', 'cover', 'description', 'sequence', 'is_active', 'price')


class CoursesListSerializer(CourseSerializer):
    admin = serializers.CharField()


class LearnerCoursesListSerializer(CoursesListSerializer):
    access = serializers.BooleanField()
    date_end = serializers.DateField()

    class Meta(CoursesListSerializer.Meta):
        fields = ('slug', 'name', 'admin', 'cover', 'description', 'price', 'access', 'date_end')


class CourseLearnersListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    user_slug = serializers.CharField(read_only=True)

    class Meta:
        model = Permission
        fields = ('user_slug', 'full_name', 'date_end', 'access')
