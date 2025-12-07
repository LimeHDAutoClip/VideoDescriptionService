from django.urls import path
from .views import *

urlpatterns = [
    path('videos/receive/', VideoReceiveAPIView.as_view(), name='video-receive'),
    path('videos/analysis/', VideoAnalysisListAPIView.as_view(), name='videos-analysis-list'),
    path('videos/analysis/<int:pk>/action/', VideoAnalysisActionAPIView.as_view(), name='videos-analysis-action'),
]
