from datetime import datetime
from typing import List, Optional, Union, Any

from bson import ObjectId
from fastapi import Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection

from app.Chats.Chats.models import Message, PyObjectId
from app.Chats.Messages.models import MessageCreate
from app.Connection.mongoDB import get_db_collections_chats, get_db_collections_messages
from pymongo.errors import PyMongoError

def map_chat(chat: Any) -> Union[Message, bool]:
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
        return Message(
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




class MessagesRepository:
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
    
    async def find_all(self) -> List[Message]:
        """
        Извлекает все сообщения из базы данных.

        :return: Список объектов Messages или пустой список в случае ошибки
        """
        try:
            # Используем find() для получения всех чатов из коллекции
            cursor = self._db_collection.find()

            # Список для хранения чатов
            messages = []

            # Асинхронно итерируем по курсору
            async for document in cursor:
                print(f"{document=}")
                # Преобразуем каждую запись в объект Message
                message = Message(**document)
                messages.append(message)

            return messages

        except PyMongoError as e:
            # Логируем ошибку и возвращаем пустой список
            print(f"Ошибка при получении чатов: {e}")
            return []

        except Exception as e:
            # Обработка любых других исключений
            print(f"Неизвестная ошибка: {e}")
            return []

    async def create_message(self, data: MessageCreate) -> Optional[Message]:
        """
        Создание нового сообщения на основе предоставленных данных.

        :param data: Данные для создания сообщения.
        :return: Объект Message или None в случае ошибки.
        """
        try:
            # Здесь мы можем добавить логику для получения recipient_id на основе chat_id и sender_id
            # Например, используя отдельную функцию или метод класса для поиска получателя
            # recipient_id = await find_recipient_id(data.chat_id, data.sender_id)

            # if recipient_id is None:
            #     raise ValueError("Не удалось найти получателя для данного сообщения.")

            # Создаем новое сообщение
            new_message = Message(
                chat_id=data.chat_id,
                sender_id=data.sender_id,
                recipient_id=data.recipient_id,
                content=data.content,
                sent_at=datetime.utcnow(),
                read_by=False,
                visibility_sender=True,
                visibility_recipient=True,
                visibility_all=True
            )

            # Вставляем сообщение в базу данных (пример для MongoDB)
            result = await self._db_collection.insert_one(new_message.dict(by_alias=True))

            # Возвращаем объект Message с присвоенным идентификатором
            return new_message.copy(update={"id": PyObjectId(result.inserted_id)})

        except Exception as e:
            # Логируем ошибку и возвращаем None
            print(f"Ошибка при создании сообщения: {e}")
            return None

    async def find_by_chat_id(self, chat_id: ObjectId) -> List[Message]:
        """
        Извлекает сообщения чата из базы данных.

        :param chat_id: ID чата.
        :return: Список объектов Messages или пустой список в случае ошибки
        """
        print(chat_id)
        try:
            # Используем find() для получения сообщений из коллекции
            cursor = self._db_collection.find({"chat_id": chat_id}).sort("sent_at", -1)
            
        # Список для хранения сообщений
            messages = []
            # Асинхронно итерируем по курсору
            async for document in cursor:
                print(f"{document=}")
                # Преобразуем каждую запись в объект Message
                message = Message(**document)
                messages.append(message)
            
            return messages
        
        except PyMongoError as e:
            # Логируем ошибку и возвращаем пустой список
            print(f"Ошибка при получении чатов: {e}")
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
    #         # Преобразуем каждую запись в объект Chat
    #             chat = Chat(**document)
    #             chats.append(chat)

    #         return chats
    #     except PyMongoError as e:
    #     # Логируем ошибку и возвращаем пустой список
    #         print(f"Ошибка при получении чатов пользователя: {e}")
    #         return []

    #     except Exception as e:
    #     # Обработка любых других исключений
    #         print(f"Неизвестная ошибка: {e}")
    #         return []

    @staticmethod
    def get_instance(db_collection: AsyncIOMotorCollection = Depends(get_db_collections_messages)):
        return MessagesRepository(db_collection)