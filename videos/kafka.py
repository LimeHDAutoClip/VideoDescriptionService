import asyncio
import json
from typing import Any

from aiokafka import AIOKafkaProducer
from django.conf import settings


class KafkaProducerService:
    def __init__(self) -> None:
        self._producer: AIOKafkaProducer | None = None
        self._lock = asyncio.Lock()

    async def _get(self) -> AIOKafkaProducer:
        async with self._lock:
            if not self._producer:
                self._producer = AIOKafkaProducer(
                    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
                )
                await self._producer.start()
        return self._producer  # type: ignore[return-value]

    async def send(self, topic: str, value: bytes) -> None:
        producer = await self._get()
        await producer.send_and_wait(topic, value)

    async def send_json(self, topic: str, payload: Any) -> None:
        data = json.dumps(payload).encode()
        await self.send(topic, data)

    async def stop(self) -> None:
        async with self._lock:
            if self._producer:
                await self._producer.stop()
                self._producer = None


kafka_producer = KafkaProducerService()

