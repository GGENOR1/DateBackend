from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from sqlalchemy import String, select

from app.domain.postgresql.database import Database
from app.domain.postgresql.models.accounts import RolesORM, UserDetailsORM, UserORM



class IUserRepository(ABC):
    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> UserORM | None:
        """Получение данных об аккаунте пользователя
        
        :params user_id: id пользователя
        :return user: UserORM
        
        """
        pass

    @abstractmethod
    async def delete_user_by_id(self, user_id: int) ->  None:
        """ Удаление аккаунта пользователя
        
        :params user_id: id пользователя
        :return user: None
        
        """
        pass
    
    @abstractmethod
    async def get_user_details_by_id(self, user_id: int) -> UserDetailsORM | None:
        """Получение подробных данных об аккаунте пользователя
        
        :params user_id: id пользователя
        :return user: UserDetailsORM
        
        """
        pass
    
    @abstractmethod
    async def update_user_details(self, user_id: int, user: UserDetailsORM) -> UserDetailsORM | None:
        """Обновление подробных данных об аккаунте пользователя
        
        :params user_id: id пользователя
        :params user: UserDetailsORM

        :return user: UserDetailsORM
        
        """
        pass

    @abstractmethod
    async def create(self, user: UserORM) -> UserORM:
        pass

    @abstractmethod
    async def get_or_create(self, user: UserORM) -> UserORM:
        pass

    @abstractmethod
    async def add_friend(self, user: UserORM, friend: UserORM) -> None:
        pass

    @abstractmethod
    async def get_roles(self, id: str) -> None:
        pass

    @abstractmethod
    async def check_user_email(self, email: str) -> bool:
        pass



@dataclass
class ORMUserRepository(IUserRepository):
    database: Database

    async def get_user_by_id(self, user_id: str) -> UserORM | None:
        stmt = select(UserORM).where(UserORM.id == user_id).limit(1)
        async with self.database.get_read_only_session() as session:
            return await session.scalar(stmt)
    
    async def get_user_details_by_id(self, user_id: str) -> UserDetailsORM | None:
        stmt = select(UserDetailsORM).where(UserDetailsORM.user_id == user_id).limit(1)
        async with self.database.get_read_only_session() as session:
            return await session.scalar(stmt)

    # async def create(self, user: UserORM) -> UserORM:
    #     print(f"creating user {user}")
    #     async with self.database.get_session() as session:
    #         session.add(user)
    #     return user

    async def create(self, user: UserORM, account: UserDetailsORM) -> None:
        async with self.database.get_session() as session:
            async with session.begin():  # Начало транзакции
                session.add(user)
                await session.flush()
                account.user_id = user.id
                session.add(UserDetailsORM(user_id=account.user_id))
        return user
    
    async def delete_user_by_id(self, user_id: int) -> int:
        # user_db = self.get_user_by_id(user_id=user_id)
        async with self.database.get_session() as session:
            async with session.begin():  # Начало транзакции
                user = await session.get(UserORM, user_id)
                if user:
                    await session.delete(user)
                    await session.flush()
                user_details = await session.get(UserDetailsORM, user_id)
                if user_details:
                    await session.delete(user_details)
    

    async def get_or_create(self, user: UserORM) -> UserORM:
        db_user = await self.get_user_by_id(user.telegram_id)
        return db_user or await self.create(user)
    
    async def get_roles(self, id: int) -> str | None:
        query = (
        select(RolesORM)
        .select_from(UserORM)  # Явно указываем, что начинаем с UserORM
        .join(RolesORM, UserORM.role_id == RolesORM.id)  # Соединение с RolesORM
        .filter(UserORM.id == id)
        )
    
        async with self.database.get_read_only_session() as session:
            return await session.scalar(query)

    #TODO: Проверить и изменить тип возвращаемой переменной 
    async def check_user_email(self, email: str):
        query = select(UserORM).filter(UserORM.email == email).limit(1)
        async with self.database.get_read_only_session() as session:
            return await session.scalar(query)
    
    async def update_user_details(self, user_id: int, user: UserDetailsORM) -> UserDetailsORM:
        async with self.database.get_session() as session:
            user_fields = {column.name: getattr(user, column.name) for column in user.__table__.columns}
            session.add(user)  # Применяем изменения к существующей записи
        
        return user

    async def add_friend(self, user: UserORM, friend: UserORM) -> None:
        async with self.database.get_session() as session:
            session.add(RolesORM(user_oid=user.oid, friend_oid=friend.oid, name=friend.username))
            session.add(RolesORM(user_oid=friend.oid, friend_oid=user.oid, name=user.username))
