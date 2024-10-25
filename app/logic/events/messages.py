from dataclasses import dataclass
from typing import ClassVar

from app.domain.events.messages import (
    ChatDeletedEvent,
    ListenerAddedEvent,
    NewChatCreatedEvent,
    NewMessageReceivedEvent,
)
from app.infra.message_brokers.converters import convert_event_to_broker_message
from app.logic.events.base import (
    EventHandler,
    IntegrationEvent,
)


@dataclass
class NewChatCreatedEventHandler(EventHandler[NewChatCreatedEvent, None]):
    async def handle(self, event: NewChatCreatedEvent) -> None:
        print(f"при создании? {event=}")
        await self.message_broker.send_message(
            topic=self.broker_topic,
            value=convert_event_to_broker_message(event=event),
            key=str(event.user_id).encode(),
        )


@dataclass
class ListenerAddedEventHandler(EventHandler[ListenerAddedEvent, None]):
    async def handle(self, event: NewChatCreatedEvent) -> None:
        await self.message_broker.send_message(
            topic=self.broker_topic,
            value=convert_event_to_broker_message(event=event),
            key=str(event.event_id).encode(),
        )


@dataclass
class NewMessageReceivedEventHandler(EventHandler[NewMessageReceivedEvent, None]):
    async def handle(self, event: NewMessageReceivedEvent) -> None:
        await self.message_broker.send_message(
            topic=self.broker_topic,
            value=convert_event_to_broker_message(event=event),
            key=event.chat_oid.encode(),
        )
        print("Вот тут скорее всего я отправляю ивент")


@dataclass
class NewMessageReceivedFromBrokerEvent(IntegrationEvent):
    event_title: ClassVar[str] = 'New Message From Broker Received'
    recipient_id: str
    sender_id: str
    action: str
    message_text: str
    message_oid: str
    chat_oid: str

#TODO: Тут часть кода, который отвечает за отправку сообщения в вебсокет
@dataclass
class NewMessageReceivedFromBrokerEventHandler(EventHandler[NewMessageReceivedFromBrokerEvent, None]):
    async def handle(self, event: NewMessageReceivedFromBrokerEvent) -> None:
        print(f"Из брокера сообщений для чатов полчаю {event} ")
        print(f"{self.connection_manager}")
        await self.connection_manager.send_all_mod(
            # key=event.chat_oid,
            keys=[str(event.recipient_id), str(event.sender_id)],
            bytes_=convert_event_to_broker_message(event=event),
        )
        print("Чисто в теории я получаю тут")

@dataclass
class NewChatReceivedFromBrokerEvent(IntegrationEvent):
    event_title: ClassVar[str] = 'New Chat From Broker Received'
    action: str
    # occurred_at: str
    user_id:str
    chat_oid: str


@dataclass
class NewChatReceivedFromBrokerEventHandler(EventHandler[NewChatReceivedFromBrokerEvent, None]):
    async def handle(self, event: NewChatReceivedFromBrokerEvent) -> None:
        print(f"Из брокера сообщений для чатов полчаю {event} ")
        print(f"{self.connection_manager}")
        print(f"Из брокера сообщений для чатов полчаю след тип user_id {type(event.user_id)} ")
        await self.connection_manager.send_all(
            key=str(event.user_id),
            bytes_=convert_event_to_broker_message(event=event),
        )
        print("Чисто в теории я получаю тут новый чат")

@dataclass
class ChatDeletedEventHandler(EventHandler[ChatDeletedEvent, None]):
    async def handle(self, event: ChatDeletedEvent) -> None:
        await self.message_broker.send_message(
            topic=self.broker_topic,
            value=convert_event_to_broker_message(event=event),
            key=event.chat_oid.encode(),
        )
        await self.connection_manager.disconnect_all(event.chat_oid)
