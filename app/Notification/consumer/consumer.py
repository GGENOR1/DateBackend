# import asyncio
# import json
# from aiokafka import AIOKafkaConsumer

# from app.Notification.service import send_push_notification
# from app.config import KAFKA_HOST, KAFKA_LIKES, KAFKA_MATCHES

# async def consume_kafka_messages():
#     # Создание консумера
#     consumer = AIOKafkaConsumer(
#         KAFKA_MATCHES,  # Можно добавить несколько топиков
#         KAFKA_LIKES,
#         bootstrap_servers=KAFKA_HOST,  # Настройки вашего Kafka сервера
#         group_id="1",  # Группа консумеров для балансировки нагрузки
#         auto_offset_reset='earliest'  # С начала или с конца
#     )
#     # Запуск консумера
#     await consumer.start()
#     try:
#         # Бесконечный цикл для прослушивания сообщений
#         async for msg in consumer:
#             # Обработка сообщений
#             print(f"Получено сообщение из топика {msg.topic}: ключ={msg.key}, значение={msg.value}")
#             await handle_message(msg.topic, msg.key, msg.value)
#     finally:
#         # Остановка консумера
#         await consumer.stop()

# async def handle_message(topic: str, key: bytes, value: bytes):
#     """
#     Функция для обработки полученного сообщения.

#     :param topic: Имя топика
#     :param key: Ключ сообщения
#     :param value: Значение сообщения
#     """
#     key_str = key.decode('utf-8') if key else None
#     value_str = value.decode('utf-8') if value else None

#     if topic == KAFKA_LIKES:
#         await process_like(key_str, value_str)
#     elif topic == KAFKA_MATCHES:
#         await process_match(key_str, value_str)

# async def process_like(key: str, value: str):
#     """
#     Обработка сообщения из топика likes-topic.

#     :param key: Ключ сообщения
#     :param value: Значение сообщения
#     """
#     print(f"Обработка лайка: ключ={key}, значение={value}")
#     data = json.loads(value)
#     liked_user_id = data.get("liked_user_id")
#     # Здесь вы можете добавить код для обработки лайков, например, обновление базы данных
#     await send_push_notification("Новый пользователь оценил вас!",
#                            f"{liked_user_id} поставил вам лайк!")

# async def process_match(key: str, value: str):
#     """
#     Обработка сообщения из топика matches-topic.

#     :param key: Ключ сообщения
#     :param value: Значение сообщения
#     """
#     print(f"Обработка мэтча: ключ={key}, значение={value}")
#     data = json.loads(value)
#     liked_user_id = data.get("liked_user_id")
#     await send_push_notification("У вас новое совпадение!",
#                            f"У вас новое совпадение с {liked_user_id} !")
#     # Здесь вы можете добавить код для обработки мэтчей, например, отправка уведомлений

# # Запуск консумера в асинхронном событии
