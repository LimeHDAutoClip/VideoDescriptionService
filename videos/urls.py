from django.urls import path
from .views import *

urlpatterns = [
    path('', VideoReceiveAPIView.as_view(), name='video-receive'),
    path('analysis/', VideoAnalysisListAPIView.as_view(), name='videos-analysis-list'),
    path('analysis/<int:pk>/action/', VideoAnalysisActionAPIView.as_view(), name='videos-analysis-action'),
]
