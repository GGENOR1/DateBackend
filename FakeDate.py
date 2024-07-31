import asyncio
import math

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.Users.models import UserDetails, Users

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, JSON, ARRAY, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from faker import Faker
from geoalchemy2 import Geography
import random

from app.config import DB_USER, DB_HOST, DB_PORT, DB_NAME, DB_PASSWORD

faker = Faker()
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
possible_tags = ["Art", "Music", "Technologies", "Films", "Sport", "Test"]

def generate_fake_user():
    return {
        'email': faker.unique.email(),  # Генерация уникального email
        'username': faker.user_name(),
        'password': '$2b$12$AavFHk1zrsQfMOus81.3QubWtAO.8sLE0zXq7JOkBE5oXKCxnpj9a',  # Статический пароль
        'role_id': random.randint(1, 3)  # Случайный role_id от 1 до 3
    }


async def insert_users(num_users):
    async with async_session_maker() as session:
        users = [generate_fake_user() for _ in range(num_users)]

        # Создаем записи пользователей
        session.add_all([Users(**user) for user in users])

        await session.commit()
        print(f"Добавлено {num_users} пользователей.")


def generate_fake_user_details(user_id):
    tags = ["Art", "Music", "Technologies", "Films", "Sport", "Test"]
    return UserDetails(
        user_id=user_id,
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        age=random.randint(18, 99),
        gender=random.choice(["Мужской", "Женский"]),
        zodiac_sign=random.choice(
            ["Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева", "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей",
             "Рыбы"]),
        height=random.randint(150, 200),
        description=faker.text(max_nb_chars=200),
        tags=random.sample(tags, random.randint(1, 5)),  # Случайные теги из списка
        location={'city': faker.city(), 'country': faker.country()},
        rating=random.randint(1, 5),
        images=[faker.image_url() for _ in range(random.randint(1, 3))],
        educations=random.choice(['Высшее', 'Среднее']),
        children=random.choice(['Планирую', 'Уже есть', 'Не планирую']),
        languages=', '.join([faker.language_name() for _ in range(random.randint(1, 3))]),
        alcohol=random.choice(['Позитивное', 'Нейтральное', 'Негативное']),
        cigarettes=random.choice(['Позитивное', 'Негативное', 'Нейтральное']),
        geolocation=f'SRID=4326;POINT({faker.latitude()} {faker.longitude()})'
    )


# Генерация и вставка тестовых данных в таблицу user_details
async def insert_user_details():
    async with async_session_maker() as session:
        # Получение всех пользователей из базы данных
        users = await session.execute(text("SELECT id FROM users"))
        user_ids = users.scalars().all()  # Теперь user_ids будет списком целых чисел

        # Генерация и добавление деталей пользователей
        user_details_list = [generate_fake_user_details(user_id) for user_id in user_ids]
        for user_details in user_details_list:
            # Проверяем, существует ли запись с таким user_id
            existing_user = await session.execute(
                text("SELECT id FROM user_details WHERE user_id = :user_id"),
                {"user_id": user_details.user_id}
            )
            # Если запись не существует, добавляем её
            if not existing_user.scalar():
                session.add(user_details)
            else:
                print(f"UserDetails с user_id={user_details.user_id} уже существует, пропуск вставки.")

        # Подтверждаем изменения
        await session.commit()
        print("Данные успешно добавлены или обновлены.")

async def update_geolocation():
    MOSCOW_LAT = 55.7558
    MOSCOW_LON = 37.6176
    RADIUS_KM = 10

    def get_random_point(lat, lon, radius_km):
        # Константа радиуса Земли
        EARTH_RADIUS_KM = 6371.0

        # Генерация случайного угла и расстояния
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, radius_km)

        # Конвертация расстояния в радианы
        distance_radians = distance / EARTH_RADIUS_KM

        # Преобразование начальных координат в радианы
        lat_radians = math.radians(lat)
        lon_radians = math.radians(lon)

        # Вычисление новых координат
        new_lat_radians = math.asin(math.sin(lat_radians) * math.cos(distance_radians) +
                                    math.cos(lat_radians) * math.sin(distance_radians) * math.cos(angle))

        new_lon_radians = lon_radians + math.atan2(math.sin(angle) * math.sin(distance_radians) * math.cos(lat_radians),
                                                   math.cos(distance_radians) - math.sin(lat_radians) * math.sin(new_lat_radians))

        # Преобразование координат обратно в градусы
        new_lat = math.degrees(new_lat_radians)
        new_lon = math.degrees(new_lon_radians)

        return new_lat, new_lon

    async with async_session_maker() as session:
        async with session.begin():
            # Получение всех пользователей
            result = await session.execute(text("SELECT id FROM user_details"))
            users = result.fetchall()

            for user in users:
                lat, lon = get_random_point(MOSCOW_LAT, MOSCOW_LON, RADIUS_KM)
                geolocation = f'SRID=4326;POINT({lon} {lat})'
                await session.execute(text(
                    "UPDATE user_details "
                    "SET geolocation = ST_GeogFromText(:geolocation) "
                    "WHERE id = :user_id"),
                    {'geolocation': geolocation, 'user_id': user.id}
                )
            await session.commit()


# asyncio.run(insert_users(40))
# asyncio.run(insert_user_details())
asyncio.run(update_geolocation())