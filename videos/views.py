# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from videos.models import VideoRecord
# from .serializers import VideoRecordSerializer
#
# class VideoReceiveAPIView(APIView):
#     def post(self, request):
#         serializer = VideoRecordSerializer(data=request.data)
#         if serializer.is_valid():
#             video_record = serializer.save(
#                 status=VideoRecord.STATUS_CHOICES.RECEIVED
#             )
#             return Response(VideoRecordSerializer(video_record).data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
