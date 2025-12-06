import os
import django
import json
from kafka import KafkaConsumer
from videos.download import download_video
import asyncio


# Настройка Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup() # инициализация django

from videos.models import VideoRecord #Важно импорт моделей осуществлять после инициализации django

consumer = KafkaConsumer(
    'video_links',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='video_service_group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("Kafka consumer started...")

for message in consumer:
    try:
        data = message.value
        video_url = data.get("video_url")
        transcription = data.get("transcription")
        if video_url:
            file_path = asyncio.run(download_video(video_url))

            video_record = VideoRecord.objects.create(
                video_url=video_url,
                transcription=transcription,
                video_path=file_path,
                status=VideoRecord.STATUS_CHOICES.RECEIVED
            )
            print(f"Video saved: {video_record.id} - {video_url}")
    except Exception as e:
        print(f"Error processing message: {e}")
