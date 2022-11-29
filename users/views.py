from rest_framework_simplejwt.views import TokenObtainPairView

from users.serializers import TokenEmailObtainPairSerializer


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenEmailObtainPairSerializer
