import asyncio
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.Connection.controller import handle_startup, handle_shutdown
# from app.Connection.controller import handle_shutdown, handle_startup
from app.Users.router import router as router_users
from app.Websocket.kafka import  KafkaService

from app.auth.router import router as router_auth
from app.Account.router import router as router_account
from app.Match.router import router as router_match
from app.Match.router import router as router_match
from app.Websocket.websocket import router as websocket_endpoint
import uvicorn
from app.Account.router import router as router_account
from app.Notification.router import router as router_notification
from app.Chats.Chats.router import router as router_chats
from app.Chats.Messages.router import router as router_messages
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import os
from pathlib import Path
from app.Connection.kafkaController.controller import kafka_service
from app.config import KAFKA_HOST, KAFKA_LIKES


app = FastAPI() 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить доступ с любых источников. В продакшне рекомендуется указывать конкретные домены.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router_users)
app.include_router(router_auth)
app.include_router(router_account)
app.include_router(router_match)
app.include_router(router_notification)
app.include_router(router_chats)
app.include_router(router_messages)
app.include_router(websocket_endpoint)




# Маппинг для настраиваемых путей
custom_paths = {}

app.add_event_handler("startup", handle_startup )
app.add_event_handler("shutdown", handle_shutdown )

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(kafka_service.start_consumers())
    print("Kafka service")

@app.on_event("shutdown")
async def shutdown_event():
    # Остановка всех консьюмеров и продюсеров
    await kafka_service.stop_all_consumers()
    await kafka_service.stop_all_producers()
    print("Kafka service")


if __name__ == "__main__":
    uvicorn.run(app, host="192.168.56.1", port=8000)
    app.add_event_handler("startup", handle_startup )
    app.add_event_handler("shutdown", handle_shutdown )
    uvicorn.run(app, host="192.168.0.102", port=8000)

    print("hellow world")