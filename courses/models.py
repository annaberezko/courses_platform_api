from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models
from imagekit.processors import Thumbnail, TrimBorderColor, Adjust
from imagekit.models import ProcessedImageField

from courses_platform_api.settings import VALID_EXTENSIONS

User = get_user_model()


class Course(models.Model):
    def file_path(self, filename):
        return "%s/courses/%s/%s" % (self.user, self.id, filename)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
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


class Permission(models.Model):
    """
    Permission for Administrator:
    When access=False, Administrator has limitation:
    can create only one course
    can't create curator (his previous curator get is_active=False)
    can create only 5 learner

    Permission for Curator and Student:
    if date_end is Null, permission unlimited
    giving accesses to different courses by course id
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_start = models.DateField(auto_now_add=True)
    date_end = models.DateField(null=True, blank=True)
    access = models.BooleanField('is active', default=False)

    def inactivate_user(self):
        self.access = False
        self.save(update_fields=['access'])

    def activate_user(self):
        self.access = True
        self.save(update_fields=['access'])
