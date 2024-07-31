
from fastapi import HTTPException
from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,

    PushServerError,
    PushTicketError,
)
push_client = PushClient()


async def send_push_notification(expo_push_token: str, title: str, body: str, data: dict = None):
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
