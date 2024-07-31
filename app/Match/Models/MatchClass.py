from typing import Optional

from pydantic import BaseModel


class MatchModel(BaseModel):
    user_id: int
    creation_date: str
    liked_user_id: Optional[int]
    is_viewed_by_liked_user: Optional[bool]
    is_viewed_by_user: Optional[bool]
    status: str

