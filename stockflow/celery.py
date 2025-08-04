import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockflow.settings")

app = Celery("stockflow")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
