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
# app.include_router(router_account)
# app.include_router(websocket_router)
app.include_router(router_chats)
app.include_router(router_messages)
app.include_router(websocket_endpoint)
# UPLOAD_DIR = Path("D:\\uploads")
# UPLOAD_DIR.mkdir(exist_ok=True)



# Маппинг для настраиваемых путей
custom_paths = {}

app.add_event_handler("startup", handle_startup )
# app.add_event_handler("startup", consume_kafka_messages )
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


# active_consumers = {}
# Глобальная переменная для хранения экземпляра KafkaService


# @app.on_event("startup")
# async def startup_event():
#     # Запуск консьюмера Kafka как фоновая задача
#     asyncio.create_task(kafka_service.consume_messages())

# @app.on_event("shutdown")
# async def shutdown_event():
#     await kafka_service.stop_all_consumers()

# Настройка асинхронного события для Kafka Consumer


# @app.on_event("startup")
# async def startup_event():
#     global consumer_task
#     global kafka_factory
#     # kafka_factory = KafkaFactory(bootstrap_servers=KAFKA_HOST)
#     # Запуск консьюмера Kafka как фоновая задача
#     consumer_task = asyncio.create_task(consume_kafka_messages())
#     await handle_startup()

# @app.on_event("shutdown")
# async def shutdown_event():
#     global consumer_task
#     consumer_manager = get_consumer_manager()
#     print(f"{consumer_manager=}")
#     try:
#         await consumer_manager.stop_all_consumers()
#         if consumer_task:
#             consumer_task.cancel()  # Остановка задачи консьюмера Kafka
#             try:
#                 await consumer_task
            
#             except asyncio.CancelledError:
#                 pass
#     except Exception as er:
#             print(er)
#     await handle_shutdown()



@app.post("/upload/")
async def upload_image(image: UploadFile = File(...), custom_path: str = None):
    file_location = UPLOAD_DIR / image.filename
    with open(file_location, "wb") as file_object:
        file_object.write(image.file.read())
    if custom_path:
        custom_paths[custom_path] = file_location
    return {"url": f"http://192.168.0.102:8000/uploads/{image.filename}"}


@app.get("/uploads/{filename}")
async def get_image(filename: str):
    file_path = UPLOAD_DIR / filename
    if file_path.exists():
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")


@app.get("/{custom_path}")
async def get_custom_image(custom_path: str):
    if custom_path in custom_paths:
        file_path = custom_paths[custom_path]
        if file_path.exists():
            return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")


if __name__ == "__main__":
    uvicorn.run(app, host="192.168.56.1", port=8000)
    app.add_event_handler("startup", handle_startup )
    app.add_event_handler("shutdown", handle_shutdown )
    uvicorn.run(app, host="192.168.0.102", port=8000)

    print("hellow world")