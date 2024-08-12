from dotenv import load_dotenv
import os

load_dotenv()
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME")
SECRET_KEY=os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
MONGO_DB =  os.environ.get("MONGO_DB")
MONGO_COLLECTION_LIKES = os.environ.get("MONGO_COLLECTION_LIKES")
MONGO_URI = os.environ.get("MONGO_URI")
KAFKA_HOST = os.environ.get("KAFKA_HOST")
KAFKA_LIKES = os.environ.get("KAFKA_LIKES")
KAFKA_MATCHES = os.environ.get("KAFKA_MATCHES")
KAFKA_ID = os.environ.get("KAFKA_ID")



# Дополнительная проверка значений переменных окружения
print(f"DB_HOST: {DB_HOST}")
print(f"DB_PORT: {DB_PORT}")
print(f"DB_USER: {DB_USER}")
print(f"DB_PASSWORD: {DB_PASSWORD}")
print(f"DB_NAME: {DB_NAME}")
print(f"SECRET_KEY: {SECRET_KEY}")
print(f"ALGORITHM: {ALGORITHM}")
print(f"MONGO_DB: {MONGO_DB}")
print(f"MONGO_COLLECTION_LIKES: {MONGO_COLLECTION_LIKES}")
print(f"MONGO_URI: {MONGO_URI}")
print(f"KAFKA_HOST: {KAFKA_HOST}")
print(f"KAFKA_LIKES: {KAFKA_LIKES}")
print(f"KAFKA_MATCHES: {KAFKA_MATCHES}")
print(f"KAFKA_ID: {KAFKA_ID}")


if not all([DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME]):
    raise ValueError("One or more database configuration values are missing.")