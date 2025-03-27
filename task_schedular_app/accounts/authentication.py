from rest_framework.exceptions import AuthenticationFailed
import jwt
from django.conf import settings
from accounts.models import CustomUser
from rest_framework_simplejwt.authentication import JWTAuthentication as BaseJWTAuthentication


class JWTAuthentication(BaseJWTAuthentication):
    def authenticate(self, request):
        token = request.headers.get('Authorization')
        if not token:
            return None

        try:
            token = token.split(' ')[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']
            user = CustomUser.objects.get(id=user_id)
            return user, token
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
        except CustomUser.DoesNotExist:
            raise AuthenticationFailed('User not found')
