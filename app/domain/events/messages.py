from dataclasses import dataclass
from typing import ClassVar

from app.domain.events.base import BaseEvent


@dataclass
class NewMessageReceivedEvent(BaseEvent):
    event_title: ClassVar[str] = 'New Message Received'
    action: str
    recipient_id: str
    sender_id: str
    message_text: str
    message_oid: str
    chat_oid: str


@dataclass
class ListenerAddedEvent(BaseEvent):
    event_title: ClassVar[str] = 'New Listener Added To Chat'

    listener_oid: str


@dataclass
class NewChatCreatedEvent(BaseEvent):
    event_title: ClassVar[str] = 'New Chat Created'
    user_id: int
    chat_oid: str
    action: str = 'Created'


@dataclass
class ChatDeletedEvent(BaseEvent):
    title: ClassVar[str] = 'Chat Has Been Deleted'

    chat_oid: str
