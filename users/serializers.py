from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
import django.contrib.auth.password_validation as validators
from django.core import exceptions

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import InvitationToken

User = get_user_model()


class TokenEmailObtainPairSerializer(TokenObtainPairSerializer):
        username_field = User.USERNAME_FIELD

        default_error_messages = {
                "no_active_account": "Email or Password is not valid. Please, check provided information."
        }


class RequestEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ["email"]


class SecurityCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)
    security_code = serializers.CharField(min_length=6, max_length=6)

    class Meta:
        fields = ["email", "security_code"]


class CreateNewPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    password = serializers.CharField(min_length=2, write_only=True, required=True)
    confirm_password = serializers.CharField(min_length=2, write_only=True, required=True)

    class Meta:
        fields = ['password', 'confirm_password']

    def validate(self, attr):
        if attr['password'] != attr['confirm_password']:
            raise serializers.ValidationError({'error': "Passwords do not match."})
        if token := InvitationToken.objects.filter(key=str(attr['token'])).first():
            attr['user'] = token.user
            attr['email'] = token.user.email
        else:
            raise serializers.ValidationError({'error': "Invalid token."})
        if check_password(attr['password'], token.user.password):
            raise serializers.ValidationError({'error': "This password can not be used."})
        try:
            validators.validate_password(password=attr['password'])
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        return attr
