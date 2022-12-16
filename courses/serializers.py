from rest_framework import serializers

from courses.models import Course, Permission


class CourseSerializer(serializers.ModelSerializer):
    slug = serializers.CharField(read_only=True)

    class Meta:
        model = Course
        fields = '__all__'


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
        fields = ['user_slug', 'full_name', 'date_end', 'access']
