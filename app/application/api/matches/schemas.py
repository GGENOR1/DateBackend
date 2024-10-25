from datetime import datetime
from pydantic import BaseModel

from app.domain.entities.matches import Match


class CreateMatchRequestSchema(BaseModel):
    
    liked_by_user_id: int

class CreateMatchResponseSchema(BaseModel):
    oid: str
    user_id: int
    liked_by_user_id: int
    creation_date: datetime



    @classmethod
    def from_entity(cls, match: Match) -> 'CreateMatchResponseSchema':
        return cls(
            oid=match.oid,
            user_id=match.user_id,
            liked_by_user_id=match.liked_by_user_id,
            creation_date=match.created_at,
        )