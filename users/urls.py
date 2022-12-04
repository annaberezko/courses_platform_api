from django.urls import path

from users.views import ResetPasswordRequestEmailAPIView, ResetPasswordSecurityCodeAPIView, RecoveryPasswordAPIView, \
    UserSignUpAPIView, UsersListAPIView, RolesListAPIView, UserAPIView, AdministratorsListAPIView

app_name = 'users'

urlpatterns = [
    path('', UsersListAPIView.as_view(), name='users-list'),
    path('<int:pk>/', UserAPIView.as_view(), name='user-detail'),
    path('roles-list/', RolesListAPIView.as_view(), name='roles-list'),
    path('administrators-list/', AdministratorsListAPIView.as_view(), name='administrators-list'),
    path('sign-up/', UserSignUpAPIView.as_view(), name='sign-up'),
    path('forgot-password/', ResetPasswordRequestEmailAPIView.as_view(), name='forgot-password'),
    path('security-code/', ResetPasswordSecurityCodeAPIView.as_view(), name='security-code'),
    path('new-security-code/', ResetPasswordRequestEmailAPIView.as_view(), name='new-security-code'),
    path('recovery-password/', RecoveryPasswordAPIView.as_view(), name='recovery-password'),
]
