from django.urls import path
from .views import VideoReceiveAPIView

urlpatterns = [
    path('receive/', VideoReceiveAPIView.as_view(), name='video-receive'),
]
