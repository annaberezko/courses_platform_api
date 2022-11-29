from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models

from users.choices_types import ProfileRoles
from users.managers import UserManager


class User(AbstractBaseUser):
    """
    When is_active=False, Administrator has limitation:
    can create only one course
    can't create curator
    can create only 5 learner
    """
    role = models.IntegerField('role', choices=ProfileRoles.CHOICES, default=3)
    first_name = models.CharField('first name', max_length=50, null=True, blank=True)
    last_name = models.CharField('last name', max_length=50, null=True, blank=True)
    email = models.EmailField('email address', unique=True)
    password = models.CharField('password', max_length=120, null=True, blank=True)
    phone = models.CharField('phone number', max_length=20, null=True, blank=True)
    google = models.CharField('google account', max_length=40, null=True, blank=True)
    facebook = models.CharField('facebook account', max_length=40, null=True, blank=True)
    last_login = models.DateTimeField('last login date', auto_now_add=True)
    date_joined = models.DateTimeField('join date', auto_now_add=True)
    is_active = models.BooleanField('is active', default=False)
    security_code = models.CharField('security code', max_length=6, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)
