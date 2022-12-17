from rest_framework import serializers

from lessons.models import Lesson


class LessonsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ('id', 'name', 'description')
