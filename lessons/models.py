import time
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models

from imagekit import register
from imagekit.models import ProcessedImageField

from courses.models import Course
from courses_platform_api.choices_types import TaskStatus
from courses_platform_api.images import ImageThumbnail
from courses_platform_api.settings import FILES_EXTENSIONS, VALID_EXTENSIONS
from users.validators import validate_size

User = get_user_model()


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    sort = models.SmallIntegerField(null=True, blank=True)
    free_access = models.BooleanField(default=False)
    name = models.CharField('lesson name', max_length=40)
    description = models.TextField('description', null=True, blank=True)
    video = models.CharField('video link', max_length=100, null=True, blank=True)
    text = models.TextField('text', null=True, blank=True)
    home_task = models.TextField(null=True, blank=True)
    test = models.BooleanField(default=False)


class Material(models.Model):
    def file_path(self, filename):
        return "media/%s/courses/%s/%s_%s" % (
            self.lesson.course.admin.slug,
            self.lesson.course.slug,
            str(time.time()),
            filename
        )

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='materials')
    file = models.FileField(upload_to=file_path, validators=[FileExtensionValidator(FILES_EXTENSIONS), validate_size])
    lookup_url_kwarg = 'material_pk'


class Question(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='questions')
    question = models.CharField('lesson name', max_length=120)


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    option = models.CharField('test option', max_length=100)
    correct = models.BooleanField(default=False)


class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Option, on_delete=models.CASCADE, related_name='answers')


class Result(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='results')
    date = models.DateTimeField('result date created', auto_now_add=True)
    result = models.SmallIntegerField('test result')


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='tasks')
    status = models.IntegerField('status', choices=TaskStatus.CHOICES, default=TaskStatus.NEW)
    text = models.CharField('text of home task from user', max_length=250, null=True, blank=True)
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
