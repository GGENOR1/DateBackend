from datetime import datetime
from fastapi import Depends, HTTPException, Request, status

import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from app.Users.servis import UsersDAO
from app.Users.utils import get_async_session
from app.config import SECRET_KEY, ALGORITHM


def get_token(request: Request):
    print("тут выполняется2")
    token = request.cookies.get('user_access_token')
    if not token:
        raise HTTPException(status_code=401)
    return token


async def get_current_user(token: str = Depends(get_token), session: AsyncSession = Depends(get_async_session)):
    print("тут выполняется")
    try:
        payload = jwt.decode(
            token, SECRET_KEY, ALGORITHM
        )
        print("тут выполняется")

    except:
        HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    expire: str = payload.get("exp")
    if (not expire) or (int(expire) < datetime.utcnow().timestamp()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user = await UsersDAO.find_by_id(user_id, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user
