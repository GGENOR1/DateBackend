from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from app.domain.entities.base import BaseEntity


@dataclass(eq=False)
class Match(BaseEntity):
    user_id: int
    liked_by_user_id: int
    is_viewed_by_user: bool = field(default=False, kw_only=True)
    is_viewed_by_liked_user: bool = field(default=False, kw_only=True)
    # creation_date: datetime = field(default=False, kw_only=True)
    # messages: set[Message] = field(default_factory=set, kw_only=True)
    # listeners: set[ChatListener] = field(default_factory=set, kw_only=True)
    # is_deleted: bool = field(default=False, kw_only=True)

    @classmethod
    def create_match(cls, user_id: int, liked_by_user_id: int) -> 'Match':
        new_match = cls(user_id=user_id, liked_by_user_id=liked_by_user_id)
        
        # TODO: Вот тут разобраться что делает данный ивент
        # new_chat.register_event(NewChatCreatedEvent(chat_oid=new_chat.oid, chat_title=new_chat.title.as_generic_type()))

        return new_match