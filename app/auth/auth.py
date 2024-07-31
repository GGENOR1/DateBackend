from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
import jwt
from starlette.requests import Request

from app.Redis.servise import get_from_cache
from app.Users.servis import UsersDAO
from app.Users.utils import get_async_session
from app.auth.servis import RegisterDAO
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import SECRET_KEY, ALGORITHM

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class CustomHTTPBearer(HTTPBearer):
    async def __call__(
            self, request: Request, session: AsyncSession = Depends(get_async_session)
    ) -> Optional[HTTPAuthorizationCredentials]:
        res = await super().__call__(request)
        try:
            print("Wdawdawdwadwad")
            payload = jwt.decode(res.credentials, SECRET_KEY, algorithms=["HS256"])

            user = await UsersDAO.find_by_id(int(payload["sub"]), session)
            request.state.user = user
            print(user.id)
            print(f"Состояние пользователя {request.state.user}")
            #
            # # Проверяем доступ к end-point
            # roles = await UsersDAO.get_user_roles(int(payload["sub"]), session)
            # print(f" Текущая роль пользоваителя: {roles}")
            # print(self.has_required_role(roles.name))
            # if not self.has_required_role(roles.name):
            #     raise HTTPException(403, "Insufficient permissions")
            print()
            return payload
        except jwt.ExpiredSignatureError:
            print("Ошибка 1")
            raise HTTPException(401, "Token is expired")
        except jwt.InvalidTokenError:
            print("Ошибка 2")
            raise HTTPException(401, "Token invalid")



# def check_user_role(required_role: list = None):
#     async def _check_user_role(bearer_token: HTTPBearer = Depends(CustomHTTPBearer()),session: AsyncSession = Depends(get_async_session)):
#         print(bearer_token)
#         try:
#             roles = await UsersDAO.get_user_roles(bearer_token["sub"], session)  # Получение ролей пользователя
#             print(roles)
#             if roles.name in required_role:
#                 return True
#             elif not required_role:
#                 raise HTTPException(status_code=403, detail="permissions not allowed")
#
#             raise HTTPException(status_code=403, detail="Insufficient permissions")
#
#         except jwt.ExpiredSignatureError:
#             raise HTTPException(status_code=401, detail="Token is expired")
#
#         except jwt.InvalidTokenError:
#             raise HTTPException(status_code=401, detail="Invalid token")
#
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=str(e))
#
#     return _check_user_role


def check_user_role(required_role: list = None):
    async def _check_user_role(
            bearer_token: HTTPBearer = Depends(CustomHTTPBearer()),
            session: AsyncSession = Depends(get_async_session)
    ):
        try:
            print(f"bearer_token равен {bearer_token}")
            # Bearer token validation
            if not bearer_token or "sub" not in bearer_token:
                raise HTTPException(status_code=401, detail="Invalid token")

            roles = await UsersDAO.get_user_roles(bearer_token["sub"], session)  # Получение ролей пользователя
            print(roles)

            if not required_role:
                raise HTTPException(status_code=403, detail="Permissions not allowed")

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

# async def check_user_role(required_roles: list):
#     # bearer_token: HTTPBearer = Depends(CustomHTTPBearer())
#     print("Тут вызывается в required_roles")
#     # try:
#     #
#     #     payload = jwt.decode(bearer_token.credentials, SECRET_KEY, algorithms=["HS256"])
#     #     roles = await UsersDAO.get_user_roles(int(payload["sub"]))  # Получение ролей пользователя
#     #     # user_roles = [role.name for role in roles]
#     #     #
#     #     # for role in required_roles:
#     #     #     if role in user_roles:
#     #     #         return True
#     #
#     #     raise HTTPException(status_code=403, detail="Insufficient permissions")
#     #
#     # except jwt.ExpiredSignatureError:
#     #     raise HTTPException(status_code=401, detail="Token is expired")
#     #
#     # except jwt.InvalidTokenError:
#     #     raise HTTPException(status_code=401, detail="Invalid token")
#     #
#     # except Exception as e:
#     #     raise HTTPException(status_code=500, detail=str(e))
#     return False

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hased_password) -> bool:
    return pwd_context.verify(plain_password, hased_password)


# def has_required_role(roles: dict):
#     required_roles = ["admin", "editor", "test"]
#     user_roles = [role.name for role in roles]
#     return any(role in user_roles for role in required_roles)


# def create_access_token(data: dict) -> str:
#     to_encode = data.copy()
#     expire = datetime.utcnow() + timedelta(minutes=30)
#     to_encode.update({"exp": expire})
#     encode_jwt = jwt.encode(
#         to_encode, SECRET_KEY, ALGORITHM
#     )
#     print(encode_jwt)
#     return encode_jwt

def create_access_token(user):
    print(user)
    try:
        payload = {"sub": user.id, "exp": datetime.utcnow() + timedelta(minutes=1000)}
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    except Exception as e:
        raise e


async def authenticate_user(email: str, password: str, session: AsyncSession):
    print(f"Authenticating{email}, password: {password}")
    user = await RegisterDAO.check_email(session, email=email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


async def verify_confirmation_code(email: str, confirmation_code_user: int) -> bool:
    status_key_redis = await get_from_cache(email)
    print(f"Verifying confirmation code in Redis {status_key_redis} ")
    if not status_key_redis:
        return False
    if int(confirmation_code_user) == int(status_key_redis):
        return True
