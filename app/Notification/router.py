from fastapi import APIRouter

from app.Notification.service import send_push_notification


router = APIRouter(
    prefix="/Notifications",
    tags=["Notifications"],
)

# ExponentPushToken[oUPG34DCUgYctZ4djP0PQ2]
#TODO: при проверке наличия взимного лайка, если имеются а Мэтча нет, надо создавать его и отправлять уведомления
@router.post("/matches")
async def send_push_notificationto_to_server():
    return await send_push_notification("ExponentPushToken[oUPG34DCUgYctZ4djP0PQ2]",
                                        "test","test")