import asyncio
from typing import Any, AsyncGenerator, Dict
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
from pydantic import BaseModel
import json
from app.config import KAFKA_HOST, KAFKA_LIKES, KAFKA_MATCHES
from app.Notification.service import send_push_notification
import logging

class KafkaService:
    def __init__(self, bootstrap_servers: str, client_id: str):
        self.bootstrap_servers = bootstrap_servers
        self.client_id = client_id
        self.admin_client = KafkaAdminClient(bootstrap_servers=self.bootstrap_servers)
        self.consumers = []
        self.producers = []
        logging.basicConfig(level=logging.INFO)

    def create_topic(self, topic_name: str, num_partitions: int = 1, replication_factor: int = 1):
        try:
            topic = NewTopic(name=topic_name, num_partitions=num_partitions, replication_factor=replication_factor)
            self.admin_client.create_topics(new_topics=[topic], validate_only=False)
            return f"Topic '{topic_name}' created successfully!"
        except TopicAlreadyExistsError:
            return f"Topic '{topic_name}' already exists."
        except Exception as e:
            return str(e)

    async def create_consumer(self, topic_name: str, group_id: str) -> AIOKafkaConsumer:
        consumer = AIOKafkaConsumer(
            topic_name,
            group_id=group_id,
            bootstrap_servers=self.bootstrap_servers,
            auto_offset_reset='earliest'
        )
        await consumer.start()
        self.consumers.append(consumer)
        return consumer

    async def stop_consumer(self, consumer: AIOKafkaConsumer):
        logging.info(f"Attempting to stop consumer: {consumer}")
        try:
            if consumer in self.consumers:
                logging.info(f"Consumer found in list: {consumer}")
                await consumer.stop()
                logging.info("Kafka consumer stopped successfully.")
                self.consumers.remove(consumer)
            else:
                logging.warning(f"Consumer not found in list: {consumer}")
        except Exception as e:
            logging.error(f"Error stopping consumer: {consumer}, error: {str(e)}")

    async def stop_all_consumers(self):
        print(f"{self.consumers=}")
        print(f"{self.producers=}")
        for consumer in self.consumers:
            await consumer.stop()
        self.consumers = []
        print(f"финальный блок с закрытием {self.consumers=}")

    async def get_producer(self) -> AsyncGenerator[AIOKafkaProducer, None]:
        producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            client_id=self.client_id
        )
        await producer.start()
        self.producers.append(producer)
        try:
            yield producer
        finally:
            await producer.stop()
            self.producers.remove(producer)

    async def stop_all_producers(self):
        for producer in self.producers:
            await producer.stop()
        self.producers = []
        print(f"финальный блок с закрытием {self.producers=}")
        

    async def consume_messages(self, topic_name: str, group_id: str):
        consumer = await self.create_consumer(topic_name, group_id)
        try:
            async for msg in consumer:
                await self.handle_message(msg.topic, msg.key, msg.value)
        except asyncio.CancelledError:
            # Если задача была отменена, например, при завершении работы приложения
            print(f"Task was cancelled for topic: {topic_name}")
            raise
        finally:
            # Обязательно закрываем consumer, чт
            await self.stop_consumer(consumer)

    async def handle_message(self, topic: str, key: bytes, value: bytes):
        key_str = key.decode('utf-8') if key else None
        value_str = value.decode('utf-8') if value else None
        if topic == KAFKA_LIKES:
            await self.process_like(key_str, value_str)
        elif topic == KAFKA_MATCHES:
            await self.process_match(key_str, value_str)

    async def start_consumers(self):
        await asyncio.gather(
            self.consume_messages(KAFKA_LIKES, "1"),
            self.consume_messages(KAFKA_MATCHES, "1")
        )

    async def process_like(self, key: str, value: str):
        data = json.loads(value)
        liked_user_id = data.get("liked_user_id")
        await send_push_notification("New like received!",
                                       f"{liked_user_id} liked you!")
        
    def set_message_callback(self, consumer: AIOKafkaConsumer, callback):
        async def consume_messages():
            try:
                async for message in consumer:
                    await callback(message)
            finally:
                await consumer.stop()

        asyncio.create_task(consume_messages())
    async def process_match(self, key: str, value: str):
        data = json.loads(value)
        liked_user_id = data.get("liked_user_id")
        await send_push_notification("New match found!",
                                       f"You have a new match with {liked_user_id}!")
    
    async def send_message(self, topic: str, key: str, value: Dict[str, Any]):
        async for producer in self.get_producer():
            await producer.send_and_wait(topic, key=key.encode('utf-8'), value=json.dumps(value).encode('utf-8'))
            print(f"Message sent to {topic}: {key} - {value}")
# Global KafkaService instance
kafka_service = KafkaService(bootstrap_servers=KAFKA_HOST, client_id=1)