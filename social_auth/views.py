from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from social_auth.serializers import GoogleSocialAuthSerializer

User = get_user_model()


def google_login(request):
    return render(request, 'google2.html')


class GoogleSocialAuthView(generics.GenericAPIView):
    serializer_class = GoogleSocialAuthSerializer
    permission_classes = (AllowAny, )

    def post(self, request):
        """
        POST with 'auth_token'
        Send an id token as fromm google to get user information
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_eception=True)
        data = (serializer.validated_data['auth_token'])
        return Response(data, status=status.HTTP_200_OK)
