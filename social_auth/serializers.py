import os

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from courses_platform_api.choices_types import AuthProvider
from social_auth import google
from social_auth.register import register_social_user


# class FacebookSocialAuthSerializer(serializers.Serializer):
#     """Handles serialization of facebook related data"""
#     auth_token = serializers.CharField()
#
#     def validate_auth_token(self, auth_token):
#         user_data = facebook.Facebook.validate(auth_token)
#
#         try:
#             user_id = user_data['id']
#             email = user_data['email']
#             name = user_data['name']
#             provider = 'facebook'
#             return register_social_user(
#                 provider=provider,
#                 user_id=user_id,
#                 email=email,
#                 name=name
#             )
#         except Exception as identifier:
#
#             raise serializers.ValidationError(
#                 'The token  is invalid or expired. Please login again.'
#             )


class GoogleSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        user_data = google.Google.validate(auth_token)
        try:
            user_data['sub']
        except:
            raise serializers.ValidationError('The token is invalid or expired. Please login again.')

        if user_data['aud'] != os.environ.get('GOOGLE_CLIENT_ID'):
            raise AuthenticationFailed(code=403, detail='Bad google token.')

        user_id = user_data['sub']
        email = user_data['email']
        name = user_data['name']
        provider = AuthProvider.GOOGLE
        return register_social_user(provider=provider, user_id=user_id, email=email, name=name)
