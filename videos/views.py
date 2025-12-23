import asyncio
import json

from django.conf import settings
from django.http import HttpRequest
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from config.logger import logger
from videos.models import VideoRecord
from .kafka import kafka_producer
from .serializers import VideoRecordSerializer


def _apply_hook_and_description(video: VideoRecord) -> None:
    """
    Заглушка для вставки hook/description в видео.
    Реализация зависит от вашего пайплайна (ffmpeg/обработка).
    """
    logger.info("Applying hook to video id=%s (stub)", video.id)


def _send_to_external_service(video: VideoRecord) -> None:
    """
    Заглушка для отправки видео и описания в внешний сервис.
    """
    logger.info("Sending video id=%s to external service (stub)", video.id)


class VideoReceiveAPIView(APIView):
    def post(self, request: HttpRequest):
        serializer = VideoRecordSerializer(data=request.data)
        if serializer.is_valid():
            video_record = serializer.save(
                status=VideoRecord.Status.RECEIVED
            )
            logger.info(
                "VideoRecord created id=%s url=%s", video_record.id, video_record.video_url
            )

            payload = {
                "id": video_record.id,
                "video_url": video_record.video_url,
                "transcription": video_record.transcription,
                "status": video_record.status,
            }
            if settings.ENABLE_KAFKA_PRODUCER:
                asyncio.create_task(
                    kafka_producer.send_json(settings.KAFKA_TOPIC_VIDEOS, payload)
                )
            else:
                logger.info("Kafka producer disabled, skipping send for id=%s", video_record.id)

            return Response(VideoRecordSerializer(video_record).data, status=status.HTTP_201_CREATED)

        logger.warning("Failed to create VideoRecord: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VideoAnalysisListAPIView(APIView):
    def get(self):
        videos = VideoRecord.objects.filter(status=VideoRecord.Status.ANALYSIS).order_by("created_at")
        serializer = VideoRecordSerializer(videos, many=True)
        logger.info("Fetched %d videos for analysis", len(videos))
        return Response(serializer.data, status=status.HTTP_200_OK)


class VideoAnalysisActionAPIView(APIView):
    def post(self, request: HttpRequest, pk):
        try:
            video = VideoRecord.objects.get(pk=pk)
        except VideoRecord.DoesNotExist:
            logger.warning("VideoRecord not found for id=%s", pk)
            return Response({"error": "VideoRecord not found"}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get("action")
        if action not in ["approve", "reject"]:
            logger.warning("Invalid action '%s' for VideoRecord id=%s", action, pk)
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

        if action == "approve":
            video.status = VideoRecord.Status.APPROVED
            logger.info("VideoRecord id=%s approved", pk)
            _apply_hook_and_description(video)
            _send_to_external_service(video)
        else:
            regenerate = request.data.get("regenerate", False)
            if regenerate:
                video.status = VideoRecord.Status.REGENERATE
                logger.info("VideoRecord id=%s marked for regeneration", pk)
            else:
                video.status = VideoRecord.Status.REJECTED
                logger.info("VideoRecord id=%s rejected", pk)

        video.save()
        serializer = VideoRecordSerializer(video)
        return Response(serializer.data, status=status.HTTP_200_OK)
