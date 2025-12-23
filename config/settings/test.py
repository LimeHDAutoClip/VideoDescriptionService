from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Используем SQLite для простого локального теста
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db_test.sqlite3",  # type: ignore[name-defined]
    }
}

# Отключаем отправку в Kafka для теста без брокера
ENABLE_KAFKA_PRODUCER = False

# Заглушки для внешних ключей
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "test-key")  # noqa: F405
KAFKA_BOOTSTRAP_SERVERS = ["localhost:9092"]  # не используется при ENABLE_KAFKA_PRODUCER=False
