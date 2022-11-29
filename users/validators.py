import re
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: "
            "'+999999999'. Up to 15 digits allowed.",
)


def validate_size(fieldfile_obj):
    filesize = fieldfile_obj.size
    megabyte_limit = 5.0
    if filesize > megabyte_limit * 1024 * 1024:
        raise ValidationError("Max file size is %sMB" % str(megabyte_limit))


class MaximumLengthValidator:
    def __init__(self, max_length=128):
        self.max_length = max_length

    def validate(self, password, user=None):
        if len(password) > self.max_length:
            raise ValidationError(
                f"This password must contain at most {self.max_length} characters.",
                code='password_too_long',)


class NumberValidator:
    def validate(self, password, user=None):
        if not re.findall('\d', password):
            raise ValidationError(
                "The password must contain at least 1 digit, 0-9.",
                code='password_no_number',)


class UppercaseValidator:
    def validate(self, password, user=None):
        if not re.findall('[A-Z]', password):
            raise ValidationError(
                "The password must contain at least 1 uppercase letter, A-Z.",
                code='password_no_upper',)


class LowercaseValidator:
    def validate(self, password, user=None):
        if not re.findall('[a-z]', password):
            raise ValidationError(
                "The password must contain at least 1 lowercase letter, a-z.",
                code='password_no_lower',)


class SymbolValidator:
    def validate(self, password, user=None):
        if not re.findall('[()[\]{}|\\`~!@#$%^&*_\-+=;:\'",<>./?]', password):
            raise ValidationError(
                "The password must contain at least 1 special character: " +
                "()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?",
                code='password_no_symbol',)
