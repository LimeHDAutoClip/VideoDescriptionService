import os
import asyncio
import logging
from celery import shared_task
from django.utils import timezone
from videos.models import VideoRecord
from videos.download import download_video
from videos.LLM_worker import call_llm

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_video_task(self, record_id: int):
    try:
        record = VideoRecord.objects.get(id=record_id)
        try:
            file_path = asyncio.run(download_video(record.video_url))
            record.video_path = file_path
            record.save(update_fields=["video_path"])
            logger.info("Downloaded video for record %s -> %s", record_id, file_path)
        except Exception as e:
            logger.exception("Download failed for record %s: %s", record_id, e)
            record.status = VideoRecord.STATUS_CHOICES.ERROR_DOWNLOAD
            record.save(update_fields=["status"])
            return

        transcription = record.transcription

        try:
            llm_result = asyncio.run(call_llm(transcription))
            description = llm_result.get("description", "").strip()
            hook = llm_result.get("hook", "").strip()
            record.description = description
            record.hook = hook
            record.status = VideoRecord.STATUS_CHOICES.ANALYS
            record.updated_at = timezone.now()
            record.save(update_fields=["description", "hook", "status", "updated_at"])
            logger.info("LLM generated for record %s", record_id)
        except Exception as e:
            logger.exception("LLM failed for record %s: %s", record_id, e)
            try:
                raise self.retry(exc=e)
            except self.MaxRetriesExceededError:
                record.status = VideoRecord.STATUS_CHOICES.ERROR_LLM
                record.save(update_fields=["status"])
                return

    except VideoRecord.DoesNotExist:
        logger.error("VideoRecord %s not found", record_id)
    except Exception as e:
        logger.exception("Unexpected error in process_video_task for %s: %s", record_id, e)
