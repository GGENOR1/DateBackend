from fastapi import (
    Depends,
    WebSocketDisconnect,
)
from fastapi.routing import APIRouter
from fastapi.websockets import WebSocket

import jwt
from punq import Container

from app.settings import settings
from app.infra.websockets.managers import BaseConnectionManager
from app.logic.exceptions.account import AccountNotFoundException
from app.logic.init import init_container
from app.logic.mediator.base import Mediator
from app.logic.queries.accounts import GetAccountQuery


router = APIRouter(tags=['chats'])


@router.websocket("/{token}/")
async def websocket_endpoint(
    token: str,
    websocket: WebSocket,
    container: Container = Depends(init_container),
):
    connection_manager: BaseConnectionManager = container.resolve(BaseConnectionManager)
    mediator: Mediator = container.resolve(Mediator)

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = payload.get("sub")
        print(f"{user_id=}")
        await mediator.handle_query(GetAccountQuery(user_id=int(user_id)))
    except AccountNotFoundException as error:
        await websocket.accept()
        await websocket.send_json(data={'error': error.message})
        await websocket.close()
        return
    except Exception as error:
        await websocket.accept()
        await websocket.send_json(data={'error': str(error)})
        await websocket.close()
        return
    print(websocket)
    await connection_manager.accept_connection(websocket=websocket, key=str(user_id))

    await websocket.send_text("You are now connected!")

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        await connection_manager.remove_connection(websocket=websocket, key=str(user_id))
