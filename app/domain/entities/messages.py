from dataclasses import (
    dataclass,
    field,
)
import datetime

from app.domain.entities.base import BaseEntity
from app.domain.events.messages import (
    ChatDeletedEvent,
    ListenerAddedEvent,
    NewChatCreatedEvent,
    NewMessageReceivedEvent,
)
from app.domain.exceptions.chats import ListenerAlreadyExistsException
from app.domain.events.messages import NewChatCreatedEvent
from app.domain.values.messages import (
    Text,
    Title,
)


@dataclass(eq=False)
class Message(BaseEntity):
    chat_oid: str
    text: Text
    sender_id: int
    recipient_id: int
    sent_at: datetime = field(default=False, kw_only=True)
    read_by_recipient: bool = field(default=False, kw_only=True)
    visibility_sender: bool = field(default=True, kw_only=True)
    visibility_recipient: bool = field(default=True, kw_only=True)
    visibility_all: bool = field(default=True, kw_only=True)


@dataclass(eq=False)
class ChatParticipants(BaseEntity):
    user_id: int



# @dataclass(eq=False)
# class Chat(BaseEntity):
#     title: Title
#     messages: set[Message] = field(default_factory=set, kw_only=True)
#     listeners: set[ChatListener] = field(default_factory=set, kw_only=True)
#     is_deleted: bool = field(default=False, kw_only=True)

#     @classmethod
#     def create_chat(cls, title: Title) -> 'Chat':
#         new_chat = cls(title=title)
#         new_chat.register_event(NewChatCreatedEvent(chat_oid=new_chat.oid, chat_title=new_chat.title.as_generic_type()))

#         return new_chat

#     def add_message(self, message: Message):
#         self.messages.add(message)
#         self.register_event(
#             NewMessageReceivedEvent(
#                 message_text=message.text.as_generic_type(),
#                 chat_oid=self.oid,
#                 message_oid=message.oid,
#             ),
#         )

#     def delete(self):
#         self.is_deleted = True
#         self.register_event(ChatDeletedEvent(chat_oid=self.oid))

#     def add_listener(self, listener: ChatListener):
#         if listener in self.listeners:
#             raise ListenerAlreadyExistsException(listener_oid=listener.oid)

#         self.listeners.add(listener)
#         self.register_event(ListenerAddedEvent(listener_oid=listener.oid))



@dataclass(eq=False)
class Chat(BaseEntity):
    last_message: str = field(default=None, kw_only=True)
    participants: dict[ChatParticipants]
    is_deleted: bool = field(default=False, kw_only=True)
    delete_by_first: bool = field(default=False, kw_only=True)
    delete_by_second: bool = field(default=False, kw_only=True)


    @classmethod
    def create_chat(cls, first_participant: ChatParticipants, second_participant :ChatParticipants) -> 'Chat':
        new_chat = cls(participants={first_participant, second_participant})
        print(f'{new_chat}')

        # TODO: разобрать что тут происходит и реализовать
        new_chat.register_event(NewChatCreatedEvent(
            chat_oid=new_chat.oid,
            user_id=first_participant,

            )
            )

        return new_chat

    def add_message(self, message: Message):
        self.last_message = message
        #TODO: ДОДЕЛАТЬ И РАЗОБРАТЬСЯ ЧТО ТУТ НЕ ТАК
        self.register_event(
            NewMessageReceivedEvent(
                message_text=message.text.as_generic_type(),
                chat_oid=self.oid,
                message_oid=message.oid,
                recipient_id=message.recipient_id,
                sender_id=message.sender_id,
                action="Update",
            ),
        )

    def delete(self, user_id: int):
        # self.is_deleted = True
        if not self.delete_by_first:
            self.delete_by_first = user_id
        else: 
            self.delete_by_second = user_id
        
        self.register_event(ChatDeletedEvent(chat_oid=self.oid))

    # TODO: Посмотреть что и как
    # def add_listener(self, listener: ChatListener):
    #     if listener in self.listeners:
    #         raise ListenerAlreadyExistsException(listener_oid=listener.oid)

    #     self.listeners.add(listener)
    #     self.register_event(ListenerAddedEvent(listener_oid=listener.oid))