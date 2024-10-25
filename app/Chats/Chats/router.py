from datetime import datetime
from typing import List

from aiokafka import AIOKafkaProducer
from bson import ObjectId
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse

from app.Account.servise import AccountDAO
from app.Chats.Chats.models import Chat, ChatResponse, PyObjectId
from app.Chats.Chats.servise import ChatRepository
from app.Users.utils import get_async_session
from app.auth.auth import check_user_role


router = APIRouter(
    prefix="/Chats",
    tags=["Chats"],
)


#TODO: при проверке наличия взимного лайка, если имеются а Мэтча нет, надо создавать его и отправлять уведомления
@router.get("/all_chats")
async def get_all_chats(repository: ChatRepository = Depends(ChatRepository.get_instance)):
    return await repository.find_all()

@router.post("/chat", dependencies=[Depends(check_user_role(["admin", "user"]))])
async def add_chat(liked_user_id: int,
                   request: Request,
                   repository: ChatRepository = Depends(ChatRepository.get_instance),
                   session: AsyncSession = Depends(get_async_session)):
    user = request.state.user
    other_account = await AccountDAO.find_by_ids(user.id, liked_user_id, session)
    print(f"{other_account=}")
    if not other_account:
        raise HTTPException(status_code=404, detail="Users accounts not found")
    
    chat_id = await repository.create(current_id_user=user.id, liked_user_id=liked_user_id)
    # print(chat_id)
    return chat_id
# Преобразование ObjectId и datetime
def json_compatible(data):
    if isinstance(data, list):
        return [json_compatible(item) for item in data]
    elif isinstance(data, dict):
        return {key: json_compatible(value) for key, value in data.items()}
    elif isinstance(data, ObjectId):
        return str(data)
    elif isinstance(data, datetime):
        return data.isoformat()
    return data
@router.get("/chat", dependencies=[Depends(check_user_role(["admin", "user"]))])
async def chat_by_user(
    request: Request,
    repository: ChatRepository = Depends(ChatRepository.get_instance),
    session: AsyncSession = Depends(get_async_session)
):
    user = request.state.user

    # Получаем чаты текущего пользователя
    chats = await repository.find_chats_by_user(user.id)
    
    # Собираем ID всех других участников чатов
    other_user_ids = set()
    matches = []  # Храним пары (user_id, chat_id) для последующего использования

    for chat in chats:
        for participant_id in chat.participants:
            if participant_id != user.id:
                other_user_ids.add(participant_id)
                matches.append((participant_id, str(chat.id)))  # Добавляем пару в список
    
    # Получаем информацию о других пользователях
    other_users_info = await AccountDAO.find_by_ids_in_list_v2(user.id, matches, session)
    
    # Создаем словарь для быстрого поиска данных пользователя по ID
    other_users_dict = {user_info['user_id']: user_info for user_info in other_users_info}
   
    # Обогащаем чаты информацией о других участниках
    enriched_chats = []
    for chat in chats:
        # Находим других участников чата
        other_participants = [p for p in chat.participants if p != user.id]
        detailed_participants = []
        for participant_id in other_participants:
            user_info = other_users_dict.get(participant_id)
            if user_info:
                detailed_participants.append(user_info)
        
        # # Формируем полный объект чата
        enriched_chat = {
            "id": chat.id,
            
            "participants": detailed_participants,
            "last_message": chat.last_message,
            "created_at": chat.created_at,
            "updated_at": chat.updated_at
        }
        
        # print(f"{enriched_chat}")
        enriched_chats.append(enriched_chat)
        enriched_chats_json = json_compatible(enriched_chats)
    # print(f"{enriched_chats_json=}")

    return enriched_chats_json
   

# @router.get("/chat", dependencies=[Depends(check_user_role(["admin", "user"]))])
# async def chat_by_user(
#                    request: Request,
#                    repository: ChatRepository = Depends(ChatRepository.get_instance),
#                    session: AsyncSession = Depends(get_async_session)):
#     user = request.state.user
#     # account = await AccountDAO.find_by_id(user.id, session)
#     # print(f"{account=}")
#     # if not account:
#     #     raise HTTPException(status_code=404, detail="User accounts not found")
#     chats = await repository.find_chats_by_user(user.id)
#     # print(chat_id)
#     return chats



