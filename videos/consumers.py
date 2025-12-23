import asyncio
import json
from typing import Any

from aiokafka import AIOKafkaConsumer
from django.conf import settings
from django.utils import timezone

from config.logger import logger
from videos.models import VideoRecord
from videos.tasks import process_video_task


async def handle_message(data: dict[str, Any], message_id: int) -> None:
    video_url = data.get("video_url")
    transcription = data.get("transcription")

    if not video_url or transcription is None:
        logger.warning("[%s] Message missing fields, skipping: %s", message_id, data)
        return

    record = VideoRecord.objects.create(
        video_url=video_url,
        transcription=transcription,
        status=VideoRecord.Status.RECEIVED,
        created_at=timezone.now(),
        updated_at=timezone.now(),
    )
    logger.info("[%s] Created VideoRecord id=%s url=%s", message_id, record.id, video_url)

    process_video_task.delay(record.id)
    logger.info("[%s] Dispatched Celery task for record id=%s", message_id, record.id)


async def start_kafka_consumer() -> None:
    consumer = AIOKafkaConsumer(
        settings.KAFKA_TOPIC_VIDEOS,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id=settings.KAFKA_GROUP_ID,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    )

    await consumer.start()
    logger.info("Kafka consumer started...")

    try:
        async for message in consumer:
            try:
                await handle_message(message.value, message.offset)
                await consumer.commit()
            except Exception as exc:  # pragma: no cover - defensive
                logger.exception("[%s] Error processing Kafka message: %s", message.offset, exc)
    finally:
        await consumer.stop()
        logger.info("Kafka consumer closed.")


def main() -> None:
    asyncio.run(start_kafka_consumer())


if __name__ == "__main__":
    main()
