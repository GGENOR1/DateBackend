from dataclasses import dataclass, field
from datetime import datetime

from app.domain.entities.base import BaseEntity


@dataclass(eq=False)
class Like(BaseEntity):
    user_id: int
    liked_by_user_id: int
    is_viewed_by_liked_user: bool = field(default=False, kw_only=True)
    status: bool = field(default=False, kw_only=True)
    creation_date: datetime = field(default=False, kw_only=True)
    # messages: set[Message] = field(default_factory=set, kw_only=True)
    # listeners: set[ChatListener] = field(default_factory=set, kw_only=True)
    # is_deleted: bool = field(default=False, kw_only=True)

    

    @classmethod
    def create_like(cls, user_id: int, liked_by_user_id: int) -> 'Like':
        new_like = cls(user_id=user_id, liked_by_user_id=liked_by_user_id)
        
        # TODO: Вот тут разобраться что делает данный ивент
        # new_chat.register_event(NewChatCreatedEvent(chat_oid=new_chat.oid, chat_title=new_chat.title.as_generic_type()))

        return new_like

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