import time

from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models

from courses.models import Course
from courses_platform_api.settings import FILES_EXTENSIONS
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
