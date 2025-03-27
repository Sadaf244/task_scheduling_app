from django.contrib.auth.models import AbstractUser
from django.db import models
import re
import logging


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=20, unique=True, null=True, blank=True)

    def email_user(self, *args, **kwargs):
        return self.email

    def __str__(self):
        return self.email


class UserSignupValidation:

    def validate_signup_data(self, email, username=None):
        errors = {}
        if not email or not email.strip():
            errors = 'Email address is required'
        else:
            # Check email format if email exists
            email_regex = re.compile(
                r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            )
            if not email_regex.match(email):
                errors = 'Please provide a valid email address (e.g., username@gmail.com)'
            elif CustomUser.objects.filter(email=email).exists():
                errors = 'Email address is already in use'
        if errors:
            return {'resp_dict': {'status': False, 'message': errors}}
        return {'resp_dict': {'status': True, 'message': 'Validation successful'}}


class UserAccountManager:
    def __init__(self, request):
        self.request = request

    def user_register(self):
        email = self.request.data.get('email')
        password = self.request.data.get('password')
        username = self.request.data.get('username', '')

        validator = UserSignupValidation()
        validation_result = validator.validate_signup_data(email, username)
        resp_dict = validation_result['resp_dict']
        if not resp_dict['status']:
            return resp_dict

        try:
            # Generate username from email if not provided
            if not username:
                username = email.split('@')[0]

            # Ensure username is unique
            counter = 1
            original_username = username
            while CustomUser.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1

            CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            resp_dict.update({
                'status': True,
                'message': 'User account created successfully'
            })
        except Exception as e:
            logging.error('Error in user_register', repr(e))
            resp_dict.update({
                'status': False,
                'message': 'Error creating user account'
            })
        return resp_dict