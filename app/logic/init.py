from functools import lru_cache
from uuid import uuid4
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from aiojobs import Scheduler
from aiokafka import (
    AIOKafkaConsumer,
    AIOKafkaProducer,
)
from motor.motor_asyncio import AsyncIOMotorClient
from punq import (
    Container,
    Scope,
)


from app.infra.repositories.likes.base import BaseLikesRepository
from app.infra.repositories.likes.mongo import MongoDBLikesRepository
from app.infra.repositories.matches.base import BaseMatchesRepository
from app.infra.repositories.matches.mongo import MongoDBMatchesRepository
from app.logic.commands.likes import CreateLikeCommand, CreateLikeCommandHandler
from app.logic.commands.matches import CreateMatchCommand, CreateMatchCommandHandler
from app.logic.queries.likes import CheckLikeQuery, CheckLikeQueryHandler, GetLikeDetailQuery, GetLikeDetailQueryHandler
from app.settings import settings
from app.domain.events.messages import (
    ChatDeletedEvent,
    ListenerAddedEvent,
    NewChatCreatedEvent,
    NewMessageReceivedEvent,
)
from app.domain.postgresql.database import Database
from app.infra.message_brokers.base import BaseChatBroker, BaseMessageBroker
from app.infra.message_brokers.kafka import KafkaMessageBroker

from app.infra.repositories.accounts.accounts import IUserRepository, ORMUserRepository
# from app.infra.repositories.auth.auth import IUserAuthRepository, UserAuthRepository
from app.infra.repositories.messages.base import (
    BaseChatsRepository,
    BaseMessagesRepository,
)
from app.infra.repositories.messages.mongo import (
    MongoDBChatsRepository,
    MongoDBMessagesRepository,
)
from app.infra.security.base import IPasswordHasher
from app.infra.security.security import PasswordHasher
from app.infra.websockets.managers import (
    BaseConnectionManager,
    ConnectionManager,
)
from app.logic.commands.account import CreateUserCommand, CreateUserCommandHandler, DeleteUserCommand, DeleteUserCommandHandler, UpdateUserDetailsCommand, UpdateUserDetailsCommandHandler
from app.logic.commands.messages import (
    AddTelegramListenerCommand,
    # AddTelegramListenerCommandHandler,
    CreateChatCommand,
    CreateChatCommandHandler,
    CreateMessageCommand,
    CreateMessageCommandHandler,
    DeleteChatCommand,
    DeleteChatCommandHandler,
)
from app.logic.events.messages import (
    ChatDeletedEventHandler,
    ListenerAddedEventHandler,
    NewChatCreatedEventHandler,
    NewChatReceivedFromBrokerEvent,
    NewChatReceivedFromBrokerEventHandler,
    NewMessageReceivedEventHandler,
    NewMessageReceivedFromBrokerEvent,
    NewMessageReceivedFromBrokerEventHandler,
)
from app.logic.mediator.base import Mediator
from app.logic.mediator.event import EventMediator

from app.logic.queries.accounts import GetAccountDetailsQuery, GetAccountDetailsQueryHandler, GetAccountQuery, GetAccountQueryHandler
from app.logic.queries.auth import GetTokenQuery, GetTokenQueryHandler
from app.logic.queries.messages import (
    GetAllChatsListenersQuery,
    # GetAllChatsListenersQueryHandler,
    GetAllChatsQuery,
    GetAllChatsQueryHandler,
    GetChatDetailQuery,
    GetChatDetailQueryHandler,
    GetMessagesQuery,
    GetMessagesQueryHandler,
)
from app.services.accounts import IUserService, ORMUserService
from app.settings.all_config import Configurate




@lru_cache(1)
def init_container() -> Container:
    return _init_container()


def _init_container() -> Container:
    container = Container()

    container.register(Configurate, instance=Configurate(), scope=Scope.singleton)

    config: Configurate = container.resolve(Configurate)

    def create_mongodb_client():
        return AsyncIOMotorClient(
            settings.mongodb_connection_uri,
            serverSelectionTimeoutMS=3000,
        )

    container.register(AsyncIOMotorClient, factory=create_mongodb_client, scope=Scope.singleton)
    client = container.resolve(AsyncIOMotorClient)

    def init_chats_mongodb_repository() -> BaseChatsRepository:
        return MongoDBChatsRepository(
            mongo_db_client=client,
            mongo_db_db_name=settings.mongodb_chat_database,
            mongo_db_collection_name=settings.mongodb_chat_database,
        )
    def init_likes_mongodb_repository() -> BaseLikesRepository:
        return MongoDBLikesRepository(
            mongo_db_client=client,
            mongo_db_db_name=settings.mongodb_match_database,
            mongo_db_collection_name=settings.mongodb_likes_collection,
        )
    
    def init_matches_mongodb_repository() -> BaseLikesRepository:
        return MongoDBMatchesRepository(
            mongo_db_client=client,
            mongo_db_db_name=settings.mongodb_match_database,
            mongo_db_collection_name=settings.mongodb_match_collection,
        )

    def init_messages_mongodb_repository() -> BaseMessagesRepository:
        return MongoDBMessagesRepository(
            mongo_db_client=client,
            mongo_db_db_name=settings.mongodb_chat_database,
            mongo_db_collection_name=settings.mongodb_messages_collection,
        )
    container.register(
        Database,
        scope=Scope.singleton,
        factory=lambda: Database(
            url=settings.POSTGRES_DB_URL,
            ro_url=settings.POSTGRES_DB_URL,
        ),
    )
    # TODO: Избавиться от вызова resolve(IUserRepository)

    container.register(IUserRepository, ORMUserRepository)
    # container.register(IUserAuthRepository, UserAuthRepository)
    container.register(IUserService, ORMUserService)
    # container.register(IAuthService, ORMIAuthService)
    # container.register(IFriendService, ORMUserService)

    # container.register(PostgresHealthcheckService)

    # def healthcheck_service_factory():
    #     services = [
    #         container.resolve(PostgresHealthcheckService),
    #     ]
    #     return CompositeHealthcheckService(services=services)

    # container.register(IHealthCheckService, factory=healthcheck_service_factory)

    # container.register(AddFriendsUseCase)


    container.register(BaseChatsRepository, factory=init_chats_mongodb_repository, scope=Scope.singleton)
    container.register(BaseLikesRepository, factory=init_likes_mongodb_repository, scope=Scope.singleton)
    container.register(BaseMatchesRepository, factory=init_matches_mongodb_repository, scope=Scope.singleton)
    container.register(BaseMessagesRepository, factory=init_messages_mongodb_repository, scope=Scope.singleton)
    container.register(IPasswordHasher, PasswordHasher)
    # Command handlers
    container.register(CreateChatCommandHandler)
    container.register(CreateMessageCommandHandler)
    container.register(CreateUserCommandHandler)
    container.register(CreateLikeCommandHandler)
    container.register(CreateMatchCommandHandler)

    # Query Handlers
    container.register(GetChatDetailQueryHandler)
    container.register(GetLikeDetailQueryHandler)
    container.register(CheckLikeQueryHandler)
    container.register(GetMessagesQueryHandler)
    container.register(GetAllChatsQueryHandler)
    # container.register(GetAllChatsListenersQueryHandler)

    container.register(GetAccountQueryHandler)
    container.register(GetAccountDetailsQueryHandler)

    container.register(GetTokenQueryHandler)

    def create_message_broker() -> BaseMessageBroker:
        return KafkaMessageBroker(
            producer=AIOKafkaProducer(bootstrap_servers=config.kafka_url),
            consumer=AIOKafkaConsumer(
                bootstrap_servers=config.kafka_url,
                group_id=f"chats-{uuid4()}",
                metadata_max_age_ms=30000,
            ),
        )
    def create_chat_broker() -> BaseChatBroker:
        return KafkaMessageBroker(
            producer=AIOKafkaProducer(bootstrap_servers=config.kafka_url),
            consumer=AIOKafkaConsumer(
                bootstrap_servers=config.kafka_url,
                group_id=f"user-{uuid4()}",
                metadata_max_age_ms=30000,
            ),
        )

    # Message Broker
    container.register(BaseMessageBroker, factory=create_message_broker, scope=Scope.singleton)
    container.register(BaseChatBroker, factory=create_chat_broker, scope=Scope.singleton)
    container.register(BaseConnectionManager, instance=ConnectionManager(), scope=Scope.singleton)

    # Mediator
    def init_mediator() -> Mediator:
        mediator = Mediator()

        # command handlers
        create_chat_handler = CreateChatCommandHandler(
            _mediator=mediator,
            chats_repository=container.resolve(BaseChatsRepository),
        )
        create_message_handler = CreateMessageCommandHandler(
            _mediator=mediator,
            message_repository=container.resolve(BaseMessagesRepository),
            chats_repository=container.resolve(BaseChatsRepository),
        )

        create_user_handler = CreateUserCommandHandler(
            _mediator=mediator,
            user_repository=container.resolve(IUserRepository),
            security_repository=container.resolve(IPasswordHasher)
        )

        delete_user_handler = DeleteUserCommandHandler(
            _mediator=mediator,
            user_repository=container.resolve(IUserRepository),
        )

        update_user_details_handler = UpdateUserDetailsCommandHandler(
            _mediator=mediator,
            user_repository=container.resolve(IUserRepository),
        )

        delete_chat_handler = DeleteChatCommandHandler(
            _mediator=mediator,
            chats_repository=container.resolve(BaseChatsRepository),
            messages_repository=container.resolve(BaseMessagesRepository)
        )

        
        # add_telegram_listener_handler = AddTelegramListenerCommandHandler(
        #     _mediator=mediator,
        #     chats_repository=container.resolve(BaseChatsRepository),
        # )

        create_like_handler = CreateLikeCommandHandler(
            _mediator=mediator,
            likes_repository=container.resolve(BaseLikesRepository),
        )
        create_match_handler = CreateMatchCommandHandler(
            _mediator=mediator,
            matches_repository=container.resolve(BaseMatchesRepository),
        )
        # event handlers
        new_chat_created_event_handler = NewChatCreatedEventHandler(
            broker_topic=config.new_chats_event_topic,
            message_broker=container.resolve(BaseMessageBroker),
            connection_manager=container.resolve(BaseConnectionManager),
        )
        new_message_received_handler = NewMessageReceivedEventHandler(
            message_broker=container.resolve(BaseMessageBroker),
            broker_topic=config.new_message_received_topic,
            connection_manager=container.resolve(BaseConnectionManager),
        )
        new_message_received_from_broker_event_handler = NewMessageReceivedFromBrokerEventHandler(
            message_broker=container.resolve(BaseMessageBroker),
            broker_topic=config.new_message_received_topic,
            connection_manager=container.resolve(BaseConnectionManager),
        )
        new_chat_received_from_broker_event_handler = NewChatReceivedFromBrokerEventHandler(
            message_broker=container.resolve(BaseMessageBroker),
            broker_topic=config.new_chats_event_topic,
            connection_manager=container.resolve(BaseConnectionManager),
        )

        chat_deleted_event_handler = ChatDeletedEventHandler(
            message_broker=container.resolve(BaseMessageBroker),
            broker_topic=config.chat_deleted_topic,
            connection_manager=container.resolve(BaseConnectionManager),
        )
        new_listener_added_handler = ListenerAddedEventHandler(
            message_broker=container.resolve(BaseMessageBroker),
            broker_topic=config.new_listener_added_topic,
            connection_manager=container.resolve(BaseConnectionManager),
        )

        # events
        mediator.register_event(
            NewChatCreatedEvent,
            [new_chat_created_event_handler],
        )
        mediator.register_event(
            NewMessageReceivedEvent,
            [new_message_received_handler],
        )
        mediator.register_event(
            NewMessageReceivedFromBrokerEvent,
            [new_message_received_from_broker_event_handler],
        )
        mediator.register_event(
            NewChatReceivedFromBrokerEvent,
            [new_chat_received_from_broker_event_handler],
        )
        mediator.register_event(
            ChatDeletedEvent,
            [chat_deleted_event_handler],
        )
        mediator.register_event(
            ListenerAddedEvent,
            [new_listener_added_handler],
        )


        # commands
        mediator.register_command(
            CreateChatCommand,
            [create_chat_handler],
        )
        mediator.register_command(
            CreateMessageCommand,
            [create_message_handler],
        )
        mediator.register_command(
            DeleteChatCommand,
            [delete_chat_handler],
        )
        # mediator.register_command(
        #     AddTelegramListenerCommand,
        #     [add_telegram_listener_handler],
        # )
        mediator.register_command(
            CreateUserCommand,
            [create_user_handler],
        )
        mediator.register_command(
            DeleteUserCommand,
            [delete_user_handler],
        )
        mediator.register_command(
            UpdateUserDetailsCommand,
            [update_user_details_handler],
        )
        mediator.register_command(
            CreateLikeCommand,
            [create_like_handler],
        )

        mediator.register_command(
            CreateMatchCommand,
            [create_match_handler],
        )

        # Queries
        mediator.register_query(
            GetChatDetailQuery,
            container.resolve(GetChatDetailQueryHandler),
        )
        mediator.register_query(
            GetLikeDetailQuery,
            container.resolve(GetLikeDetailQueryHandler),
        )
        mediator.register_query(
            CheckLikeQuery,
            container.resolve(CheckLikeQueryHandler),
        )
        ## Попытка реализовать запрос к postgres через медиатор на получение пользователя
        #  по id пользователя из таблицы users
        mediator.register_query(
            GetAccountQuery,
            container.resolve(GetAccountQueryHandler),
        )

        ## запрос к postgres через медиатор на получение пользователя
        #  по id пользователя из таблицы details_users
        mediator.register_query(
            GetAccountDetailsQuery,
            container.resolve(GetAccountDetailsQueryHandler),
        )

        ## Попытка реализовать Получение токена через медиатор
        mediator.register_query(
            GetTokenQuery,
            container.resolve(GetTokenQueryHandler),
        )

        mediator.register_query(
            GetMessagesQuery,
            container.resolve(GetMessagesQueryHandler),
        )
        mediator.register_query(
            GetAllChatsQuery,
            container.resolve(GetAllChatsQueryHandler),
        )
        # mediator.register_query(
        #     GetAllChatsListenersQuery,
        #     container.resolve(GetAllChatsListenersQueryHandler),
        # )

        return mediator

    container.register(Mediator, factory=init_mediator)
    container.register(EventMediator, factory=init_mediator)

    container.register(Scheduler, factory=lambda: Scheduler(), scope=Scope.singleton)

    return container
