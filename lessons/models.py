from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models

from courses.models import Course
from courses_platform_api.settings import FILES_EXTENSIONS
from users.validators import validate_size

User = get_user_model()


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    free_access = models.BooleanField(default=False)
    name = models.CharField('lesson name', max_length=40)
    description = models.TextField('description', null=True, blank=True)
    video = models.CharField('video link', max_length=100, null=True, blank=True)
    text = models.TextField('text', null=True, blank=True)
    home_task = models.TextField(null=True, blank=True)
    tests_task = models.BooleanField(default=False)


class Material(models.Model):
    def file_path(self, filename):
        return "media/%s/courses/%s/%s" % (self.lesson.course.admin.slug, self.lesson.course.slug, filename)

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='materials')
    file = models.FileField(upload_to=file_path, validators=[FileExtensionValidator(FILES_EXTENSIONS), validate_size])


class Test(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    question = models.CharField('lesson name', max_length=120)


class Option(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    option = models.CharField('test option', max_length=100)
    correct = models.BooleanField(default=False)
