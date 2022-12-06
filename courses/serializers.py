from rest_framework import serializers

from courses.models import Course


class CourseSerializer(serializers.ModelSerializer):
    slug = serializers.CharField(read_only=True)

    class Meta:
        model = Course
        fields = '__all__'


class CoursesListSerializer(CourseSerializer):
    admin = serializers.CharField()
