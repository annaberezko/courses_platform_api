from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models
from imagekit.processors import Thumbnail, TrimBorderColor, Adjust
from imagekit.models import ProcessedImageField

from courses_platform_api.settings import VALID_EXTENSIONS

User = get_user_model()


class Course(models.Model):
    def file_path(self, filename):
        return "%s/courses/%s/%s" % (self.admin, self.id, filename)

    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField('course name', max_length=40)
    cover = ProcessedImageField(
        validators=[FileExtensionValidator(VALID_EXTENSIONS)],
        upload_to=file_path,
        processors=[
            Thumbnail(width=800, height=800, crop=False, upscale=True),
            TrimBorderColor(),
            Adjust(contrast=1.1, sharpness=2.0),
        ],
        format='JPEG',
        options={'quality': 95},
        null=True,
        blank=True
    )
    description = models.TextField('description', null=True, blank=True)
    sequence = models.BooleanField('sequence tasks', default=False)
    access = models.BooleanField('is active', default=True)


class Permission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    date_start = models.DateField(auto_now_add=True)
    date_end = models.DateField(null=True, blank=True)
    access = models.BooleanField('is active', default=False)

    def inactivate_user(self):
        self.access = False
        self.save(update_fields=['access'])

    def activate_user(self):
        self.access = True
        self.save(update_fields=['access'])
