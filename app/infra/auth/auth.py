

from typing import Container, Optional
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from app.settings import config
from app.infra.repositories.accounts.accounts import IUserRepository
from app.logic.init import init_container
from app.settings import settings

class CustomHTTPBearer(HTTPBearer):

    # Переношу все функции в оотсветсвующий класс
    # использую контенер тут для вызова данных функций
    # куда вынести данный класс - надо разобраться 
    async def __call__(
            self, request: Request,
            container: Container = Depends(init_container)
    ) -> Optional[HTTPAuthorizationCredentials]:
        res = await super().__call__(request)
        try:

            payload = jwt.decode(res.credentials, settings.secret_key, algorithms=settings.algorithm)
            print(f"{payload=}")
            service = container.resolve(IUserRepository)
            user = await service.get_user_by_id(int(payload["sub"]))
            if user is None:
                raise HTTPException(401, "User not found")
            print(f"{user=}")
            request.state.user = user
            print(user.id)
            print(f"Состояние пользователя {request.state.user}")
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(401, "Token is expired")
        except jwt.InvalidTokenError:
            raise HTTPException(401, "Token invalid")
        


def check_user_role(required_role: list = None):
    async def _check_user_role(
            bearer_token: HTTPBearer = Depends(CustomHTTPBearer()),
            container: Container = Depends(init_container)
    ):
        try:
            print(f"bearer_token равен {bearer_token}")
            # Bearer token validation
            if not bearer_token or "sub" not in bearer_token:
                raise HTTPException(status_code=401, detail="Invalid token")
            service = container.resolve(IUserRepository)
            roles = await service.get_roles(int(bearer_token["sub"]))
        
            print(f"{roles=}")
            print(f"{required_role=}")
            if not required_role:
                raise HTTPException(status_code=403, detail="Permissions not allowed")
            print(f"{roles.name=}")
            if roles.name in required_role:
                return True

            raise HTTPException(status_code=403, detail="Insufficient permissions")

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token is expired")

        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

        except HTTPException as http_ex:
            # Re-raise HTTPExceptions with the appropriate status code
            raise http_ex

        except Exception as e:
            # For all other exceptions, raise a 500 Internal Server Error
            raise HTTPException(status_code=500, detail=str(e))

    return _check_user_role



