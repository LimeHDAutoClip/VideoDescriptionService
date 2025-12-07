from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from videos.models import VideoRecord
from .serializers import VideoRecordSerializer
from config.logger import logger


class VideoReceiveAPIView(APIView):
    def post(self, request):
        serializer = VideoRecordSerializer(data=request.data)
        if serializer.is_valid():
            video_record = serializer.save(
                status=VideoRecord.STATUS_CHOICES.RECEIVED
            )
            logger.info(
                "VideoRecord created id=%s url=%s", video_record.id, video_record.video_url
            )
            return Response(VideoRecordSerializer(video_record).data, status=status.HTTP_201_CREATED)

        logger.warning("Failed to create VideoRecord: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VideoAnalysisListAPIView(APIView):
    def get(self):
        videos = VideoRecord.objects.filter(status="ANALYS").order_by("created_at")
        serializer = VideoRecordSerializer(videos, many=True)
        logger.info("Fetched %d videos for analysis", len(videos))
        return Response(serializer.data, status=status.HTTP_200_OK)


class VideoAnalysisActionAPIView(APIView):
    def post(self, request, pk):
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
            video.status = "APPROVED"
            logger.info("VideoRecord id=%s approved", pk)
            # монтаж видео
        else:
            regenerate = request.data.get("regenerate", False)
            if regenerate:
                video.status = "REGENERATE"
                logger.info("VideoRecord id=%s marked for regeneration", pk)
            else:
                video.status = "REJECTED"
                logger.info("VideoRecord id=%s rejected", pk)

        video.save()
        serializer = VideoRecordSerializer(video)
        return Response(serializer.data, status=status.HTTP_200_OK)
