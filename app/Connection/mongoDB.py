import os
import asyncio

from app.config import MONGO_DB, MONGO_URI, MONGO_COLLECTION_LIKES

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

db_client: AsyncIOMotorClient = None


async def get_db_collections_matches() -> AsyncIOMotorCollection:
    print(MONGO_COLLECTION_LIKES)
    print(MONGO_DB)
    return db_client["Match"]["Match"]

async def get_db_collections_likes() -> AsyncIOMotorCollection:
    print(MONGO_COLLECTION_LIKES)
    print(MONGO_DB)
    return db_client["Match"]["Likes"]

async def get_db_collections_chats() -> AsyncIOMotorCollection:
    print(MONGO_DB)
    return db_client["Chats"]["Chats"]

async def get_db_collections_messages() -> AsyncIOMotorCollection:
    print(MONGO_DB)
    return db_client["Chats"]["Messages"]

async def connect_and_init_db():
    global db_client
    try:
        db_client = AsyncIOMotorClient(MONGO_URI)
        print(f"Successful connection to {MONGO_URI}")
    except Exception as ex:
        print(f"Cant connection {ex} to {MONGO_URI}")


async def close_connect():
    global db_client
    if db_client is None:
        print("Connection close")
        return
    else:
        db_client.close()