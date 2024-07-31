from typing import Optional

from pydantic import BaseModel


class LikeModel(BaseModel):
    user_id: int
    creation_date: str
    liked_user_id: Optional[int]
    is_viewed_by_liked_user: bool
    status: str