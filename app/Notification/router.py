from aiokafka import AIOKafkaProducer
from fastapi import APIRouter, Depends

from app.Notification.service import send_push_notification


router = APIRouter(
    prefix="/Notifications",
    tags=["Notifications"],
)

# ExponentPushToken[oUPG34DCUgYctZ4djP0PQ2]
#TODO: при проверке наличия взимного лайка, если имеются а Мэтча нет, надо создавать его и отправлять уведомления
@router.post("/matches")
async def send_push_notificationto_to_server():
    return await send_push_notification("test","test?ee", data={"wdawdaw": "wdawdassss"})


# @router.post("/kafka")
# async def send_push_notificationto_to_kafka(producer: AIOKafkaProducer = Depends(get_kafka_producer)):
#     return await send_kafka_message(producer,"likes-topic","10", {"match_id": 12, "user_id":12, "liked_user_id": 12, "status": "match_created"})