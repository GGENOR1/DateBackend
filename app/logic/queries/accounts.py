from dataclasses import dataclass
from app.domain.entities.accounts import User, UserDetails
from app.infra.repositories.accounts.accounts import IUserRepository
from app.logic.exceptions.account import AccountDetailsNotFoundException, AccountNotFoundException
from app.logic.queries.base import BaseQuery, BaseQueryHandler


@dataclass(frozen=True)
class GetAccountQuery(BaseQuery):
    user_id: int

@dataclass(frozen=True)
class GetAccountDetailsQuery(BaseQuery):
    user_id: int


@dataclass(frozen=True)
class GetAccountQueryHandler(BaseQueryHandler):
    account_repository: IUserRepository
    async def handle(self, query: GetAccountQuery) -> User:
        account = await self.account_repository.get_user_by_id(user_id=query.user_id)
        if not account:
            raise AccountNotFoundException(account=query.user_id)
        
        return account
    

@dataclass(frozen=True)
class GetAccountDetailsQueryHandler(BaseQueryHandler):
    account_repository: IUserRepository
    async def handle(self, query: GetAccountDetailsQuery) -> UserDetails:
        account = await self.account_repository.get_user_details_by_id(user_id=query.user_id)
        print(f"в функции GetAccountDetailsQueryHandler получем {account=}")
        if not account:
            raise AccountDetailsNotFoundException(account=query.user_id)

        return account