import asyncio

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from config.logger import logger
from videos.models import VideoRecord
from .serializers import VideoRecordSerializer
from videos.hook import insert_hook
from videos.tasks import process_video_task
from videos.download import download_video


class VideoReceiveAPIView(APIView):
    def post(self, request):
        serializer = VideoRecordSerializer(data=request.data)
        if serializer.is_valid():
            video_record = serializer.save(
                status=VideoRecord.Status.RECEIVED
            )
            logger.info(
                "VideoRecord created id=%s url=%s", video_record.id, video_record.video_url
            )

            process_video_task.delay(record_id=video_record.id)

            return Response(
                VideoRecordSerializer(video_record).data,
                status=status.HTTP_201_CREATED
            )

        logger.warning("Failed to create VideoRecord: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VideoAnalysisListAPIView(APIView):
    def get(self, request):
        videos = VideoRecord.objects.filter(status=VideoRecord.Status.ANALYSIS).order_by("created_at")
        serializer = VideoRecordSerializer(videos, many=True)
        logger.info("Fetched %d videos for analysis", len(videos))
        return Response(serializer.data, status=status.HTTP_200_OK)


class VideoAnalysisActionAPIView(APIView):
    def post(self, request, pk):
        try:
            video = VideoRecord.objects.get(id=pk)
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
            record = VideoRecord.objects.get(id=pk)

            try:
                file_path = asyncio.run(download_video(record.video_url))
                record.video_path = file_path
                record.save(update_fields=["video_path"])
                logger.info("Downloaded video for record %s -> %s", record.id, file_path)
            except Exception as e:
                logger.exception("Download failed for record %s: %s", record.id, e)
                record.status = VideoRecord.Status.ERROR_DOWNLOAD
                record.save(update_fields=["status"])
                return

            insert_hook(
                video.video_path,
                video.video_path.replace("processed", "hooked"),
                video.hook
            )
            logger.info("VideoRecord id=%s hooked", pk)
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
