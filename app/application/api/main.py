from contextlib import asynccontextmanager

from fastapi import FastAPI

from aiojobs import Scheduler
from punq import Container



from app.application.api.lifespan import close_chat_broker, close_message_broker, consume2_in_background, consume_in_background, init_chat_broker, init_message_broker
from fastapi.middleware.cors import CORSMiddleware
# from application.api.messages.handlers import router as mes
from app.application.api.auth.handlers import router as auth_router
from app.application.api.accounts.handlers import router as account_router
from app.application.api.messages.handlers import router as message_router
from app.application.api.likes.handlers import router as like_router
from app.application.api.matches.handlers import router as matches_router
from app.application.api.messages.websockets.messages import router as message_ws_router
from app.application.api.accounts.websockets.chats import router as chats_ws_router
from app.logic.init import init_container
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_message_broker()
    await init_chat_broker()

    container: Container = init_container()
    scheduler: Scheduler = container.resolve(Scheduler)

    job = await scheduler.spawn(consume_in_background())
    job2 = await scheduler.spawn(consume2_in_background())
    yield
    await close_message_broker()
    await close_chat_broker()
    await job.close()
    await job2.close()

def create_app() -> FastAPI:
    app = FastAPI(
        title='My friendship',
        docs_url='/api/docs',
        description='Application with DDD architecture ',
        debug=True,
        lifespan=lifespan
       
    )
    app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы: POST, GET, OPTIONS и т.д.
    allow_headers=["*"],  # Разрешить все заголовки
    )
    app.include_router(message_router, prefix='/Chats')
    app.include_router(like_router, prefix='/Likes')
    app.include_router(matches_router, prefix="/Matches")
    
    app.include_router(message_ws_router, prefix='/WSMessages')
    app.include_router(chats_ws_router, prefix='/WSChats')

    app.include_router(account_router, prefix="/Account")
    
    app.include_router(auth_router, prefix="/Auth")
    return app
