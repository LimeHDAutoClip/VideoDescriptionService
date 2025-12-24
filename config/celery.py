import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# 🔥 ВАЖНО — именно так
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

print(">>> CELERY.PY LOADED <<<")
print("BROKER FROM DJANGO:", app.conf.broker_url)
print("RESULT BACKEND:", app.conf.result_backend)
