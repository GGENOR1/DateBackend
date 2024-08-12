
import json
from typing import AsyncGenerator
from fastapi import HTTPException
from aiokafka import AIOKafkaProducer
from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,

    PushServerError,
    PushTicketError,
)

from app.config import KAFKA_HOST, KAFKA_ID
push_client = PushClient()

#TODO: Изменить подход, принимать ID пользователя, брать данные из БД (токен) и отправлять

async def send_push_notification( title: str, body: str, data: dict = None, expo_push_token: str = "ExponentPushToken[oUPG34DCUgYctZ4djP0PQ2]"):
    print(f"Push notification")
    if data is None:
        data = {}

    # Формируем сообщение
    message = PushMessage(
        to=expo_push_token,
        title=title,
        body=body,
        data=data,
        sound="default"
    )
    print(message)
    try:
        # Отправляем уведомление
        response =  push_client.publish(message)
        print(f"{response=}")
        # Проверяем ошибки тикетов
         # Проверка состояния ответа
        if response.status != 'ok':
            raise HTTPException(status_code=400, detail=f"Error with ticket: {response.message}")

    except PushServerError as exc:
        print(f"{exc=}")
        raise HTTPException(status_code=500, detail=f"Error sending notification: {exc.errors}")

# async def send_kafka_message(producer: AIOKafkaProducer, topic: str, key: str, value: dict):
#     # Отправка сообщения
#     await producer.send_and_wait(topic, key=key.encode('utf-8'), value=json.dumps(value).encode('utf-8'))
#     print(f"Message sent to {topic}: {key} - {value}")

# async def get_kafka_producer() -> AsyncGenerator[AIOKafkaProducer, None]:
#     # Создание экземпляра продюсера
#     producer = AIOKafkaProducer(
#         bootstrap_servers=KAFKA_HOST,  # Замените на ваши настройки Kafka
#         client_id= KAFKA_ID  # Замените на ваш клиент ID
#     )
#     await producer.start()  # Запуск продюсера
#     try:
#         yield producer  # Передача продюсера в контекстный менеджер
#     finally:
#         await producer.stop()  # Остановка продюсера после использования