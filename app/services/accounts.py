from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.entities.accounts import User
from app.domain.postgresql.models.accounts import UserORM
from app.infra.repositories.accounts.accounts import IUserRepository




class IUserService(ABC):
    @abstractmethod
    async def get_or_create(self, user: User) -> User:
        pass
    @abstractmethod
    async def get_user_by_id(self, id: int) -> User:
        pass

class IFriendService(ABC):
    @abstractmethod
    async def add_friend(self, user: User, friend: User) -> None:
        pass
    
@dataclass
class ORMUserService(IUserService, IFriendService):
    repository: IUserRepository
    
    async def get_or_create(self, user: User) -> User:
        user_dto = await self.repository.get_or_create(UserORM.from_entity(user))
        return user_dto.to_entity()

    async def add_friend(self, user: User, friend: User) -> None:
        user_dto = UserORM.from_entity(user)
        friend_dto = await self.repository.get_or_create(UserORM.from_entity(friend))
        await self.repository.add_friend(user_dto, friend_dto) 
