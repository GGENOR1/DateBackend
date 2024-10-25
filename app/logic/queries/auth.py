from dataclasses import dataclass

from pydantic import EmailStr

from app.infra.repositories.accounts.accounts import IUserRepository
from app.infra.security.base import IPasswordHasher
from app.logic.exceptions.auth import TokentCanNotTakeException, UserNotFoundException
from app.logic.queries.base import BaseQuery


@dataclass(frozen=True)
class GetTokenQuery(BaseQuery):
    code: int
    email: EmailStr
    password: str


@dataclass(frozen=True)
#TODO: 
# Указать тип возвращаемых данных
# Добавить исключенния 
class GetTokenQueryHandler(BaseQuery):
     account_repository: IUserRepository
     security_repository: IPasswordHasher

     async def handle(self, query: GetTokenQuery) -> str:
        user = await self.account_repository.check_user_email(email=query.email)
        print(f"В GetTokenQueryHandler выводит {user=} ")
        if not user:
              raise UserNotFoundException()
        if not self.security_repository.verify_password(query.password, user.password):
             raise UserNotFoundException()
            
        token = self.security_repository.create_access_token(user.id)
        print(f"TOKEN : {token}")
        if not token:
             raise TokentCanNotTakeException()
        return token

        
