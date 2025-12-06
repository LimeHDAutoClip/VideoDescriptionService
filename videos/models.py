from django.db import models

class VideoRecord(models.Model):
    STATUS_CHOICES = [
        ('RECEIVED', 'Received'),
        ('ANALYSIS', 'Analysis'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    video_url = models.URLField()
    video_path = models.CharField(max_length=512, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='RECEIVED'
    )
    transcription = models.TextField()
    description = models.TextField(blank=True, null=True)
    hook = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.video_url} ({self.status})"
