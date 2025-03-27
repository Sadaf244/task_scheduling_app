from django.urls import path
from . import views


urlpatterns = [
    path('create-account/', views.CreateAccount.as_view()),
    path('auth/google/', views.GoogleLogin.as_view(), name='google_login'),
    path('login/', views.Login.as_view()),
    ]