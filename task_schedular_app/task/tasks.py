from celery import shared_task
from datetime import datetime, timedelta
from .models import Task
import pytz
import logging
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


@shared_task()
def check_task_deadlines():
    """Check and handle task deadlines based on days_until_deadline"""
    now = timezone.now()

    # 1. Send reminders for tasks due in 1 day (24h)
    tasks_due_soon = Task.objects.filter(
        deadline__lte=now + timedelta(days=1),
        deadline__gt=now,
        reminder_sent=False,
        status='PENDING'
    )

    for task in tasks_due_soon:
        try:
            subject = f"Reminder: '{task.title}' due in 1 day"
            message = f"Your task is due on {task.deadline.strftime('%Y-%m-%d')}"
            send_mail(subject, message, settings.EMAIL_HOST_USER, [task.user.email])
            task.reminder_sent = True
            task.save()
        except Exception as e:
            logger.error(f"Failed to send reminder for task {task.id}: {str(e)}")

    # 2. Mark overdue tasks
    Task.objects.filter(
        deadline__lt=now,
        status='PENDING'
    ).update(status='OVERDUE')