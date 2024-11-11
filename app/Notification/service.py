
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

async def send_push_notification(expo_push_token: str, title: str, body: str, data: dict = None,  ):
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

