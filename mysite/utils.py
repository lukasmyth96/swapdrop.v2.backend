from users.serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken


def my_jwt_response_handler(token, user=None, request=None):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': UserSerializer(user, context={'request': request}).data
    }
