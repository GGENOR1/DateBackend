from pydantic import ValidationError
from app.Users.schema import UserAddSchema
from app.Users.utils import get_async_session as session
from app.Users.models import Users, Roles
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import selectinload


class UsersDAO:

    # Поиск пользователя по ID
    @classmethod
    async def find_by_id(cls, user_id: int, session: AsyncSession):
        query = select(Users).filter_by(id=user_id)
        user = await session.execute(query)
        print(user)
        return user.scalar_one_or_none()
    
    # Получение всех польователей 
    @classmethod
    async def find_all(cls, session: AsyncSession):
        query = select(Users)
        users = await session.execute(query)
        return users.scalars().all()
    
    # Добавление нового пользователя
    @classmethod
    async def add_user(cls, user_data: dict, session: AsyncSession):
        try:
            UserAddSchema(**user_data)
        except ValidationError as e:
            print(f"Invalid user data: {e}")
            return None  
        query = insert(Users).values(**user_data)
        try:
            result = await session.execute(query)
            await session.commit()  
            inserted_primary_key = result.inserted_primary_key
            return inserted_primary_key
        except IntegrityError as e:
            await session.rollback() 
            print(f"Error occurred while adding user: {e}")
            return None  
        

    #Удаление пользователя    
    @classmethod
    async def delete_user(cls, user_id: int, session: AsyncSession):
        query = select(Users).where(Users.id == user_id)
        try:
            result = await session.execute(query)
            user = result.scalar_one()
            print(user)
            await session.delete(user)
            await session.commit()
            return user_id
        except NoResultFound:
            await session.rollback()
            return None
        
        
    #Обновление данных о пользователе 
    @classmethod
    async def update_user(cls, user_id: int, user_data: dict, session: AsyncSession):
        query = select(Users).where(Users.id == user_id)
        try:
            result = await session.execute(query)
            user = result.scalar_one()
            for field, value in user_data.items():
                if value is not None:
                    setattr(user, field, value)  
            await session.commit()
            await session.refresh(user)
            return user
        except NoResultFound:
            await session.rollback()
            return None


    @classmethod
    async def get_user_roles(cls, user_id: int, session: AsyncSession):
        query = select(Roles).join(Users, Users.role_id == Roles.id).filter(Users.id == user_id)
        result = await session.execute(query)
        print(f" Текущая результат по роли пользоваителя: {result}")
        return result.scalar_one_or_none()
