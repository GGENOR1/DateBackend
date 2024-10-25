


from pydantic import Field
from pydantic_settings import BaseSettings


class Configurate(BaseSettings):
    # postgres_connection_host: str = Field(alias="POSTGRES_CONNECTION_HOST")
    # postgres_connection_port: str = Field(alias="POSTGRES_CONNECTION_PORT")
    # postgres_user_login: str = Field(alias="POSTGRES_USER_LOGIN")
    # postgres_user_password: str = Field(alias="POSTGRES_USER_PASSWORD")
    # postgres_accounts_db: str = Field(alias="POSTGRES_ACCOUNTS")
    # postgres_url: str = f"postgresql+asyncpg://{postgres_user_login}:{postgres_user_password}@{postgres_connection_host}:{postgres_connection_port}/{postgres_accounts_db}"
    # postgres_url = f"postgresql+asyncpg://postgres:Ruslan5360@localhost:5432/postgres"
    # mongodb_connection_uri: str = Field(alias='MONGODB_CONNECTION_URI')
    # # print(f"Строка подключения к бд {postgres_url}")
    # #База данных с лайками и матчами
    # mongodb_match_database: str = Field(default='Match', alias='MONGODB_MATCH_DATABASE')
    # mongodb_match_collection: str = Field(default='Match', alias='MONGO_COLLECTION_MATCH')
    # mongodb_likes_collection: str = Field(default='Likes', alias='MONGO_COLLECTION_LIKES')
    
    # #База данных с чатами и сообщениями
    # mongodb_chat_database: str = Field(default='Сhats', alias='MONGODB_CHAT_DATABASE')
    # mongodb_messages_collection: str = Field(default='messages', alias='MONGODB_MESSAGES_COLLECTION')

    new_message_received_topic: str = Field(default='new-messages-topic')
    new_chats_event_topic: str = Field(default='new-chats-topic')
    chat_deleted_topic: str = Field(default='chat-deleted-topic')
    new_listener_added_topic: str = Field(default='listener-added-topic')

    kafka_url: str = "localhost:9092"
    secret_key: str = 'AaPCsazeGKkYsPddmVjUoh3Kaxr5War56ha0Mw01adA='
    algorithm: str = 'HS256'
    # class Config:
    #     env_file = ".env"
    #     env_file_encoding = "utf-8"
    # pass