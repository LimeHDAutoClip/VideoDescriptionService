import json
import os
import django
from kafka import KafkaConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from videos.models import VideoRecord
from videos.tasks import process_video_task
from config.logger import logger
from django.conf import settings


consumer = KafkaConsumer(
    settings.KAFKA_TOPIC_VIDEO_TRANSCRIBED,
    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="video-analysis-service",
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
)


def run_consumer():
    logger.info("Kafka consumer started")

    for message in consumer:
        data = message.value

        record = VideoRecord.objects.create(
            video_url=data["video_url"],
            transcription=data["transcription"],
            status=VideoRecord.Status.RECEIVED,
        )

        logger.info("VideoRecord created id=%s", record.id)

        # Запускаем Celery пайплайн
        process_video_task.delay(record.id)
