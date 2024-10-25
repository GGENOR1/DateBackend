from datetime import datetime
import json
from typing import List

from aiokafka import AIOKafkaProducer
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse

from app.Account.servise import AccountDAO
from app.Chats.Chats.models import Chat, PyObjectId
from app.Chats.Chats.servise import ChatRepository
from app.Chats.Messages.models import MessageCreate
from app.Chats.Messages.servise import MessagesRepository
# from app.Notification.service import get_kafka_producer
from app.Redis.servise import get_from_cache
from app.Users.utils import get_async_session
from app.auth.auth import check_user_role
from app.Connection.kafkaController.controller import kafka_service

router = APIRouter(
    prefix="/Messages",
    tags=["Messages"],
)


@router.get("/all_messages")
async def get_all_messages(repository: MessagesRepository = Depends(MessagesRepository.get_instance)):
    return await repository.find_all()


@router.post("/message", dependencies=[Depends(check_user_role(["admin", "user"]))])
async def send_message(
                   request: Request,
                   message: MessageCreate,
                   repository: MessagesRepository = Depends(MessagesRepository.get_instance),
                   session: AsyncSession = Depends(get_async_session)):
    user = request.state.user
    account = await AccountDAO.find_by_id(user.id, session)
    # print(f"{account=}")
    if not account:
        raise HTTPException(status_code=404, detail="Users accounts not found")
    message.sender_id = user.id
    # print(f"{message=}")
    message_sent = await repository.create_message(message)
    # print(f"{message_sent=}")
    # # Отправка события в Kafka после успешного создания сообщения
    kafka_event = {
        "sender_id": user.id,
        "receiver_id": message_sent.recipient_id,
        "message_id": str(message_sent.id),
        "content": message_sent.content,
        "timestamp": str(datetime.utcnow())
    }
    # print(f"{kafka_event=}")
    
    await kafka_service.send_message(
        f"{message.recipient_id}",
        key=str(message.recipient_id),
        value=json.dumps(kafka_event)
    )

    return message_sent


@router.get("/messages_by_chat", dependencies=[Depends(check_user_role(["admin", "user"]))])
async def get_messages_by_chat(id_chat: str, repository: MessagesRepository = Depends(MessagesRepository.get_instance)):
    try:
        # Преобразуем id_chat из строки в ObjectId
        chat_id = PyObjectId(id_chat)
    except ValueError:
        # Обрабатываем случай, когда id_chat не является корректным ObjectId
        raise HTTPException(status_code=400, detail="Invalid chat ID format")
    return await repository.find_by_chat_id(chat_id)