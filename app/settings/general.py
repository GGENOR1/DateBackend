from enum import Enum

from pydantic_settings import BaseSettings
class Environment(str, Enum):
    DEV = "dev"
    PROD = "prod"
    LOCAL = "local"


class GeneralSettings(BaseSettings):
    SERVICE_NAME: str = "FriendlyService"
    ENVIRONMENT: Environment = Environment.DEV
    mongodb_connection_uri: str = "mongodb://localhost:27017"
    mongodb_match_database: str = "Match"
    mongodb_match_collection: str = "Match"
    mongodb_likes_collection: str = "Likes"
    mongodb_chat_database: str = "Chats"
    mongodb_messages_collection: str | None = "Messages"
    # kafka_url: str = "localhost:9092"
    # kafka_host: str = "localhost:9092"
    ALGORITHM : str= "HS256"
    algorithm: str = "HS256"
    # new_message_received_topic: str = 'new-messages'
    # new_chats_event_topic: str = F'new-chats-topic'
    # chat_deleted_topic: str = 'chat-deleted-topic'
    # new_listener_added_topic: str = 'listener-added-topic'

    # kafka_url: str ='KAFKA_URL'
    secret_key: str ='AaPCsazeGKkYsPddmVjUoh3Kaxr5War56ha0Mw01adA='
