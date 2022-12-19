from rest_framework import serializers

from lessons.models import Lesson, Material


class LessonsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ('id', 'name', 'description')


class LessonSerializer(LessonsListSerializer):
    materials_list = serializers.CharField(read_only=True)

    class Meta(LessonsListSerializer.Meta):
        fields = ('free_access', 'name', 'video', 'text', 'home_task', 'materials_list')


class MaterialSerializer(serializers.ModelSerializer):

    class Meta:
        model = Material
        fields = ('file', )
