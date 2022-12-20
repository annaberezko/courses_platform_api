from django.urls import path

from .views import GoogleSocialAuthView, google_login

# , FacebookSocialAuthView, TwitterSocialAuthView

urlpatterns = [
    path('google/', google_login),
    # path('google/', GoogleSocialAuthView.as_view()),
    # path('facebook/', FacebookSocialAuthView.as_view()),
    # path('twitter/', TwitterSocialAuthView.as_view()),
]
