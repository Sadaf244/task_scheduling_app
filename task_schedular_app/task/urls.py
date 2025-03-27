from django.urls import path
from . import views

urlpatterns = [
    path('create-task/', views.CreateTask.as_view()),
    path('get-task-by-id/<int:task_id>/', views.GetTask.as_view()),
    path('get-task-list-by-user/', views.GetAllTask.as_view()),
    path('delete-task/<int:task_id>/', views.DeleteTask.as_view()),
    path('update-task/<int:task_id>/', views.UpdateTask.as_view()),
    ]