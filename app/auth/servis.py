from bisect import insort
from sqlite3 import IntegrityError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession 
from app.Users.models import Users
from sqlalchemy import select

from app.Users.schema import UserAddSchema

class RegisterDAO():
    
    # Проверка на наличие email пользователя
    @classmethod
    async def check_email(cls, session: AsyncSession, **filter_by):
        print(f"Filter parameters: {filter_by}")
        query = select(Users).filter_by(**filter_by)
        result = await session.execute(query)
    
        return result.scalars().first()
    

    # Добавление нового пользователя
    @classmethod
    async def add_user(cls, user_data: dict, session: AsyncSession):
        try:
            UserAddSchema(**user_data)
        except ValidationError as e:
            print(f"Invalid user data: {e}")
            return None  
        query = insort(Users).values(**user_data)
        try:
            result = await session.execute(query)
            await session.commit()  
            inserted_primary_key = result.inserted_primary_key
            return inserted_primary_key
        except IntegrityError as e:
            await session.rollback() 
            print(f"Error occurred while adding user: {e}")
            return None



