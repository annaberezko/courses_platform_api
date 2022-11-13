from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models

from courses_platform_api.choices_types import ProfileRoles


class User(AbstractBaseUser):
    """
    When is_active=False, Administrator has limitation:
    can create only one course
    can't create curator
    can create only 5 learner
    """
    role = models.IntegerField(choices=ProfileRoles.CHOICES, default=3)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField('email address', unique=True)
    password = models.CharField(max_length=40, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    google = models.CharField(max_length=40, null=True, blank=True)
    facebook = models.CharField(max_length=40, null=True, blank=True)
    last_login = models.DateTimeField(auto_now_add=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    security_code = models.CharField(max_length=6, null=True, blank=True)

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)
