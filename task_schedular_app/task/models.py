from django.db import models
from accounts.models import CustomUser
import logging
from django.utils import timezone
from datetime import timedelta

class Task(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('OVERDUE', 'Overdue'),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    deadline = models.DateTimeField(null=True, blank=True)
    days_until_deadline = models.PositiveIntegerField(null=True, blank=True, default=0)
    reminder_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['deadline']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.title} (Due: {self.deadline})"

    def save(self, *args, **kwargs):
        # Update completed_at when status changes to COMPLETED
        if self.days_until_deadline and not self.deadline:
            self.deadline = timezone.now() + timedelta(days=self.days_until_deadline)
        if self.deadline and timezone.now() > self.deadline and self.status != 'COMPLETED':
            self.status = 'OVERDUE'
        if self.status == 'COMPLETED' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != 'COMPLETED' and self.completed_at:
            self.completed_at = None
        super().save(*args, **kwargs)


    @staticmethod
    def create_task(user, title, description=None, days_until_deadline=None):
        deadline = timezone.now() + timedelta(days=days_until_deadline) if days_until_deadline else None
        obj = Task.objects.create(user=user, title=title, description=description,
                                  days_until_deadline=days_until_deadline,
                                  deadline=deadline)
        return obj

    @staticmethod
    def get_task_object_on_id(user, task_id):
        task_object = None
        if task_id:
            try:
                task_object = Task.objects.filter(user=user, id=task_id).first()
                print(task_object)
            except Exception as e:
                logging.error('getting exception on get_task_object_on_id', repr(e))
        return task_object

    @staticmethod
    def get_task_on_user(user):
        task = None
        if user:
            try:
                task = Task.objects.filter(user=user).values(
                    'id', 'title', 'description', 'status',
                'created_at', 'updated_at', 'completed_at', 'deadline'
                ).order_by('-created_at')
            except Exception as e:
                logging.error('getting exception on get_task_on_user', repr(e))
        return task



class CreateTaskManager:
    def __init__(self, user, requested_data):
        self.user = user
        self.requested_data = requested_data

    def save_user_task(self):
        resp_dict = dict(status=False, message="Something went wrong")
        try:
            title = self.requested_data.data.get('title', None)
            description = self.requested_data.data.get('description', None)
            days_until_deadline = self.requested_data.data.get('days_until_deadline', None)
            if title is not None:
                Task.create_task(self.user, title, description, days_until_deadline)
                resp_dict['status'] = True
                resp_dict['message'] = "Task Created and Scheduled Successfully"
        except Exception as e:
            logging.error('getting exception on save_user_task', repr(e))
        return resp_dict


class GetTaskManager:

    def __init__(self, user, task_id):
        self.user = user
        self.task_id = task_id
        self.task_obj = Task.get_task_object_on_id(self.user, self.task_id)
        print(self.task_obj)
        self.task_dict = self.task_obj.__dict__ if self.task_obj else dict()

    def get_user_task(self):
        resp_dict = dict(status=False, message="Something went wrong", data=dict())
        try:

            if self.task_obj is not None:
                task_detail = {
                    "task_title": self.task_dict['title'],
                    "description": self.task_dict['description'],
                    "status": self.task_dict['status'],
                    "deadline": self.task_dict['deadline'],
                    "completed_at": self.task_dict['completed_at'],

                }
                resp_dict['data'] = task_detail
                resp_dict['status'] = True
                resp_dict['message'] = "Got Task Successfully"
        except Exception as e:
            logging.error('getting exception on get_user_task', repr(e))
        return resp_dict


class GetAllTaskManager:
    def __init__(self, user):
        self.user = user
        self.task = Task.get_task_on_user(self.user)

    def get_user_task_list(self):
        resp_dict = dict(status=False, message="Something went wrong", data=dict())
        try:
            if self.task:

                data_list = []
                for task in self.task:
                    task_data = {
                    "task_title": task['title'],
                    "description": task['description'],
                    "status": task['status'],
                    "deadline": task['deadline'],
                    "completed_at": task['completed_at'],
                    }
                    data_list.append(task_data)

                resp_dict['data'] = data_list
                resp_dict['status'] = True
                resp_dict['message'] = "Got Job Successfully"
        except Exception as e:
            logging.error('getting exception on get_user_task_list', repr(e))
        return resp_dict


class DeleteTaskManager:

    def __init__(self, user, task_id):
        self.user = user
        self.task_id = task_id

    def delete_user_task(self):
        resp_dict = dict(status=False, message="Something went wrong", data=dict())
        try:
            if not self.task_id:
                resp_dict['message'] = "Task ID is required"
                return resp_dict
            task = Task.get_task_object_on_id(self.user, self.task_id)

            if not task:
                resp_dict['message'] = "Task not found or you don't have permission"
                return resp_dict
            task.delete()
            resp_dict['status'] = True
            resp_dict['message'] = "Task Deleted Successfully"

        except Exception as e:
            logging.error('getting exception on delete_user_task', repr(e))
        return resp_dict


class UpdateTaskManager:

    def __init__(self, user, task_id, requested_data):
        self.user = user
        self.task_id = task_id
        self.requested_data = requested_data

    def update_user_task(self):
        updated = Task.objects.filter(
            user=self.user,
            id=self.task_id
        ).update(
            **{
                k: v for k, v in {
                    'title': self.requested_data.data.get('title'),
                    'description': self.requested_data.data.get('description'),
                }.items()
                if v is not None
            }
        )

        if not updated:
            return {'status': False, 'message': 'Task not found or no changes'}

        return {'status': True, 'message': 'Task updated'}
