import os
from celery import Celery
from datetime import timedelta
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task_schedular_app.settings')

app = Celery('task_schedular_app')
app.conf.enable_utc=False
app.conf.update(timezone='Asia/Kolkata')
# Load task modules from all registered Django apps.
app.config_from_object(settings, namespace='CELERY')

# Define a periodic task in Celery beat
app.conf.beat_schedule = {
    # 'update_something': {
    #     'task': 'jobs.tasks.update_something',
    #     'schedule': timedelta(minutes=5),
    #
    # },
    'send-email': {
        'task': 'task.tasks.check_and_execute_jobs',
        'schedule': timedelta(minutes=1),
    },
}

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')