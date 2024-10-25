
from typing import Container
from fastapi import APIRouter, HTTPException
from fastapi import (
    Depends,
    status,
)

from app.application.api.auth.schemas import AuthorizationResponseSchema, AuthorizationShema
from app.application.api.schemas import ErrorSchema
from app.domain.exceptions.base import ApplicationException
from app.logic.init import init_container
from app.logic.mediator.base import Mediator
from app.logic.queries.auth import GetTokenQuery, GetTokenQueryHandler

router = APIRouter(tags=['Authentication and Authorization'])

@router.post(
    '/verify_email_to_login/',
    status_code=status.HTTP_200_OK,
    description='Ручка для проверки кода и входа пользователя',
    responses={
        status.HTTP_200_OK: {'model': AuthorizationResponseSchema},
        status.HTTP_400_BAD_REQUEST: {'model': ErrorSchema},
    },
)

#TODO: если присутсвует код в моделе, то проверять и отдавать токен
# если нет, то просто отправляем код
# использовать только захешированный пароль
async def verify_email_to_login(
    schema: AuthorizationShema,
    container: Container = Depends(init_container),
) -> AuthorizationResponseSchema:
    """Ручка для проверки кода и верификации пользователя"""

    mediator: Mediator = container.resolve(Mediator)
    try:
        token = await mediator.handle_query(GetTokenQuery(code=schema.code,email=schema.email,password=schema.password))
    # mediator: Mediator = container.resolve(Mediator)
    except ApplicationException as exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'error': exception.message})

    return AuthorizationResponseSchema.from_entity(token)

    # try:
    #     chat = await mediator.handle_query(GetChatDetailQuery(chat_oid=chat_oid))
    # except ApplicationException as exception:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'error': exception.message})

    # return ChatDetailSchema.from_entity(chat)


@router.get("/TEST")
async def testFunctions():
    return "Hellow"