import asyncio
from datetime import datetime
from typing import List, Optional, Union, Any

from bson import ObjectId
from fastapi import Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection

from app.Account.schema import UserAccountReturnToChat
from app.Account.servise import AccountDAO
from app.Chats.Chats.models import Chat, Message
from app.Connection.mongoDB import get_db_collections_chats
from pymongo.errors import PyMongoError
from sqlalchemy.ext.asyncio import AsyncSession
def map_chat(chat: Any) -> Union[Chat, bool]:
    try:
        # Извлечение данных из chat и преобразование их к нужным типам
        id = str(chat.get("_id", None))  # Поле _id является идентификатором чата в MongoDB
        print(f"{id=}")
        # if isinstance(chat_id, ObjectId):
        #     chat_id = PyObjectId(chat_id)

        participants = chat.get("participants", [])
        # if not isinstance(participants, list):
        #     raise ValueError("participants field must be a list of user IDs")

        # last_message_data = chat.get("last_message", None)
        # if last_message_data and isinstance(last_message_data, dict):
        #     last_message = Message(
        #         id=PyObjectId(last_message_data.get("_id")),
        #         chat_id=PyObjectId(last_message_data.get("chat_id")),
        #         sender_id=last_message_data.get("sender_id"),
        #         content=last_message_data.get("content"),
        #         sent_at=last_message_data.get("sent_at"),
        #         read_by=last_message_data.get("read_by", ""),
        #         deleted_for=last_message_data.get("deleted_for", ""),
        #         deleted_for_all=last_message_data.get("deleted_for_all", False)
        #     )
        # else:
        #     last_message = None

        # created_at = chat.get("created_at", "")
        # if isinstance(created_at, str):
        #     created_at = datetime.fromisoformat(created_at)

        # updated_at = chat.get("updated_at", datetime.utcnow())
        # if isinstance(updated_at, str):
        #     updated_at = datetime.fromisoformat(updated_at)

        # Создаем объект модели Chat
        return Chat(
            id=id,
            participants=participants,
            # last_message=last_message,
            # created_at=created_at,
            # updated_at=updated_at
        )
    
    except Exception as e:
        print(f"Error occurred while mapping chat: {e}")
        return False


def get_filter(id: str) -> dict:
    return {'_id': ObjectId(id)}




class ChatRepository:
    _db_collection: AsyncIOMotorCollection

    def __init__(self, db_collection: AsyncIOMotorCollection):
        self._db_collection = db_collection


    # async def create(self, current_id_user: int, liked_user_id: int) -> str:
    #     """
    #     Создание нового чата между двумя пользователями.
    #     :param current_id_user: ID текущего пользователя
    #     :param liked_user_id: ID понравившегося пользователя
    #     :return: Идентификатор нового чата в виде строки
    #     """
    #     # Проверяем наличие чата между двумя пользователями
    #     existing_chat = await self._db_collection.find_one({
    #     "participants": {"$all": [current_id_user, liked_user_id]}
    # })
    #     if existing_chat:
    #      return str(existing_chat["_id"])
    # # Создаем новый чат
    #     new_chat = Chat(
    #         participants=[current_id_user, liked_user_id],
    #         created_at=datetime.utcnow(),
    #         updated_at=datetime.utcnow()
    # )
    # # Вставляем новый чат в коллекцию и получаем его идентификатор
    #     result = await self._db_collection.insert_one(new_chat.dict(by_alias=True))
    #     return str(result.inserted_id)
    
    async def find_all(self) -> List[Chat]:
        """
        Извлекает все чаты из базы данных.

        :return: Список объектов Chat или пустой список в случае ошибки
        """
        try:
            # Используем find() для получения всех чатов из коллекции
            cursor = self._db_collection.find()

            # Список для хранения чатов
            chats = []

            # Асинхронно итерируем по курсору
            async for document in cursor:
                print(f"{document=}")
                # Преобразуем каждую запись в объект Chat
                chat = Chat(**document)
                chats.append(chat)

            return chats

        except PyMongoError as e:
            # Логируем ошибку и возвращаем пустой список
            print(f"Ошибка при получении чатов: {e}")
            return []

        except Exception as e:
            # Обработка любых других исключений
            print(f"Неизвестная ошибка: {e}")
            return []
    
    async def create(self, current_id_user: int, liked_user_id: int) -> Optional[str]:
        """
        Создание нового чата между двумя пользователями.
    
        :param current_id_user: ID текущего пользователя
        :param liked_user_id: ID понравившегося пользователя
        :return: Идентификатор нового чата в виде строки или None в случае ошибки
        """
        try:
        # Проверяем наличие чата между двумя пользователями
            existing_chat = await self._db_collection.find_one({
            "participants": {"$all": [current_id_user, liked_user_id]}
        })

            if existing_chat:
                return str(existing_chat["_id"])

        # Создаем новый чат
            new_chat = Chat(
            participants=[current_id_user, liked_user_id],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Вставляем новый чат в коллекцию и получаем его идентификатор
            result = await self._db_collection.insert_one(new_chat.dict(by_alias=True))
            return str(result.inserted_id)

        except PyMongoError as e:
        # Логируем ошибку и возвращаем None или другое значение по умолчанию
            print(f"Ошибка при создании чата: {e}")
            raise HTTPException(status_code=404, detail=f"Ошибка при создании чата: {e}")
            

        except Exception as e:
        # Обработка любых других исключений
            print(f"Неизвестная ошибка: {e}")
            raise HTTPException(status_code=404, detail=f"Неизвестная ошибка: {e}")
        
        

    async def find_chats_by_user(self, user_id: int) -> List[Chat]:
        """
        Извлекает все чаты, в которых участвует пользователь.

        :param user_id: ID пользователя
        :return: Список объектов Chat или пустой список в случае ошибки
        """
        try:
            cursor = self._db_collection.find({"participants": user_id})
            chats = []
            async for document in cursor:
            # Преобразуем каждую запись в объект Chat
                chat = Chat(**document)
                chats.append(chat)

            return chats
        except PyMongoError as e:
        # Логируем ошибку и возвращаем пустой список
            print(f"Ошибка при получении чатов пользователя: {e}")
            return []

        except Exception as e:
        # Обработка любых других исключений
            print(f"Неизвестная ошибка: {e}")
            return []


    # async def find_chats_by_user(self, user_id: int) -> List[Chat]:
    #     """
    #     Извлекает все чаты, в которых участвует пользователь.

    #     :param user_id: ID пользователя
    #     :return: Список объектов Chat или пустой список в случае ошибки
    #     """
    #     try:
    #         cursor = self._db_collection.find({"participants": user_id})
    #         chats = []
    #         async for document in cursor:
    #             # Преобразуем каждую запись в объект Chat
    #             chat = Chat(**document)
    #             # Преобразуем участников в список словарей
    #             chat.participants = [{"user_id": p["user_id"], "first_name": p["first_name"], "last_name": p["last_name"]} for p in chat.participants]
    #             chats.append(chat)

    #         return chats
    #     except PyMongoError as e:
    #         # Логируем ошибку и возвращаем пустой список
    #         print(f"Ошибка при получении чатов пользователя: {e}")
    #         return []

    #     except Exception as e:
    #         # Обработка любых других исключений
    #         print(f"Неизвестная ошибка: {e}")
    #         return []
    
    # async def find_chats_by_user(self, user_id: int, session: AsyncSession) -> List[dict]:
    #     """
    #     Извлекает все чаты, в которых участвует пользователь,
    #     и подготавливает расширенные данные об участниках.

    #     :param user_id: ID пользователя
    #     :param session: Асинхронная сессия для выполнения запросов
    #     :return: Список словарей, содержащих информацию о чатах и участниках
    #     """
    #     chats = []

    #     try:
    #         cursor = self._db_collection.find({"participants": user_id})

    #         async for document in cursor:
    #             chat = Chat(**document)

    #             try:
    #                 participants_info = await AccountDAO.get_participants_info(chat.participants, session)
    #                 print(participants_info)
    #                 await session.commit()  # коммит транзакции после успешного выполнения
    #             except Exception as e:
    #                 await session.rollback()  # откат транзакции в случае ошибки
    #                 print(f"Ошибка при получении данных участников: {e}")
    #                 continue

    #             chat_data = {
    #                 "_id": str(chat.id),
    #                 "participants": participants_info,
    #                 "last_message": chat.last_message,
    #                 "created_at": chat.created_at,
    #                 "updated_at": chat.updated_at
    #             }

    #             chats.append(chat_data)

    #     except PyMongoError as e:
    #         print(f"Ошибка при получении чатов пользователя: {e}")
    #     except Exception as e:
    #         print(f"Неизвестная ошибка: {e}")

    #     return chats

    # async def find_by_user_and_liked_user(self, user_id: int, liked_user_id: int) -> Any:
    #     try:
    #         filter_query = {"user_id": user_id, "liked_user_id": liked_user_id}
    #         like = self._db_collection.find(filter_query)
    #         likes = await like.to_list(length=1)
    #         # Проверяем, найдено ли что-то
    #         if not likes:
    #             return None
    #         return likes[0]
    #     except Exception as e:
    #         raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    # async def update_post(self, mess_id: str, mess: UpdateMessagesModel) -> Any:
    #     db_post = await self._db_collection.find_one_and_replace(get_filter(mess_id), dict(mess))
    #     chech = map_messages(db_post)
    #     if not chech:
    #         return False
    #     return chech
    #
    # async def find_mess_by_id(self, mess_id: str) -> Any:
    #     db_post = await self._db_collection.find_one(get_filter(mess_id))
    #
    #     return map_messages(db_post)
    # async def find_paginated(self, page: int, page_size: int) -> list[Messages]:
    #     skip = (page - 1) * page_size
    #     db_mess=[]
    #     async for mes in self._db_collection.find().skip(skip).limit(page_size):
    #         print(mes)
    #         db_mess.append(map_messages(mes))  # Запрос данных с пагинацией
    #     return db_mess
    #
    # async def count_documents(self,skip:int )->list[Messages]:
    #     page_size = 15000
    #     db_mess = []
    #     total_documents = self._db_collection.count_documents({})
    #     total_pages = -(-int(total_documents) // page_size)
    #     async for mes in self._db_collection.find().skip(skip).limit(page_size):
    #         print(mes)
    #         db_mess.append(map_messages(mes))# Запрос данных с пагинацией
    #     return db_mess
    # async def get_participants_info(participant_ids: List[int], session: AsyncSession) -> List[UserAccountReturnToChat]:
    #     """
    #     Получает расширенную информацию об участниках.

    #     :param participant_ids: Список ID участников
    #     :param session: Асинхронная сессия для выполнения запросов
    #     :return: Список объектов UserAccountReturnToChat
    #     """
    #     participants_info = []
        
    #     # Загружаем информацию об участниках параллельно
    #     participants_tasks = [AccountDAO.find_by_id(participant_id, session) for participant_id in participant_ids]
    #     participants_accounts = await asyncio.gather(*participants_tasks)

    #     for participant_account in participants_accounts:
    #         if participant_account:
    #             participant_info = UserAccountReturnToChat(
    #                 user_id=participant_account.id,
    #                 first_name=participant_account.first_name,
    #                 last_name=participant_account.last_name,
    #                 # image=participant_account.image_url
    #             )
    #             print(f"{participant_info=}")
    #             participants_info.append(participant_info)

    #     return participants_info
    
    @staticmethod
    def get_instance(db_collection: AsyncIOMotorCollection = Depends(get_db_collections_chats)):
        return ChatRepository(db_collection)