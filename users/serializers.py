from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
User = get_user_model()


class TokenEmailObtainPairSerializer(TokenObtainPairSerializer):
        username_field = User.USERNAME_FIELD

        default_error_messages = {
                "no_active_account": "Email or Password is not valid. Please, check provided information."
        }
