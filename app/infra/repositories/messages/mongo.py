from abc import ABC
from dataclasses import dataclass

from datetime import datetime
from typing import Iterable

from motor.core import AgnosticClient

from app.domain.entities.messages import (
    Chat,
    # ChatListener,
    Message,
)
from app.infra.repositories.filters.messages import (
    GetAllChatsFilters,
    GetMessagesFilters,
)
from app.infra.repositories.messages.base import (
    BaseChatsRepository,
    BaseMessagesRepository,
)
from app.infra.repositories.messages.converters import (
    # convert_chat_document_to_entity,
    convert_chat_document_to_entity,
    convert_chat_entity_to_document,
    # convert_chat_listener_document_to_entity,
    convert_message_document_to_entity,
    convert_message_entity_to_document,
)


@dataclass
class BaseMongoDBRepository(ABC):
    mongo_db_client: AgnosticClient
    mongo_db_db_name: str
    mongo_db_collection_name: str

    @property
    def _collection(self):
        return self.mongo_db_client[self.mongo_db_db_name][self.mongo_db_collection_name]


@dataclass
class MongoDBChatsRepository(BaseChatsRepository, BaseMongoDBRepository):
    async def get_chat_by_oid(self, oid: str) -> Chat | None:
        chat_document = await self._collection.find_one(filter={'oid': oid})

        if not chat_document:
            return None

        return convert_chat_document_to_entity(chat_document)

    async def check_chat_exists_by_title(self, title: str) -> bool:
        return bool(await self._collection.find_one(filter={'title': title}))
    
    async def check_chat_exists_by_users(self, first_participants: int, second_participants: int) -> bool:
        filter_criteria = {
        'participants': {
            '$all': [first_participants, second_participants]  # Оба участника должны быть в массиве
        }
    }
        return bool(await self._collection.find_one(filter_criteria))

    async def add_chat(self, chat: Chat) -> None:
        print(f'{chat=}')
        await self._collection.insert_one(convert_chat_entity_to_document(chat))

    async def get_all_chats(self, filters: GetAllChatsFilters, user_id: int) -> Iterable[Chat]:
        cursor = self._collection.find().skip(filters.offset).limit(filters.limit)

        chats = [
            convert_chat_document_to_entity(chat_document=chat_document)
            async for chat_document in cursor
        ]
        count = await self._collection.count_documents({})

        return chats, count
    
    async def get_all_chats_by_user(self, filters: GetAllChatsFilters, user_id: int) -> Iterable[Chat]:
        # Поиск документов, где user_id есть в массиве participants
        cursor = self._collection.find(
            {'participants': {'$in': [user_id]}}  # Фильтр по user_id в массиве participants
        ).skip(filters.offset).limit(filters.limit)

        # Преобразуем документы в сущности Chat
        chats = [
            convert_chat_document_to_entity(chat_document=chat_document)
            async for chat_document in cursor
        ]

        # Подсчитываем количество документов с учетом фильтрации
        count = await self._collection.count_documents({'participants': {'$in': [user_id]}})

        return chats, count




    async def add_last_message_to_chat(self, chat_oid: str, message_oid: str) -> None:
        print(f"Последнее сообщение при обновлении чата {chat_oid}: {message_oid}")
        
        await self._collection.update_one(
            {'oid': chat_oid}, 
            {
                '$set': {
                'last_message': message_oid,
                'updated_at': datetime.utcnow()  # Обновляем поле updated_at
                }
            }
        )
    async def delete_chat_by_oid(self, chat: Chat) -> None:
        await self._collection.update_one(
        {'oid': chat.oid},
        {
            '$set': {
            'delete_by_first': chat.delete_by_first,
            'delete_by_second': chat.delete_by_second,
                }
            }
        )

    # async def delete_chat_by_oid(self, chat_oid: str) -> None:
    #     await self._collection.delete_one({'oid': chat_oid})

    async def add_telegram_listener(self, chat_oid: str, telegram_chat_id: str):
        await self._collection.update_one({'oid': chat_oid}, {'$push': {'listeners': telegram_chat_id}})

    # async def get_all_chat_listeners(self, chat_oid: str) -> Iterable[ChatListener]:
    #     chat = await self.get_chat_by_oid(oid=chat_oid)

    #     return [convert_chat_listener_document_to_entity(listener_id=listener.oid) for listener in chat.listeners]


@dataclass
class MongoDBMessagesRepository(BaseMessagesRepository, BaseMongoDBRepository):
    async def add_message(self, message: Message) -> None:
        await self._collection.insert_one(
            document=convert_message_entity_to_document(message),
        )
    
    async def get_messages(self, chat_oid: str, filters: GetMessagesFilters) -> tuple[Iterable[Message], int]:
        find = {'chat_oid': chat_oid}
        cursor = self._collection.find(find).sort('sent_at', 1).skip(filters.offset).limit(filters.limit)

        messages = [
            convert_message_document_to_entity(message_document=message_document)
            async for message_document in cursor
        ]
        count = await self._collection.count_documents(filter=find)

        return messages, count
    
    async def get_count_unread_messages(self, chat_oid: str, user_id: int) -> int:
        count = await self._collection.count_documents({
        'chat_oid': chat_oid,                      # Сообщение принадлежит указанному чату
        'recipient_id': user_id,                   # Сообщение предназначено указанному пользователю
        'read_by_recipient': False,                # Сообщение не было прочитано
        '$or': [                                   # Сообщение должно быть видно пользователю
            {'visibility_recipient': True},
            {'visibility_all': True}
        ]
    })
        return count
    
    
    async def delete_all_message_by_user(self, chat_oid: str, user_id: int) -> None:
        # Формируем условие обновления для MongoDB
        update_filter = {'chat_oid': chat_oid}
    

        # Если user_id совпадает с sender_id, обновляем visibility_sender
        update_fields_sender = {'visibility_sender': False}

        # Если user_id совпадает с recipient_id, обновляем visibility_recipient
        update_fields_recipient = {'visibility_recipient': False}

        # Используем `$set` для изменения поля видимости
        await self._collection.update_many(
            {**update_filter, 'sender_id': user_id},  # Фильтр для sender_id
            {'$set': update_fields_sender}
        )

        await self._collection.update_many(
            {**update_filter, 'recipient_id': user_id},  # Фильтр для recipient_id
            {'$set': update_fields_recipient}
        )
        


    async def get_message(self, message_oid: str) -> Message | None:
        message_document = await self._collection.find_one(filter={'oid': message_oid})

        if not message_document:
            return None
        print(f"{message_document=}")
        return convert_message_document_to_entity(message_document)
