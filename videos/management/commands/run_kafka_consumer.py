from django.core.management.base import BaseCommand
from videos.kafka.consumer import run_consumer


class Command(BaseCommand):
    help = "Run Kafka consumer"

    def handle(self, *args, **options):
        run_consumer()
