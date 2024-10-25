# from kafka.admin import KafkaAdminClient, NewTopic
# from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
# from kafka.errors import TopicAlreadyExistsError
# import asyncio

# from pydantic import BaseModel

# from app.config import KAFKA_HOST

# class KafkaFactory:
#     def __init__(self, bootstrap_servers):
#         self.bootstrap_servers = bootstrap_servers
#         self.admin_client = KafkaAdminClient(bootstrap_servers=self.bootstrap_servers)
#         self.producers = {}

#     def create_topic(self, topic_name: str, num_partitions: int = 1, replication_factor: int = 1):
#         try:
#             topic = NewTopic(name=topic_name, num_partitions=num_partitions, replication_factor=replication_factor)
#             self.admin_client.create_topics(new_topics=[topic], validate_only=False)
#             return f"Topic '{topic_name}' created successfully!"
#         except TopicAlreadyExistsError:
#             return f"Topic '{topic_name}' already exists."
#         except Exception as e:
#             return str(e)

#     async def create_consumer(self, topic_name: str, group_id: str):
#         consumer = AIOKafkaConsumer(
#             topic_name,
#             group_id=group_id,
#             bootstrap_servers=self.bootstrap_servers,
#             auto_offset_reset='earliest'
#         )
#         await consumer.start()
#         return consumer

#     async def stop_consumer(self, consumer):
#         await consumer.stop()

# # Функция для зависимости
# def get_kafka_factory():
#     return KafkaFactory(bootstrap_servers=KAFKA_HOST)


# class ConsumerRequest(BaseModel):
#     topic_name: str
#     group_id: str

# class ConsumerManager:
#     def __init__(self):
#         self.consumers = []

#     async def create_consumer(self, kafka_factory: KafkaFactory, topic_name: str, group_id: str):
#         consumer = await kafka_factory.create_consumer(topic_name, group_id)
#         self.consumers.append(consumer)
#         return consumer

#     async def stop_all_consumers(self):
#         for consumer in self.consumers:
#             await consumer.stop()
#         self.consumers = []

# def get_consumer_manager():
#     return ConsumerManager()


import asyncio
import json
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
from pydantic import BaseModel
from app.Notification.service import send_push_notification
from app.config import KAFKA_HOST, KAFKA_LIKES, KAFKA_MATCHES

class KafkaService:
    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        self.admin_client = KafkaAdminClient(bootstrap_servers=self.bootstrap_servers)
        self.consumers = []

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
        if consumer in self.consumers:
            await consumer.stop()
            self.consumers.remove(consumer)

    async def stop_all_consumers(self):
        for consumer in self.consumers:
            await consumer.stop()
        self.consumers = []

    async def consume_messages(self, topic_name: str, group_id: str, handle_message):
        consumer = await self.create_consumer(topic_name, group_id)
        try:
            async for msg in consumer:
                await handle_message(msg.topic, msg.key, msg.value)
        finally:
            await self.stop_consumer(consumer)

    async def handle_message(self, topic: str, key: bytes, value: bytes):
        key_str = key.decode('utf-8') if key else None
        value_str = value.decode('utf-8') if value else None
        if topic == KAFKA_LIKES:
            await self.process_like(key_str, value_str)
        elif topic == KAFKA_MATCHES:
            await self.process_match(key_str, value_str)

    async def process_like(self, key: str, value: str):
        print(f"Обработка лайка: ключ={key}, значение={value}")
        data = json.loads(value)
        liked_user_id = data.get("liked_user_id")
        await send_push_notification("Новый пользователь оценил вас!",
                                       f"{liked_user_id} поставил вам лайк!")

    async def process_match(self, key: str, value: str):
        print(f"Обработка мэтча: ключ={key}, значение={value}")
        data = json.loads(value)
        liked_user_id = data.get("liked_user_id")
        await send_push_notification("У вас новое совпадение!",
                                       f"У вас новое совпадение с {liked_user_id} !")

# Глобальный экземпляр KafkaService
kafka_service = KafkaService(bootstrap_servers=KAFKA_HOST)