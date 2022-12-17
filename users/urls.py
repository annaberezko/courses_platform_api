from django.urls import path

from users.views import ResetPasswordRequestEmailAPIView, ResetPasswordSecurityCodeAPIView, RecoveryPasswordAPIView, \
    UserSignUpAPIView, UsersListAPIView, RolesListAPIView, UserAPIView, AdministratorsListAPIView, \
    AdministratorSwitchStatusAPIView

app_name = 'users'

urlpatterns = [
    path('', UsersListAPIView.as_view(), name='user-list'),
    path('roles/', RolesListAPIView.as_view(), name='role-list'),
    path('administrators/', AdministratorsListAPIView.as_view(), name='administrator-list'),
    path('sign-up/', UserSignUpAPIView.as_view(), name='sign-up'),
    path('forgot-password/', ResetPasswordRequestEmailAPIView.as_view(), name='forgot-password'),
    path('security-code/', ResetPasswordSecurityCodeAPIView.as_view(), name='security-code'),
    path('new-security-code/', ResetPasswordRequestEmailAPIView.as_view(), name='new-security-code'),
    path('recovery-password/', RecoveryPasswordAPIView.as_view(), name='recovery-password'),
    path('<slug:slug>/', UserAPIView.as_view(), name='user-detail'),
    path('<slug:slug>/switch-status/', AdministratorSwitchStatusAPIView.as_view(), name='administrator-switch-status'),
]
