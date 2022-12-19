import time

from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models

from imagekit import register
from imagekit.models import ProcessedImageField

from courses_platform_api.images import ImageThumbnail
from courses_platform_api.settings import VALID_EXTENSIONS
from lessons.models import Lesson
from courses_platform_api.choices_types import TaskStatus

User = get_user_model()


class Question(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='questions')
    question = models.CharField('lesson name', max_length=120)


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    option = models.CharField('test option', max_length=100)
    correct = models.BooleanField(default=False)


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Option, on_delete=models.CASCADE, related_name='answers')


class Result(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='results')
    result = models.SmallIntegerField('test result')
    accept = models.BooleanField(default=False)


class Task(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='tasks')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.IntegerField('status', choices=TaskStatus.CHOICES, default=1)
    test = models.CharField('text of home task from user', max_length=250, null=True, blank=True)
    curator = models.ForeignKey(User, related_name='tasks', on_delete=models.CASCADE, null=True, blank=True)
    review = models.CharField('comment from curator', max_length=250, null=True, blank=True)


class ImageTask(models.Model):
    def file_path(self, filename):
        return "media/%s/courses/%s/homeworks/%s/%s/%s_%s" % (
            self.task.lesson.course.admin.slug,
            self.task.lesson.course.slug,
            self.task.lesson.id,
            self.task.user,
            str(time.time()), filename)

    register.generator('tasks:thumbnail', ImageThumbnail)

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='images')
    image = ProcessedImageField(spec_id='tasks:thumbnail', upload_to=file_path,
                                validators=[FileExtensionValidator(VALID_EXTENSIONS)])
