import random
from string import digits

from django.contrib.auth.base_user import AbstractBaseUser
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework.authtoken.models import Token

from courses_platform_api.mixins import GeneratorMixin
from courses_platform_api.settings import EMAIL_HOST_USER, FRONT_END_NEW_PASSWORD_URL
from courses_platform_api.choices_types import ProfileRoles, AuthProvider
from users.managers import UserManager


class User(AbstractBaseUser):
    auth_provider = models.IntegerField('provider', choices=AuthProvider.CHOICES, default=AuthProvider.EMAIL)
    slug = models.SlugField('slug', max_length=20, unique=True)
    role = models.IntegerField('role', choices=ProfileRoles.CHOICES, default=ProfileRoles.LEARNER)
    first_name = models.CharField('first name', max_length=50, null=True, blank=True)
    last_name = models.CharField('last name', max_length=50, null=True, blank=True)
    email = models.EmailField('email address', unique=True)
    password = models.CharField('password', max_length=120, null=True, blank=True)
    phone = models.CharField('phone number', max_length=20, null=True, blank=True)
    instagram = models.CharField('google account', max_length=40, null=True, blank=True)
    facebook = models.CharField('facebook account', max_length=40, null=True, blank=True)
    last_login = models.DateTimeField('last login date', auto_now_add=True)
    date_joined = models.DateTimeField('join date', auto_now_add=True)
    security_code = models.CharField('security code', max_length=6, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def generate_security_code(self, length=6):
        return ''.join(random.sample(digits, length))

    def set_lead(self, lead):
        Lead.objects.create(user=self, lead=lead)

    def send_security_code(self):
        self.security_code = self.generate_security_code()
        self.save()

        context = {
            'first_name': self.first_name,
            'second_name': self.last_name,
            'security_code': self.security_code
        }
        subject = 'Courses platform security code'
        html = render_to_string('email_security_code.html', context=context)
        message = strip_tags(html)
        send_mail(subject, message, EMAIL_HOST_USER, [self.email], html_message=html)

    def send_invitation_link(self):
        token = InvitationToken.objects.create(user_id=self.id)

        context = {
            'first_name': self.first_name,
            'second_name': self.last_name,
            'link_url': FRONT_END_NEW_PASSWORD_URL + '?token=' + str(token)
        }

        subject = 'Invitation to Courses Platform password creation'
        html = render_to_string('invitation_to_courses_platform.html', context=context)
        message = strip_tags(html)

        send_mail(subject, message, EMAIL_HOST_USER, [self.email], html_message=html)

    def __str__(self):
        return self.get_full_name()

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = GeneratorMixin.slug(self.id)
        super().save(*args, **kwargs)


class InvitationToken(Token):
    type = models.CharField(max_length=20, default="invitation")


class Lead(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='users')
    lead = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leads')
