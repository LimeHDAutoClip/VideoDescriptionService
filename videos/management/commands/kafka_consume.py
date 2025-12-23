from django.core.management.base import BaseCommand

from videos.consumers import main


class Command(BaseCommand):
    help = "Запускает Kafka consumer"

    def handle(self, *args, **options):
        main()