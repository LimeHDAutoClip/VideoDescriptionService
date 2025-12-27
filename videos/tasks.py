import asyncio

from celery import shared_task
from django.utils import timezone

from config.logger import logger
from videos.LLM_worker import call_llm
from videos.models import VideoRecord

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_video_task(self, record_id: int):
    try:
        logger.info("process_video_task")
        record = VideoRecord.objects.get(id=record_id)
        transcription = record.transcription
        try:
            llm_result = asyncio.run(call_llm(transcription))
            description = llm_result.get("description", "").strip()
            hook = llm_result.get("hook", "").strip()

            record.description = description
            record.hook = hook
            record.status = VideoRecord.Status.ANALYSIS
            record.updated_at = timezone.now()
            record.save(update_fields=["description", "hook", "status", "updated_at"])
            logger.info("LLM generated for record %s", record_id)

        except Exception as e:
            logger.exception("LLM failed for record %s: %s", record_id, e)
            record.status = VideoRecord.Status.ERROR_LLM
            record.save(update_fields=["status"])
            try:
                raise self.retry(exc=e)
            except self.MaxRetriesExceededError:
                record.status = VideoRecord.Status.ERROR_LLM
                record.save(update_fields=["status"])
                return

    except VideoRecord.DoesNotExist:
        logger.error("VideoRecord %s not found", record_id)
    except Exception as e:
        logger.exception("Unexpected error in process_video_task for %s: %s", record_id, e)
