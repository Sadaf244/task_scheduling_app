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
import requests

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


class GoogleLogin(APIView):
    def post(self, request):
        access_token = request.data.get('access_token')
        if not access_token:
            return Response({'error': 'Access token required'}, status=status.HTTP_400_BAD_REQUEST)

        # Verify token with Google
        google_response = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            params={'access_token': access_token}
        )

        if not google_response.ok:
            return Response({'error': 'Invalid Google token'}, status=status.HTTP_401_UNAUTHORIZED)

        google_data = google_response.json()

        # Get or create user
        user, created = CustomUser.objects.get_or_create(
            email=google_data['email'],
            defaults={
                'username': google_data.get('email'),
                'first_name': google_data.get('given_name', ''),
                'last_name': google_data.get('family_name', ''),
            }
        )

        # Generate JWT tokens
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'email': user.email,
                'username': user.username,
            }
        })