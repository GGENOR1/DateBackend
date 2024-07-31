from fastapi import APIRouter, WebSocket, WebSocketDisconnect


router = APIRouter(
    prefix="/ws",
    tags=["WebSocket"],
)
connected_clients = {}

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    connected_clients[user_id] = websocket

    try:
        while True:
            data = await websocket.receive_text()
            # Обработка входящих данных при необходимости
            print(data)
    except WebSocketDisconnect:
        del connected_clients[user_id]

# Функция для отправки обновлений о новом матче
async def notify_new_match(user_id: int, match: dict):
    if user_id in connected_clients:
        websocket = connected_clients[user_id]
        await websocket.send_json(match)

# # Функция для создания нового матча и уведомления пользователей
# def create_match(user1_id: int, user2_id: int, db: Session = Depends(get_db)):
#     match = db.query(Match).filter(
#         (Match.user1_id == user2_id) & (Match.user2_id == user1_id) |
#         (Match.user1_id == user1_id) & (Match.user2_id == user2_id)
#     ).first()
#
#     if match:
#         # Если матч уже существует, обновляем его
#         match.is_viewed_by_user1 = False
#         match.is_viewed_by_user2 = False
#         db.commit()
#
#         # Отправляем обновления пользователям
#         match_data = {
#             "match_id": match.id,
#             "user1_id": match.user1_id,
#             "user2_id": match.user2_id
#         }
#
#         asyncio.create_task(notify_new_match(user1_id, match_data))
#         asyncio.create_task(notify_new_match(user2_id, match_data))
#     else:
#         # Создаем новый матч
#         new_match = Match(user1_id=user1_id, user2_id=user2_id)
#         db.add(new_match)
#         db.commit()
#         db.refresh(new_match)
#
#         # Отправляем обновления пользователям
#         match_data = {
#             "match_id": new_match.id,
#             "user1_id": new_match.user1_id,
#             "user2_id": new_match.user2_id
#         }
#
#         asyncio.create_task(notify_new_match(user1_id, match_data))
#         asyncio.create_task(notify_new_match(user2_id, match_data))