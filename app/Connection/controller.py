import asyncio

from app.Connection.mongoDB import close_connect, connect_and_init_db




async def handle_startup():
    init_mongo_future = connect_and_init_db()
    print(f"{init_mongo_future=}")
    await asyncio.gather(init_mongo_future)


async def handle_shutdown():
    await close_connect()
