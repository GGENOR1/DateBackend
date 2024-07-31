# import asyncio
#
# from app.Users.utils import get_async_session
# from fastapi import APIRouter, Depends, HTTPException, Response, status
# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
# class AccountDAO:
#     @staticmethod
#     async def add_user(user_data: dict, session: AsyncSession):
#         new_user = Users(**user_data)
#         session.add(new_user)
#         await session.commit()
#         return new_user
#
#     @staticmethod
#     async def get_user_by_id(user_id: int, session: AsyncSession):
#         result = await session.execute(select(Users).filter_by(id=user_id))
#         user = result.scalars().first()
#         return user
from math import cos, radians, sin, atan2, sqrt
from typing import List, Dict, Tuple

from fastapi.encoders import jsonable_encoder
# from shapely import Point
from shapely.geometry import shape, Point

from app.Account.schema import Geolocation
from app.Users.models import UserDetails

from geoalchemy2 import WKTElement, WKBElement
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, ARRAY, TEXT, and_, text
from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape
from fastapi import HTTPException

def calculate_distance(lat1, lon1, lat2, lon2):
    # Константы для радиуса Земли
    R = 6371.0 # Радиус Земли в километрах

    # Преобразование градусов в радианы
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    # Разницы координат
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Формула Haversine
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Расчет расстояния
    distance = R * c

    return distance
class AccountDAO:

    @staticmethod
    async def find_by_id(user_id: int, session: AsyncSession):
        try:
            query = select(UserDetails).filter_by(user_id=user_id)
            result = await session.execute(query)
            user_account = result.scalars().first()

            if not user_account:
                raise HTTPException(status_code=404, detail="User not found")

            # Декодирование геолокации
            if user_account.geolocation:
                wkb_geom = user_account.geolocation
                point = to_shape(wkb_geom)
                user_account.geolocation = Geolocation(latitude=point.y, longitude=point.x)

            return user_account
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    @staticmethod
    async def find_by_ids(user_id1: int, user_id2: int, session: AsyncSession):
        try:
            # Поиск первой записи
            query1 = select(UserDetails).filter_by(user_id=user_id1)
            result1 = await session.execute(query1)
            user_account1 = result1.scalars().first()

            # Поиск второй записи
            query2 = select(UserDetails).filter_by(user_id=user_id2)
            result2 = await session.execute(query2)
            user_account2 = result2.scalars().first()
            if not user_account1 or not user_account2:
                raise HTTPException(status_code=404, detail="One or both users not found")

            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# TODO добавить исключения если аккаунт заблокирован или удален или не найден
    @staticmethod
    async def find_by_ids_in_list(current_user_id : int, matches: List[Tuple[bool,int]], session: AsyncSession):
        try:
            user_ids = [match[0] for match in matches]
            print(f"{user_ids}")
            query = select(UserDetails).filter_by(user_id=current_user_id)
            result = await session.execute(query)
            current_user_account = result.scalars().first()
            query = select(
                UserDetails,
                func.ST_Distance(UserDetails.geolocation, current_user_account.geolocation).label('distance')
            ).filter(
                UserDetails.user_id.in_(user_ids)
            ).order_by('distance')

            result = await session.execute(query)
            user_accounts = result.fetchall()
            # print(f"{user_accounts=}")

            if len(user_accounts) != len(user_ids):
                raise HTTPException(status_code=404, detail="One or more users not found")
            find_users = []
            for user_row, match in zip(user_accounts, matches):
                # print(match[0])
                user = user_row[0]
                distance = user_row[1]  # Расстояние в метрах

                # Преобразование WKB в Shapely объект
                wkb_geom = user.geolocation
                point = to_shape(wkb_geom)
                user_geolocation = Geolocation(latitude=point.y, longitude=point.x)

                user_dict = user.__dict__.copy()
                user_dict['geolocation'] = user_geolocation
                user_dict['distance'] = distance
                user_dict['view'] = match[1]
                find_users.append(user_dict)
                # print(f"{user_dict=}")
                # Печать значения расстояния
                # print(f"Distance for user {user.user_id}: {distance} meters")
            # Запрос для поиска пользователей и расчета расстояния
            # query = select(
            #     UserDetails,
            #     func.ST_Distance(UserDetails.geolocation, current_user_location_wkb).label('distance')
            # ).filter(
            #     UserDetails.user_id.in_(user_ids)
            # ).order_by('distance')
            #
            # result = await session.execute(query)
            # user_accounts = result.fetchall()
            #
            # if len(user_accounts) != len(user_ids):
            #     raise HTTPException(status_code=404, detail="One or more users not found")
            #
            # users_with_geolocation = []
            # for user_row in user_accounts:
            #     user = user_row[0]
            #     distance = user_row[1]  # Расстояние в метрах
            #
            #     # Преобразование WKB в Shapely объект
            #     wkb_geom = user.geolocation
            #     point = to_shape(wkb_geom)
            #     user_geolocation = Geolocation(latitude=point.y, longitude=point.x)
            #
            #     user_dict = user.__dict__.copy()
            #     user_dict['geolocation'] = user_geolocation
            #     user_dict['distance'] = distance
            #
            #     users_with_geolocation.append(user_dict)
            #
            #     # Печать значения расстояния
            #     print(f"Distance for user {user.user_id}: {distance} meters")

            return find_users
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    @staticmethod
    async def create_user(user_id: int, user_data: dict, session: AsyncSession):
        new_user = UserDetails(
            user_id=user_id,
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name"),
            age=user_data.get("age"),
            gender=user_data.get("gender"),
            zodiac_sign=user_data.get("zodiac_sign"),
            height=user_data.get("height"),
            description=user_data.get("description"),
            tags=user_data.get("tags"),
            location=user_data.get("location"),
            rating=user_data.get("rating"),
            images=user_data.get("images"),
            educations=user_data.get("educations"),
            children=user_data.get("children"),
            languages=user_data.get("languages"),
            alcohol=user_data.get("alcohol"),
            cigarettes=user_data.get("cigarettes"),
            geolocation=WKTElement(
                f'POINT({user_data["geolocation"]["longitude"]} {user_data["geolocation"]["latitude"]})', srid=4326
            ) if 'geolocation' in user_data else None

        )
        session.add(new_user)

        await session.commit()
        await session.refresh(new_user)
        return new_user

    @staticmethod
    async def update_user(user_id: int, user_data: dict, session: AsyncSession):
        query = select(UserDetails).filter_by(user_id=user_id)
        result = await session.execute(query)
        existing_user = result.scalars().first()

        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")

        for key, value in user_data.items():
            setattr(existing_user, key, value)

        await session.commit()
        await session.refresh(existing_user)
        if existing_user.geolocation:
            wkb_geom = existing_user.geolocation
            point = to_shape(wkb_geom)
            existing_user.geolocation = Geolocation(latitude=point.y, longitude=point.x)
        return existing_user

    @staticmethod
    async def update_user_geolocation(user_id: int, longitude: float, latitude: float, session: AsyncSession):
        query = select(UserDetails).filter_by(user_id=user_id)
        result = await session.execute(query)
        existing_user = result.scalars().first()

        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Обновление только геолокации
        geolocation = WKTElement(f'POINT({longitude} {latitude})', srid=4326)
        existing_user.geolocation = geolocation

        await session.commit()
        await session.refresh(existing_user)
        return existing_user 

    # @staticmethod
    # async def find_nearby_accounts(latitude: float, longitude: float, session: AsyncSession):
    #     # Преобразуем целевые координаты в географическую точку
    #     target_point = func.ST_SetSRID(
    #         func.ST_MakePoint(longitude, latitude),
    #         4326  # SRID 4326 соответствует WGS 84 (стандарт для географических данных)
    #     )
    #
    #     # Выполняем запрос к базе данных
    #     query = select(UserDetails).filter(
    #         func.ST_DWithin(
    #             func.ST_SetSRID(
    #                 func.ST_MakePoint(
    #                     func.cast(UserDetails.location['longitude'], Geography),
    #                     func.cast(UserDetails.location['latitude'], Geography)
    #                 ),
    #                 4326
    #             ),
    #             target_point,
    #             2000  # Расстояние в метрах (2 км)
    #         )
    #     )
    #
    #     result = await session.execute(query)
    #     user_accounts = result.scalars().all()
    #
    #     return user_accounts

    # @staticmethod
    # async def get_users_within_radius(user_id: int, session: AsyncSession):
    #     try:
    #         # Найти текущего пользователя
    #         user_query = select(UserDetails).filter_by(user_id=user_id)
    #         user_result = await session.execute(user_query)
    #         existing_user = user_result.scalars().first()
    #
    #         if not existing_user or not existing_user.geolocation:
    #             raise HTTPException(status_code=404, detail="User not found or geolocation not set")
    #
    #         # Получаем геолокацию текущего пользователя
    #         user_geolocation = existing_user.geolocation
    #         print(f"{user_geolocation=}")
    #
    #         # Радиус в метрах (10 км)
    #         radius_in_meters = 20 * 1000
    #
    #         # Выполняем запрос для поиска пользователей в радиусе, исключая текущего пользователя
    #         query = select(UserDetails).where(
    #             func.ST_DWithin(UserDetails.geolocation, user_geolocation, radius_in_meters, use_spheroid=False),
    #             UserDetails.user_id != user_id
    #         ).order_by(
    #             func.ST_Distance(UserDetails.geolocation, user_geolocation)
    #         )
    #         # print(f"{func.ST_Distance(UserDetails.geolocation, user_geolocation)=}")
    #         result = await session.execute(query)
    #         users = result.scalars().all()
    #
    #         wkb_geom_exist_user = existing_user.geolocation
    #         point_exist_user = to_shape(wkb_geom_exist_user)
    #         exist_user_geolocation = Geolocation(latitude=point_exist_user.y, longitude=point_exist_user.x)
    #         # Преобразуем геолокацию в удобный формат
    #         users_with_geolocation = []
    #         for user in users:
    #             wkb_geom = user.geolocation
    #             point = to_shape(wkb_geom)
    #             user_geolocation = Geolocation(latitude=point.y, longitude=point.x)
    #             print(f"{user_geolocation=}")
    #             user_dict = user.__dict__
    #             user_dict['geolocation'] = user_geolocation
    #             # users_with_geolocation.append(user_dict)
    #             # # Вычисляем расстояние
    #             print(f"заходит перед distance")
    #             # print(f"{existing_user.geolocation.x=}, {existing_user.geolocation.y=}")
    #             distance = calculate_distance(
    #                 exist_user_geolocation.latitude,
    #                 exist_user_geolocation.longitude,
    #                 point.y,
    #                 point.x
    #             )
    #             # print(f"{distance=}")
    #             user_dict['distance'] = distance
    #             users_with_geolocation.append(user_dict)
    #         print(f"{users_with_geolocation=}")
    #         return users_with_geolocation
    #
    #     except Exception as e:
    #         raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_users_within_radius(user_id: int, session: AsyncSession):
        try:
            user_query = select(UserDetails).filter_by(user_id=user_id)
            user_result = await session.execute(user_query)
            existing_user = user_result.scalars().first()

            if not existing_user or not existing_user.geolocation:
                raise HTTPException(status_code=404, detail="User not found or geolocation not set")
            print(f"{type(existing_user.geolocation)=} {existing_user.geolocation=}")
            user_geolocation = existing_user.geolocation
            radius_in_meters = 20 * 1000

            query = select(
                UserDetails,
                func.ST_Distance(UserDetails.geolocation, user_geolocation).label('distance')
            ).where(
                func.ST_DWithin(UserDetails.geolocation, user_geolocation, radius_in_meters, use_spheroid=False),
                UserDetails.user_id != user_id
            ).order_by('distance')

            result = await session.execute(query)
            users = result.fetchall()

            users_with_geolocation = []
            for user_row in users:
                user, distance = user_row
                wkb_geom = user.geolocation
                point = to_shape(wkb_geom)
                user_geolocation = Geolocation(latitude=point.y, longitude=point.x)
                user_dict = user.__dict__
                user_dict['geolocation'] = user_geolocation
                user_dict['distance'] = distance
                users_with_geolocation.append(user_dict)
                # Печать значения расстояния
                print(f"Distance for user {user.user_id}: {distance} meters")

            return users_with_geolocation

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_users_within_radius_with_tags(user_id: int, tags: List[str], session: AsyncSession):
        print(tags)
        try:
            # Шаг 1: Найти текущего пользователя и его геолокацию
            user_query = select(UserDetails).filter_by(user_id=user_id)
            user_result = await session.execute(user_query)
            existing_user = user_result.scalars().first()

            if not existing_user or not existing_user.geolocation:
                raise HTTPException(status_code=404, detail="User not found or geolocation not set")

            user_geolocation = existing_user.geolocation
            radius_in_meters = 20 * 1000

            # Преобразование строки тегов в массив строк
            if tags:
                # Создаем условие для фильтрации по массивам
                tags_array = tags[0].split(',')  # Преобразуем строку в список тегов
                tag_filter = text("user_details.tags && :tags")
                tag_filter_params = {'tags': tags_array}
            else:
                tag_filter = text("TRUE")  # Без фильтрации по тегам
                tag_filter_params = {}

            query = select(
                UserDetails,
                func.ST_Distance(UserDetails.geolocation, user_geolocation).label('distance')
            ).where(
                func.ST_DWithin(UserDetails.geolocation, user_geolocation, radius_in_meters, use_spheroid=False),
                UserDetails.user_id != user_id,
                tag_filter
            ).params(tag_filter_params).order_by('distance')

            result = await session.execute(query)
            users = result.fetchall()

            # Шаг 3: Обработка результатов
            users_with_geolocation = []
            for user_row in users:
                user, distance = user_row
                wkb_geom = user.geolocation
                point = to_shape(wkb_geom)
                user_geolocation = Geolocation(latitude=point.y, longitude=point.x)
                user_dict = user.__dict__
                user_dict['geolocation'] = user_geolocation
                user_dict['distance'] = distance
                users_with_geolocation.append(user_dict)
                # Печать значения расстояния
                # print(f"Distance for user {user.user_id}: {distance} meters")

            return users_with_geolocation

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))