from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
import django.contrib.auth.password_validation as validators
from django.core import exceptions

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from courses.models import Permission, Course
from users.choices_types import ProfileRoles
from users.models import InvitationToken

User = get_user_model()


class TokenEmailObtainPairSerializer(TokenObtainPairSerializer):
        username_field = User.USERNAME_FIELD

        default_error_messages = {
                "no_active_account": "Email or Password is not valid. Please, check provided information."
        }

        @classmethod
        def get_token(cls, user):
            token = super().get_token(user)
            if user.role == ProfileRoles.ADMINISTRATOR:
                token['profile_access'] = Permission.objects.filter(user=user, access=True).exists()
            return token


class RequestEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ("email")


class SecurityCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)
    security_code = serializers.CharField(min_length=6, max_length=6)

    class Meta:
        fields = ("email", "security_code")


class RecoveryPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validators.validate_password])
    confirm_password = serializers.CharField(min_length=2, write_only=True, required=True)

    class Meta:
        fields = ('password', 'confirm_password')

    def validate(self, attr):
        if attr['password'] != attr['confirm_password']:
            raise serializers.ValidationError({'error': "Passwords do not match."})
        if token := InvitationToken.objects.filter(key=str(attr['token'])).first():
            attr['user'] = token.user
            attr['email'] = token.user.email
        else:
            raise serializers.ValidationError({'error': "Invalid token."})
        if check_password(attr['password'], token.user.password):
            raise serializers.ValidationError({'error': "Old password can not be used."})
        try:
            validators.validate_password(password=attr['password'])
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        return attr


class UserSignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validators.validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'confirm_password')

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': "Password fields didn't match."})
        return attrs


class CreateUserSerializer(serializers.ModelSerializer):
    curator_lead = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ('role', 'first_name', 'last_name', 'email', 'phone', 'instagram', 'facebook', 'curator_lead')


class UserCoursesListSerializer(serializers.ModelSerializer):
    access = serializers.BooleanField()

    class Meta:
        model = Course
        fields = ('slug', 'name', 'access')


class UsersListSerializer(serializers.ModelSerializer):
    slug = serializers.CharField(read_only=True)
    role = serializers.SerializerMethodField()
    full_name = serializers.CharField()
    courses_list = UserCoursesListSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('slug', 'role', 'full_name', 'email', 'phone', 'instagram', 'facebook', 'last_login',
                  'date_joined', 'courses_list')

    def get_role(self, obj):
        role = obj['role'] if type(obj) is dict else obj.role
        return dict(ProfileRoles.CHOICES)[role]


class UsersListForCuratorSerializer(UsersListSerializer):
    class Meta(UsersListSerializer.Meta):
        fields = ('slug', 'role', 'full_name', 'last_login', 'date_joined', 'courses_list')


class UserSerializer(serializers.ModelSerializer):
    last_login = serializers.DateTimeField(read_only=True)
    role = serializers.SerializerMethodField(read_only=True)
    email = serializers.EmailField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    courses_list = UserCoursesListSerializer(many=True, read_only=True)
    phone = serializers.CharField(min_length=9, max_length=16)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)

    class Meta:
        model = User
        exclude = ('id', 'password', 'security_code')

    def get_role(self, obj):
        role = obj['role'] if type(obj) is dict else obj.role
        return dict(ProfileRoles.CHOICES)[role]
