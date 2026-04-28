import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
app = Celery('playto')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Beat schedule — check for stuck payouts every 30 seconds
app.conf.beat_schedule = {
    'retry-stuck-payouts': {
        'task': 'apps.payouts.tasks.retry_stuck_payouts',
        'schedule': 30.0,
    },
}