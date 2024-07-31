from datetime import datetime
from typing import Union, Any

from bson import ObjectId
from fastapi import Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection

from app.Connection.mongoDB import get_db_collections_likes
from app.Match.Models.LikeClass import LikeModel
from app.Match.Models.MatchClass import MatchModel
def map_messages(like: Any) -> Union[LikeModel, bool]:
    try:
        user_id = str(like.get("user_id", ""))
        creation_date = str(like.get("creation_date", " "))
        liked_user_id = str(like.get("liked_user_id", " " ))
        status = str(like.get("status", " "))
        is_viewed_by_liked_user = bool(like.get("is_viewed_by_liked_user", False))
    except Exception as e:
        print(f"Error occurred while mapping match: {e}")
        return False
    finally:
        return LikeModel(user_id=user_id,
                          creation_date=creation_date,
                          liked_user_id=liked_user_id,
                          is_viewed_by_liked_user=is_viewed_by_liked_user,
                          status=status)


def get_filter(id: str) -> dict:
    return {'_id': ObjectId(id)}




class LikeRepository:
    _db_collection: AsyncIOMotorCollection

    def __init__(self, db_collection: AsyncIOMotorCollection):
        self._db_collection = db_collection

    async def find_all(self) -> list[LikeModel]:
        db_like = []
        async for mes in self._db_collection.find():
            db_like.append(map_messages(mes))
            print(mes)
        return db_like

    async def create_post(self, current_id_user: str, liked_user_id: int) -> str:
        like_model = LikeModel(
            user_id=current_id_user,
            creation_date=datetime.utcnow().isoformat(),
            liked_user_id=liked_user_id,
            is_viewed_by_liked_user=False,
            status="200",
        )
        try:
            insert_post = await self._db_collection.insert_one(like_model.dict())
        except Exception as e:
            raise HTTPException(status_code=500, detail=e)
        return str(insert_post.inserted_id)

    async def find_by_id(self, user_id: str) -> Any:
        try:
            like = self._db_collection.find({"user_id": user_id})
            likes = await like.to_list(length=100)
            print(likes)
            if not likes:
                raise HTTPException(status_code=404, detail="likes not found for the given user_id")
            return likes
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    async def find_by_user_and_liked_user(self, user_id: int, liked_user_id: int) -> Any:
        try:
            filter_query = {"user_id": user_id, "liked_user_id": liked_user_id}
            like = self._db_collection.find(filter_query)
            likes = await like.to_list(length=1)
            # Проверяем, найдено ли что-то
            if not likes:
                return None
            return likes[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
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

    @staticmethod
    def get_instance(db_collection: AsyncIOMotorCollection = Depends(get_db_collections_likes)):
        return LikeRepository(db_collection)