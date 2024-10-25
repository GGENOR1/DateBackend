from app.settings.config import PostgresSettings
from app.settings.general import GeneralSettings


class Settings(
    PostgresSettings,
    # MongoDBSettings,
    GeneralSettings,
    
):
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        


settings = Settings()
print(f"{settings=}")