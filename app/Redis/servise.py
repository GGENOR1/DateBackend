from redis import asyncio as aioredis

# Создаем соединение с Redis
redis_pool = None

async def get_redis_pool():
    global redis_pool
    if redis_pool is None:
        redis_pool = await aioredis.from_url('redis://localhost:6379/0', encoding='utf-8')
    return redis_pool

async def get_from_cache(key):
    """Асинхронное получение данных из кеша"""
    try:
        redis = await get_redis_pool()
        value = await redis.get(key)
        if value:
            return value
    except Exception as _ex:
        print(_ex)
        return None

async def set_in_cache(key, value, ex=100):
    """Асинхронное сохранение данных в кеше"""
    try:
        redis = await get_redis_pool()
        await redis.set(key, value)
        await redis.expire(key, ex)
        return key
    except Exception as _ex:
        print(_ex)
        return None