from rest_framework import serializers

from lessons.models import Lesson, Material, Question, Option, Task


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ('file', )


class LessonsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ('id', 'name', 'description')


class LessonSerializer(LessonsListSerializer):
    materials_list = serializers.CharField(read_only=True)

    class Meta(LessonsListSerializer.Meta):
        fields = ('free_access', 'name', 'video', 'text', 'home_task', 'materials_list')


class OptionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Option
        fields = ('id', 'option', 'correct')


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True)

    class Meta:
        model = Question
        fields = ('question', 'options')

    def create(self, validated_data):
        lesson = self.context.get('view').kwargs.get('pk')
        options_data = validated_data.pop('options')
        question = Question.objects.create(lesson_id=lesson, **validated_data)
        for option_data in options_data:
            Option.objects.create(question=question, **option_data)
        return question

    def update(self, instance, validated_data):
        instance.question = validated_data['question']
        instance.save()
        for option_data in validated_data['options']:
            if 'correct' not in option_data:
                option_data['correct'] = False
            if 'id' not in option_data:
                option_data['id'] = None
            option_data['question'] = instance
            Option.objects.update_or_create(pk=option_data['id'], defaults=option_data)
        return instance


class ImageTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ('image', )


class TaskSerializer(serializers.ModelSerializer):
    images = ImageTaskSerializer(many=True, required=False)

    class Meta:
        model = Task
        fields = ('text', 'images')

    def create(self, validated_data):
        user = self.context['request'].user
        lesson = self.context.get('view').kwargs.get('pk')
        task = Task.objects.create(user=user, lesson_id=lesson, text=validated_data['text'])
        if 'images' in validated_data:
            for image_data in validated_data['images']:
                Option.objects.create(task=task, **image_data)
        return task
