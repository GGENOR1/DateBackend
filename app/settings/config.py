from pydantic import Field, model_validator
from pydantic_settings import BaseSettings

from app.settings.general import GeneralSettings



class PostgresSettings(GeneralSettings):
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB_URL: str | None = None

    @model_validator(mode="before")  # noqa
    @classmethod
    def assemble_postgres_url(cls, values: dict[str, str]) -> dict[str, str]:
        if values.get("POSTGRES_DB_URL"):
            return values

        username = values.get("POSTGRES_USER")
        password = values.get("POSTGRES_PASSWORD")
        host = values.get("POSTGRES_HOST")
        port = values.get("POSTGRES_PORT")
        db_name = values.get("POSTGRES_DB")
        values["POSTGRES_DB_URL"] = (
            f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{db_name}"
        )

        return values
    

class MongoDBSettings(GeneralSettings):
    mongodb_connection_uri: str
    mongodb_match_database: str
    mongodb_match_collection: str
    mongodb_likes_collection: str
    mongodb_chat_database: str
    mongodb_messages_collection: str | None = None

    @model_validator(mode="before")  # noqa
    @classmethod
    def assemble_mongo_url(cls, values: dict[str, str]) -> dict[str, str]:

        cls.mongodb_connection_uri = values.get("MONGODB_CONNECTION_URI")
        print(f"вот в кконцифугации {cls.mongodb_connection_uri=}")
        cls.mongodb_match_database = values.get("MONGODB_MATCH_DATABASE")
        cls.mongodb_match_collection = values.get('MONGO_COLLECTION_MATCH')
        cls.mongodb_likes_collection = values.get('MONGO_COLLECTION_LIKES')
        cls.mongodb_chat_database = values.get('MONGODB_CHAT_DATABASE')
        cls.mongodb_messages_collection = values.get('MONGODB_MESSAGES_COLLECTION')
    # # print(f"Строка подключения к бд {postgres_url}")
    # #База данных с лайками и матчами
    # mongodb_match_database: str = Field(default='Match', alias='MONGODB_MATCH_DATABASE')
    # mongodb_match_collection: str = Field(default='Match', alias='MONGO_COLLECTION_MATCH')
    # mongodb_likes_collection: str = Field(default='Likes', alias='MONGO_COLLECTION_LIKES')
    
    # #База данных с чатами и сообщениями
    # mongodb_chat_database: str = Field(default='Сhats', alias='MONGODB_CHAT_DATABASE')
    # mongodb_messages_collection: str = Field(default='messages', alias='MONGODB_MESSAGES_COLLECTION')

        return values

