from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from app.domain.entities.base import BaseEntity
from app.domain.events.accounts import UserDeletedEvent
from app.domain.values.messages import Title

@dataclass
class Geolocation:
    latitude: float
    longitude: float


@dataclass
class Location:
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None


@dataclass
class User:
    id: int | None = None
    
    email: str | None = None
    username: str | None = None
    password: str | None = None
    # registered_at: datetime | None = None

    @classmethod
    def create_user(cls, email: str, password: str, username: str) -> 'User':
        new_user = cls(email=email, username=username, password=password)
        return new_user
    
    def delete(self):
        self.register_event(UserDeletedEvent(id=self.id))

@dataclass
class UserDetails: 
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    zodiac_sign: Optional[str] = None
    height: Optional[int] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    location: Optional[Location] = None
    rating: Optional[int] = None
    # images: Optional[List[str]] = None
    educations: Optional[str] = None
    children: Optional[str] = None
    languages: Optional[str] = None
    alcohol: Optional[str] = None
    cigarettes: Optional[str] = None
    geolocation: Optional[Geolocation] = None
    
# @dataclass
# class Account(BaseEntity):
#     messages: str = field(default_factory=set, kw_only=True)
#     username: str = field(default_factory=set, kw_only=True)
#     role_id: int = field(default_factory=set, kw_only=True)

    # messages: set[Message] = field(default_factory=set, kw_only=True)
    # listeners: set[ChatListener] = field(default_factory=set, kw_only=True)
    # is_deleted: bool = field(default=False, kw_only=True)

    # @classmethod
    # def create_chat(cls, title: Title) -> 'Chat':
    #     new_chat = cls(title=title)
    #     new_chat.register_event(NewChatCreatedEvent(chat_oid=new_chat.oid, chat_title=new_chat.title.as_generic_type()))

    #     return new_chat

    # def add_message(self, message: Message):
    #     self.messages.add(message)
    #     self.register_event(
    #         NewMessageReceivedEvent(
    #             message_text=message.text.as_generic_type(),
    #             chat_oid=self.oid,
    #             message_oid=message.oid,
    #         ),
    #     )

    # def delete(self):
    #     self.is_deleted = True
    #     self.register_event(ChatDeletedEvent(chat_oid=self.oid))

    # def add_listener(self, listener: ChatListener):
    #     if listener in self.listeners:
    #         raise ListenerAlreadyExistsException(listener_oid=listener.oid)

    #     self.listeners.add(listener)
    #     self.register_event(ListenerAddedEvent(listener_oid=listener.oid))
