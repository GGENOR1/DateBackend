from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.application.api.schemas import BaseQueryResponseSchema
from app.domain.entities.messages import (
    Chat,
    # ChatListener,
    Message,
)
from app.domain.values.messages import Text


class CreateChatRequestSchema(BaseModel):
    first_participants_id: int
    second_participants_id: int


class CreateChatResponseSchema(BaseModel):
    oid: str
    participants: List[int]


    @classmethod
    def from_entity(cls, chat: Chat) -> 'CreateChatResponseSchema':
        return cls(
            oid=chat.oid,
            participants=chat.participants,
        )


class CreateMessageSchema(BaseModel):
    text: str
    recipient_id: int
    sender_id: int


class CreateMessageResponseSchema(BaseModel):
    text: str
    oid: str

    @classmethod
    def from_entity(cls, message: Message) -> 'CreateMessageResponseSchema':
        return cls(text=message.text.as_generic_type(), oid=message.oid)


class MessageDetailSchema(BaseModel):
    oid: str
    text: str
    sent_at: datetime
    recipient_id: int
    read_by_recipient: bool

    @classmethod
    def from_entity(cls, message: Message) -> 'MessageDetailSchema':
        return cls(
            oid=message.oid,
            text=message.text.as_generic_type(),
            sent_at=message.sent_at,
            recipient_id=message.recipient_id,
            read_by_recipient=message.read_by_recipient,
        )


# class ChatDetailSchema(BaseModel):
#     oid: str
#     title: str
#     created_at: datetime

#     @classmethod
#     def from_entity(cls, chat: Chat) -> 'ChatDetailSchema':
#         return cls(
#             oid=chat.oid,
#             title=chat.title.as_generic_type(),
#             created_at=chat.created_at,
#         )
class ParticipantDetailSchema(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    # images: List[str]

class MessageFromChat(BaseModel):
    chat_oid: str
    text: Text
    sender_id: int
    recipient_id: int
    sent_at: Optional[datetime] 
    read_by_recipient: bool
    visibility_sender: bool 
    visibility_recipient: bool
    visibility_all: bool

    
class ChatDetailSchema(BaseModel):
    oid: str
    created_at: datetime
    updated_at: datetime
    delete_by_first: bool | int
    delete_by_second: bool | int
    participants: List[ParticipantDetailSchema]
    last_message: Optional[MessageFromChat]
    unread_count_messages: Optional[int]

    @classmethod
    def from_entity(cls, chat: Chat) -> 'ChatDetailSchema':
        print(f"Чат в from_entity {chat=}")
        participants_ids = [participant.user_id for participant in chat.participants]
        return cls(
            oid=chat.oid,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            delete_by_first=chat.delete_by_first,
            delete_by_second=chat.delete_by_second,
            participants=participants_ids
        )
    @classmethod
    def from_entity_details(cls, chat: Chat, count: Optional[int] = None) -> 'ChatDetailSchema':
        print(f"Чат в from_entity_details {chat=}")
        print(f"Чат в from_entity_details {chat.last_message=}")
        # Создаем детализированную информацию об участниках
        participants_details = [
             ParticipantDetailSchema(
                # oid=participant['oid'],  # Если нужно использовать `oid`
                user_id=participant['user_id'],
                first_name=participant['first_name'],  # Доступ через ключи словаря
                last_name=participant['last_name'],    # Доступ через ключи словаря
                # images=participant['images']          # Доступ через ключи словаря, если требуется
            )
            for participant in chat.participants
        ]
        last_message = (
        MessageFromChat(
            chat_oid=chat.last_message.oid,
            text=chat.last_message.text,
            sender_id=chat.last_message.sender_id,
            recipient_id=chat.last_message.recipient_id,
            sent_at=chat.last_message.sent_at,
            read_by_recipient=chat.last_message.read_by_recipient,
            visibility_sender=chat.last_message.visibility_sender,
            visibility_recipient=chat.last_message.visibility_recipient,
            visibility_all=chat.last_message.visibility_all
        ) if chat.last_message is not None else None
    )

        # Возвращаем схему с детализированными участниками
        return cls(
            oid=chat.oid,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            delete_by_first=chat.delete_by_first,
            delete_by_second=chat.delete_by_second,
            participants=participants_details,  # Детализированные участники
            last_message=last_message,
            unread_count_messages=count,
        )
    @classmethod
    def convert_dict_to_chat(cls, chat_dict: dict) -> Chat:
        print(f"Словарь при получении всех чатов {chat_dict}")
        chat = chat_dict.get('last_message')
        print(f"само последнее сообшение при получении всех чатов {chat}")
        last_message = (
        MessageFromChat(

            chat_oid=chat.oid,
            text=chat.text,
            sender_id=chat.sender_id,
            recipient_id=chat.recipient_id,
            sent_at=chat.sent_at,
            read_by_recipient=chat.read_by_recipient,
            visibility_sender=chat.visibility_sender,
            visibility_recipient=chat.visibility_recipient,
            visibility_all=chat.visibility_all
        )if chat is not None else None
        )

        return cls(
            oid=chat_dict['oid'],
            created_at=chat_dict['created_at'],
            updated_at=chat_dict['updated_at'],
            delete_by_first=chat_dict['delete_by_first'],
            delete_by_second=chat_dict['delete_by_second'],
            participants=[ParticipantDetailSchema(**participant) for participant in chat_dict['participants']],
            last_message=last_message,
            # Допустим, что поле unread_messages_count в вашем словаре существует
            unread_count_messages=chat_dict.get('unread_messages_count', 0)
        )


class AddTelegramListenerSchema(BaseModel):
    telegram_chat_id: str


# class AddTelegramListenerResponseSchema(BaseModel):
#     listener_id: str

#     @classmethod
#     def from_entity(cls, listener: ChatListener) -> 'AddTelegramListenerResponseSchema':
#         return cls(listener_id=listener.oid)


class GetMessagesQueryResponseSchema(BaseQueryResponseSchema[list[MessageDetailSchema]]):
    ...


class GetAllChatsQueryResponseSchema(BaseQueryResponseSchema[list[ChatDetailSchema]]):
    ...


# class ChatListenerListItemSchema(BaseModel):
#     oid: str

#     @classmethod
#     def from_entity(cls, chat_listener: ChatListener):
#         return cls(oid=chat_listener.oid)
