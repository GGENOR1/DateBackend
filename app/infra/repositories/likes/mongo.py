from abc import ABC
from dataclasses import dataclass
from motor.core import AgnosticClient

from app.domain.entities.likes import Like
from app.infra.repositories.likes.base import BaseLikesRepository
from app.infra.repositories.likes.converers import convert_like_document_to_entity, convert_like_entity_to_document


@dataclass
class BaseMongoDBRepository(ABC):
    mongo_db_client: AgnosticClient
    mongo_db_db_name: str
    mongo_db_collection_name: str

    @property
    def _collection(self):
        return self.mongo_db_client[self.mongo_db_db_name][self.mongo_db_collection_name]
    

@dataclass
class MongoDBLikesRepository(BaseLikesRepository, BaseMongoDBRepository):
    
    async def get_like_by_oid(self, oid: str) -> Like | None:
        like_document = await self._collection.find_one(filter={'oid': oid})

        if not like_document:
            return None
        print(f'{like_document=}')
        return convert_like_document_to_entity(like_document)

    async def check_like_exists_by_id(self, user_id: int, 
                                      liked_by_user_id: int)-> bool:
        
        return bool(await self._collection.find_one(
            filter={
                'user_id': user_id,
                'liked_by_user_id': liked_by_user_id
                }))

    async def add_like(self, like: Like) -> None:
        await self._collection.insert_one(convert_like_entity_to_document(like))

    # async def get_all_chats(self, filters: GetAllChatsFilters) -> Iterable[Chat]:
    #     cursor = self._collection.find().skip(filters.offset).limit(filters.limit)

    #     chats = [
    #         convert_chat_document_to_entity(chat_document=chat_document)
    #         async for chat_document in cursor
    #     ]
    #     count = await self._collection.count_documents({})

    #     return chats, count

    # async def delete_chat_by_oid(self, chat_oid: str) -> None:
    #     await self._collection.delete_one({'oid': chat_oid})

    # async def add_telegram_listener(self, chat_oid: str, telegram_chat_id: str):
    #     await self._collection.update_one({'oid': chat_oid}, {'$push': {'listeners': telegram_chat_id}})

    # async def get_all_chat_listeners(self, chat_oid: str) -> Iterable[ChatListener]:
    #     chat = await self.get_chat_by_oid(oid=chat_oid)

    #     return [convert_chat_listener_document_to_entity(listener_id=listener.oid) for listener in chat.listeners]