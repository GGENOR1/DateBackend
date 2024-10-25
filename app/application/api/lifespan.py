

from app.infra.message_brokers.base import BaseChatBroker, BaseMessageBroker
from app.logic.events.messages import NewChatReceivedFromBrokerEvent, NewMessageReceivedFromBrokerEvent
from app.logic.init import init_container
from app.logic.mediator.base import Mediator
from app.settings.all_config import Configurate


async def init_message_broker():
    
    ''' Иницилизация брокера сообщений '''

    container = init_container()
    message_broker: BaseMessageBroker = container.resolve(BaseMessageBroker)
    await message_broker.start()

async def init_chat_broker():
    
    ''' Иницилизация брокера сообщений '''

    container = init_container()
    chat_broker: BaseChatBroker = container.resolve(BaseChatBroker)
    await chat_broker.start()

async def consume_in_background():
    container = init_container()
    config: Configurate = container.resolve(Configurate)
    message_broker: BaseMessageBroker = container.resolve(BaseMessageBroker)

    mediator: Mediator = container.resolve(Mediator)

    async for msg in message_broker.start_consuming(config.new_message_received_topic):
        await mediator.publish([
            NewMessageReceivedFromBrokerEvent(
                message_text=msg['message_text'],
                message_oid=msg['message_oid'],
                chat_oid=msg['chat_oid'],
                recipient_id=msg["recipient_id"],
                sender_id=msg["sender_id"],
                action=msg["action"],
            ),
        ])

async def consume2_in_background():
    container = init_container()
    config: Configurate = container.resolve(Configurate)
    chat_broker: BaseChatBroker = container.resolve(BaseChatBroker)

    mediator: Mediator = container.resolve(Mediator)

    async for msg in chat_broker.start_consuming(config.new_chats_event_topic):
        print(f"получаемое сообщение {msg}")
        await mediator.publish([
            NewChatReceivedFromBrokerEvent(
                # occurred_at=msg['occurred_at'],
                chat_oid=msg['chat_oid'],
                user_id=msg['user_id'],
                action=msg['action'],
                
                
            ),
        ])

async def close_message_broker():
    container = init_container()
    message_broker: BaseMessageBroker = container.resolve(BaseMessageBroker)
    await message_broker.close()

async def close_chat_broker():
    container = init_container()
    chat_broker: BaseChatBroker = container.resolve(BaseChatBroker)
    await chat_broker.close()