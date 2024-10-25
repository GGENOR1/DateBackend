
import asyncio
import json
from typing import Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from pydantic import BaseModel
from app.Connection.kafkaController.controller import kafka_service  # Импорт глобального экземпляра

router =APIRouter(
    prefix="/WS",
    tags=["WS"],
)

# Словарь для хранения веб-сокет-соединений
active_connections: Dict[str, WebSocket] = {}


@router.websocket("/ws/user/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    print(f"{active_connections=}")
    active_connections[user_id] = websocket

    consumer = await kafka_service.create_consumer(f"{user_id}", group_id="group1")

    async def send_message_to_websocket(message):
        if websocket.application_state != WebSocketDisconnect:
            await websocket.send_text(message.value.decode('utf-8'))

    kafka_service.set_message_callback(consumer, send_message_to_websocket)

    try:
        await websocket.receive_text()  # Держим WebSocket соединение открытым
    except WebSocketDisconnect as er:
        print(f"WebSocket disconnected for user {user_id}: {er}")
    finally:
        if user_id in active_connections:
            del active_connections[user_id]
        await kafka_service.stop_consumer(consumer)
        await websocket.close()

# @router.websocket("/ws/user/{user_id}")
# async def websocket_endpoint(websocket: WebSocket, user_id: str):
#     await websocket.accept()
#     active_connections[user_id] = websocket

#     # Создаем потребителя для конкретного пользователя
#     consumer = await kafka_service.create_consumer(f"{user_id}", group_id=1)
#     print(f"connect {consumer=}")
#     print(f"active_connections {active_connections=}")
#     try:
#         async for msg in consumer:
#             await websocket.send_text(msg.value.decode('utf-8'))
#     except WebSocketDisconnect as er:
#         print(f"excepy {consumer=} with error: {er}")
#     except Exception as e:
#         print(f"Exception in websocket connection for {user_id}: {e}")
#     finally:
#         if user_id in active_connections:
#             print("Удалить бы его ")
#             del active_connections[user_id]
#         await kafka_service.stop_consumer(consumer)
#         await websocket.close()  # Закрываем WebSocket соединение

# import json
# from typing import Dict, List
# from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
# from fastapi.responses import HTMLResponse
# from pydantic import BaseModel

# from app.Redis.servise import set_in_cache

# from app.config import KAFKA_HOST, KAFKA_LIKES, KAFKA_MATCHES

# router = APIRouter(
#     prefix="/ws",
#     tags=["WebSocket"],
# )




# connections = {}


# @router.websocket("/ws/user/{user_id}")
# async def websocket_endpoint(user_id: str, websocket: WebSocket, kafka_factory: KafkaFactory = Depends(get_kafka_factory)):
#     await websocket.accept()
#     consumer = await kafka_factory.create_consumer(f"{user_id}", group_id=1)
#     connections[user_id] = websocket

#     try:
#         async for msg in consumer:
#             message_data = json.loads(msg.value.decode('utf-8'))
#             if str(message_data["receiver_id"]) == user_id:
#                 await websocket.send_text(f"New message from {message_data['sender_id']}: {message_data['content']}")
    
#     except WebSocketDisconnect:
#         print(f"Disconnecting {user_id}")
#     finally:
#         await kafka_factory.stop_consumer(consumer)
#         connections.pop(user_id, None)
       
        
# class TopicRequest(BaseModel):
#     topic_name: str
#     num_partitions: int = 1
#     replication_factor: int = 1

# @router.post("/create_topic/")
# async def create_topic_endpoint(topic_request: TopicRequest, kafka_factory: KafkaFactory = Depends(get_kafka_factory)):
#     result = kafka_factory.create_topic(
#         topic_name=topic_request.topic_name,
#         num_partitions=topic_request.num_partitions,
#         replication_factor=topic_request.replication_factor
#     )

#     if "successfully" not in result:
#         raise HTTPException(status_code=400, detail=result)
    
#     return {"message": result}

# @router.post("/create_consumer/")
# async def create_consumer_endpoint(
#     consumer_request: ConsumerRequest,
#     kafka_factory: KafkaFactory = Depends(get_kafka_factory),
#     consumer_manager: ConsumerManager = Depends(get_consumer_manager)
# ):
#     try:
#         consumer = await consumer_manager.create_consumer(
#             kafka_factory=kafka_factory,
#             topic_name=consumer_request.topic_name,
#             group_id=consumer_request.group_id
#         )
#         return {"message": f"Consumer for topic '{consumer_request.topic_name}' created successfully!"}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

# @router.post("/stop_all_consumers/")
# async def stop_all_consumers_endpoint(
#     consumer_manager: ConsumerManager = Depends(get_consumer_manager)
# ):
#     await consumer_manager.stop_all_consumers()
#     return {"message": "All consumers stopped successfully!"}