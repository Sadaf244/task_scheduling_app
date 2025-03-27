from django.http import JsonResponse
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from .models import *
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken


class CreateAccount(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        resp_dict = dict()
        resp_dict['status'] = False
        resp_dict['message'] = "Something went wrong. Please try again after sometime"
        try:
            create_user_manager = UserAccountManager(request)
            save_user_resp = create_user_manager.user_register()
            resp_dict['status'] = save_user_resp['status']
            resp_dict['message'] = save_user_resp['message']
        except Exception as e:
            logging.error('Error in creating account', repr(e))
        return JsonResponse(resp_dict, status=200)


class Login(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(email=email, password=password)
        if user is None:
            raise AuthenticationFailed('Invalid credentials')

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username
            }
        }, status=status.HTTP_200_OK)
