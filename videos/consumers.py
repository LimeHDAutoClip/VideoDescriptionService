import os
import django
import json
import logging
from kafka import KafkaConsumer
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from videos.models import VideoRecord
from videos.tasks import process_video_task

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def start_kafka_consumer():
    consumer = KafkaConsumer(
        'video_links',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        enable_auto_commit=False,
        group_id='video_service_group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    )

    logger.info("Kafka consumer started...")

    try:
        for message in consumer:
            try:
                data = message.value
                video_url = data.get("video_url")
                transcription = data.get("transcription")

                if not video_url or transcription is None:
                    logger.warning("Message missing fields, skipping: %s", data)
                    consumer.commit()
                    continue

                record = VideoRecord.objects.create(
                    video_url=video_url,
                    transcription=transcription,
                    status=VideoRecord.STATUS_CHOICES.RECEIVED,
                    created_at=timezone.now(),
                    updated_at=timezone.now(),
                )
                logger.info("Created VideoRecord id=%s url=%s", record.id, video_url)

                process_video_task.delay(record.id)
                logger.info("Dispatched Celery task for record id=%s", record.id)

                consumer.commit()
            except Exception as e:
                logger.exception("Error processing kafka message: %s", e)

    finally:
        consumer.close()
        logger.info("Kafka consumer closed.")


if __name__ == "__main__":
    start_kafka_consumer()

