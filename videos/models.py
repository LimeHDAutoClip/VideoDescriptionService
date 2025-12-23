from django.db import models


class VideoRecord(models.Model):
    class Status:
        RECEIVED = "RECEIVED"
        ANALYSIS = "ANALYSIS"
        APPROVED = "APPROVED"
        REJECTED = "REJECTED"
        REGENERATE = "REGENERATE"
        ERROR_LLM = "ERROR_LLM"
        ERROR_DOWNLOAD = "ERROR_DOWNLOAD"

    STATUS_CHOICES = [
        (Status.RECEIVED, "Received"),
        (Status.ANALYSIS, "Analysis"),
        (Status.APPROVED, "Approved"),
        (Status.REJECTED, "Rejected"),
        (Status.REGENERATE, "Regenerate"),
        (Status.ERROR_LLM, "Error_LLM"),
        (Status.ERROR_DOWNLOAD, "Error_download"),
    ]

    video_url = models.URLField()
    video_path = models.CharField(max_length=512, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=Status.RECEIVED
    )
    transcription = models.TextField()
    description = models.TextField(blank=True, null=True)
    hook = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.video_url} ({self.status})"


class Prompt(models.Model):
    name = models.CharField(max_length=255, unique=True)
    content = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name