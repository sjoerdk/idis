import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("idis")
app.config_from_object("django.conf:settings", namespace="CELERY_")
app.autodiscover_tasks()
