from .base import *

DEBUG = True

ALLOWED_HOSTS = ["*"]

CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"