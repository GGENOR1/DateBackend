from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.postgresql.database import Database
from app.infra.repositories.auth.base import IAuthService


@dataclass
class ORMIAuthService(IAuthService):
    database: Database

    # async def authenticate(self, telegram_id: str) -> UserORM | None:
    #     stmt = select(UserORM).where(UserORM.id == telegram_id).limit(1)
    #     async with self.database.get_read_only_session() as session:
    #         return await session.scalar(stmt)

    # async def authorize(self, user: UserORM) -> UserORM:
    #     async with self.database.get_session() as session:
    #         session.add(user)
    #     return user


  