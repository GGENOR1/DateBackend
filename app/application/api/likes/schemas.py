from datetime import datetime
from pydantic import BaseModel

from app.domain.entities.likes import Like


class CreateLikeRequestSchema(BaseModel):
    liked_by_user_id: int

class CreateLikeResponseSchema(BaseModel):
    oid: str
    liked_by_user_id: int


    @classmethod
    def from_entity(cls, like: Like) -> 'CreateLikeResponseSchema':
        return cls(
            oid=like.oid,
            liked_by_user_id=like.liked_by_user_id,
        )
    

class LikeDetailsSchema(BaseModel):
    user_id: int
    liked_by_user_id: int
    creation_date: datetime
    is_viewed_by_liked_user: bool
    status: bool

    @classmethod
    def from_entity(cls, like: Like) -> 'LikeDetailsSchema':
        return cls(
            user_id=like.user_id,
            liked_by_user_id=like.liked_by_user_id,
            creation_date=like.creation_date,
            is_viewed_by_liked_user=like.is_viewed_by_liked_user,
            status=like.status,
        )
