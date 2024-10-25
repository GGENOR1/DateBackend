from abc import ABC
from dataclasses import dataclass
from motor.core import AgnosticClient

from app.domain.entities.matches import Match
from app.infra.repositories.matches.base import BaseMatchesRepository
from app.infra.repositories.matches.converters import convert_match_entity_to_document

@dataclass
class BaseMongoDBRepository(ABC):
    mongo_db_client: AgnosticClient
    mongo_db_db_name: str
    mongo_db_collection_name: str

    @property
    def _collection(self):
        return self.mongo_db_client[self.mongo_db_db_name][self.mongo_db_collection_name]
    


@dataclass
class MongoDBMatchesRepository(BaseMatchesRepository, BaseMongoDBRepository):
    
    # async def get_like_by_oid(self, oid: str) -> Like | None:
    #     like_document = await self._collection.find_one(filter={'oid': oid})

    #     if not like_document:
    #         return None
    #     print(f'{like_document=}')
    #     return convert_like_document_to_entity(like_document)

    async def check_match_exists_by_id(self, user_id: int, 
                                      liked_by_user_id: int)-> bool:
        reverse_filter = {
            'user_id': liked_by_user_id,
            'liked_by_user_id': user_id
            }
        forward_filter = {
            'user_id': user_id,
            'liked_by_user_id': liked_by_user_id
            }
        
        return bool(await self._collection.find_one({'$or': [forward_filter, reverse_filter]}))


    async def add_match(self, match: Match) -> None:
        await self._collection.insert_one(convert_match_entity_to_document(match))