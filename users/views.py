from django.contrib.auth import get_user_model
from django.db.models import Value
from django.db.models.functions import Concat
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from courses_platform_api.permissions import IsSuperuserOrAdministratorReadWriteOrCuratorReadOnly, \
    IsSuperuserOrAdministrator
from users.choices_types import ProfileRoles
from users.models import InvitationToken
from users.serializers import TokenEmailObtainPairSerializer, RequestEmailSerializer, SecurityCodeSerializer, \
    UserSignUpSerializer, UsersListSerializer, RecoveryPasswordSerializer, UsersListForCuratorSerializer, \
    CreateUserSerializer

User = get_user_model()


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenEmailObtainPairSerializer


class ResetPasswordRequestEmailAPIView(generics.GenericAPIView):
    serializer_class = RequestEmailSerializer
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        if user := User.objects.filter(email=email).first():
            user.send_security_code()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'There is no account with that email.'}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordSecurityCodeAPIView(generics.GenericAPIView):
    serializer_class = SecurityCodeSerializer
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        if user := User.objects.filter(email=serializer.validated_data['email']).first():
            if serializer.validated_data['security_code'] == user.security_code:
                token, _ = InvitationToken.objects.get_or_create(user=user)
                return Response({'token': str(token)}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Incorrect security code. Check your secure code or request for a new one.'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'There is no user with that email.'}, status=status.HTTP_400_BAD_REQUEST)


class RecoveryPasswordAPIView(generics.GenericAPIView):
    serializer_class = RecoveryPasswordSerializer
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        user.set_password(serializer.validated_data['password'])
        user.save()
        InvitationToken.objects.filter(user_id=user.id).delete()
        return Response({'email': serializer.validated_data['email']}, status=status.HTTP_200_OK)


class UserSignUpAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSignUpSerializer
    permission_classes = (AllowAny, )

    def perform_create(self, serializer):
        user_data = dict(serializer.validated_data)
        del user_data['confirm_password']
        User.objects.create_user(**user_data)


class UsersListAPIView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    permission_classes = (IsSuperuserOrAdministratorReadWriteOrCuratorReadOnly, )

    filter_backends = [OrderingFilter]
    ordering_fields = ['role', 'full_name']
    ordering = ['role', 'full_name']

    def get_queryset(self):
        if self.request.method == 'GET':
            return User.objects.filter(role__gt=self.request.user.role).\
            annotate(full_name=Concat('first_name', Value(' '), 'last_name'))
        return super().get_queryset()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            if self.request.user.role == ProfileRoles.CURATOR:
                return UsersListForCuratorSerializer
            return UsersListSerializer
        return CreateUserSerializer

    def perform_create(self, serializer):
        user = User.objects.create_user(**serializer.validated_data)
        user.set_lead(self.request.user)
        if serializer.validated_data['role'] in (ProfileRoles.ADMINISTRATOR, ProfileRoles.CURATOR):
            user.send_invitation_link()


class RolesListAPIView(APIView):
    permission_classes = (IsSuperuserOrAdministrator, )

    def get(self, request, *args, **kwargs):
        role = request.user.role
        roles_list = [{'id': role_key, 'name': role_name} for role_key, role_name in ProfileRoles.CHOICES
                      if role_key > role]
        return Response({'roles_list': roles_list}, status=status.HTTP_200_OK)
