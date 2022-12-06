from django.contrib.auth import get_user_model
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Value, Q, QuerySet
from django.db.models.functions import Concat
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from courses_platform_api.permissions import IsSuperuserOrAdministratorAllOrCuratorReadOnly, \
    IsSuperuserOrAdministrator, IsSuperuser
from users.choices_types import ProfileRoles
from users.models import InvitationToken, Lead
from users.serializers import TokenEmailObtainPairSerializer, RequestEmailSerializer, SecurityCodeSerializer, \
    UserSignUpSerializer, UsersListSerializer, RecoveryPasswordSerializer, UsersListForCuratorSerializer, \
    CreateUserSerializer, UserSerializer

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
    permission_classes = (IsSuperuserOrAdministratorAllOrCuratorReadOnly, )

    filter_backends = [OrderingFilter]
    ordering_fields = ['role', 'courses', 'full_name']
    ordering = ['role', 'courses', 'full_name']

    def get_queryset(self):
        if self.request.method == 'GET':
            role = self.request.user.role
            pk = self.request.user.id
            default_values = ['id', 'role', 'email', 'phone', 'instagram', 'facebook', 'last_login', 'date_joined']
            annotation = {
                "full_name": Concat('first_name', Value(' '), 'last_name'),
                "courses": ArrayAgg('permission__course__name', distinct=True)
            }

            if role == ProfileRoles.ADMINISTRATOR:
                queryset = User.objects.filter(Q(users__lead_id=pk) | Q(permission__course__admin_id=pk)).\
                               values(*default_values).annotate(**annotation)
                return queryset.filter(role=ProfileRoles.LEARNER) \
                    if role == ProfileRoles.ADMINISTRATOR and not self.request.auth['profile_access'] else queryset

            elif role == ProfileRoles.CURATOR:
                admin_list = Lead.objects.values_list('lead_id').filter(user_id=pk, lead__permission__access=True)
                return User.objects.filter(permission__access=True, permission__course__admin_id__in=admin_list).\
                    values('id', 'role', 'last_login', 'date_joined').annotate(**annotation)

            return User.objects.exclude(role=ProfileRoles.SUPERUSER).values(*default_values).annotate(**annotation)
        return super().get_queryset()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            if self.request.user.role == ProfileRoles.CURATOR:
                return UsersListForCuratorSerializer
            return UsersListSerializer
        return CreateUserSerializer

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        if self.request.user.role == ProfileRoles.ADMINISTRATOR and not self.request.auth['profile_access']:
            return queryset[:5]
        return queryset

    def perform_create(self, serializer):
        user = User.objects.create_user(**serializer.validated_data)
        user.set_lead(self.request.user)
        if serializer.validated_data['role'] in (ProfileRoles.ADMINISTRATOR, ProfileRoles.CURATOR):
            user.send_invitation_link()


class UserAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    permission_classes = (IsSuperuserOrAdministratorAllOrCuratorReadOnly, )
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.request.user.role == ProfileRoles.CURATOR:
            return UsersListForCuratorSerializer
        return UserSerializer

    def get_queryset(self):
        if self.request.user.role == ProfileRoles.CURATOR:
            slug = self.kwargs['slug']
            return User.objects.filter(slug=slug).annotate(full_name=Concat('first_name', Value(' '), 'last_name'))
        return super().get_queryset()


class RolesListAPIView(APIView):
    permission_classes = (IsSuperuserOrAdministrator, )

    def get(self, request, *args, **kwargs):
        role = request.user.role
        roles_list = [{'id': role_key, 'name': role_name} for role_key, role_name in ProfileRoles.CHOICES
                      if role_key > role]
        return Response({'roles_list': roles_list}, status=status.HTTP_200_OK)


class AdministratorsListAPIView(APIView):
    permission_classes = (IsSuperuser, )

    def get(self, request, *args, **kwargs):
        administrators = User.objects.values('id').annotate(full_name=Concat('first_name', Value(' '), 'last_name')).\
            filter(role=ProfileRoles.ADMINISTRATOR)
        return Response({'data': list(administrators)}, status=status.HTTP_200_OK)
