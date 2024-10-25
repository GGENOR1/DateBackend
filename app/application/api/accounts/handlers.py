
from typing import Container
from fastapi import APIRouter, HTTPException, Request

from fastapi import (
    Depends,
    status,
)
from fastapi.security import OAuth2PasswordBearer


from app.application.api.accounts.schemas import AccountDetailsSchema, AccountSchema, CreateUserRequestSchema, CreateUserResponseSchema, DeleteUserResponseSchema, UpdateAccountDetailsRequestSchema, UpdateAccountDetailsResponseSchema
from app.application.api.schemas import ErrorSchema
from app.domain.exceptions.base import ApplicationException
from app.infra.auth.auth import check_user_role
from app.infra.repositories.accounts.accounts import IUserRepository
from app.logic.commands.account import CreateUserCommand, DeleteUserCommand, UpdateUserDetailsCommand
from app.logic.init import init_container
from app.logic.mediator.base import Mediator
from app.logic.queries.accounts import GetAccountDetailsQuery, GetAccountQuery





router = APIRouter(tags=['Account'])

@router.get(
    '/{id}/',
    status_code=status.HTTP_200_OK,
    description='Тестовая херня для postgres',
    responses={
        status.HTTP_200_OK: {'model': AccountSchema},
        status.HTTP_400_BAD_REQUEST: {'model': ErrorSchema},
    },
)
async def get_user(
    id: int,
    container: Container = Depends(init_container),
):
    mediator: Mediator = container.resolve(Mediator)
    try:
        user = await mediator.handle_query(GetAccountQuery(user_id=id))
    except ApplicationException as exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'error': exception.message})

    print(f"{user}")
    return AccountSchema.from_entity(user)

# @router.get(
#     '/user/{id}/',
#     status_code=status.HTTP_200_OK,
#     description='Получение данных об аккаунте пользователя',
#     responses={
#         status.HTTP_200_OK: {'model': AccountDetailsSchema},
#         status.HTTP_400_BAD_REQUEST: {'model': ErrorSchema},
#     },
# )
# async def get_details_user(
#     id: int,
#     container: Container = Depends(init_container),
# ):
#     mediator: Mediator = container.resolve(Mediator)
#     try:
#         account = await mediator.handle_query(GetAccountDetailsQuery(id))
#     except ApplicationException as exception:
#          raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'error': exception.message})

#     return AccountDetailsSchema.from_entity(account)

@router.get(
    '/',
    dependencies=[Depends(check_user_role(["admin", "user"]))],
    status_code=status.HTTP_200_OK,
    description='Получение данных об аккаунте пользователя',
    responses={
        status.HTTP_200_OK: {'model': AccountDetailsSchema},
        status.HTTP_400_BAD_REQUEST: {'model': ErrorSchema},
    },
)
async def get_details_user(
    request: Request,
    container: Container = Depends(init_container),
):
    
    mediator: Mediator = container.resolve(Mediator)
    try:
        account = await mediator.handle_query(GetAccountDetailsQuery(request.state.user.id))
    except ApplicationException as exception:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'error': exception.message})

    return AccountDetailsSchema.from_entity(account)

# @router.get(
#     '/id',
#     dependencies=[Depends(check_user_role(["admin", "user"]))],
#     status_code=status.HTTP_200_OK,
#     description='Получение id пользователя',
#     responses={
#         status.HTTP_200_OK: {'model': IDUserSchema},
#         status.HTTP_400_BAD_REQUEST: {'model': ErrorSchema},
#     },
#     summary="Получение id пользователя"
# )
# async def get_id_user(
#     request: Request,
#     container: Container = Depends(init_container),
# ):
#     return request.state.user.id

@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    description='Ручка на создание нового пользователя, если пользователь существует, то 400 ошибка',
    responses={
        status.HTTP_201_CREATED: {'model': CreateUserResponseSchema},
        status.HTTP_400_BAD_REQUEST: {'model': ErrorSchema},
    },
) 
async def create_user_handler(
    schema: CreateUserRequestSchema,
    container: Container = Depends(init_container),
):
    """Создание нового пользователя"""
    mediator: Mediator = container.resolve(Mediator)
    try:
        user, *_ = await mediator.handle_command(CreateUserCommand(email=schema.email,
                                                                   password=schema.password, 
                                                                   username=schema.username))
    except ApplicationException as exception:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'error': exception.message})

    
    return CreateUserResponseSchema.from_entity(user)


@router.delete(
    '/{id}',
    status_code=status.HTTP_204_NO_CONTENT,
    description='Ручка на удаление пользователя, если пользователя не существует, то 400 ошибка',
) 
async def delete_user_handler(
    id: int,
    container: Container = Depends(init_container),
):
    """Удаление аккаунта"""
    mediator: Mediator = container.resolve(Mediator)
    try:
        await mediator.handle_command(DeleteUserCommand(user_id=id))
    except ApplicationException as exception:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'error': exception.message})


@router.patch(
    '/',
    dependencies=[Depends(check_user_role(["admin", "user"]))],
    status_code=status.HTTP_200_OK,
    description='Ручка для обновления данных аккаунта пользователя',
        responses={
        status.HTTP_200_OK: {'model': AccountDetailsSchema},
        status.HTTP_400_BAD_REQUEST: {'model': ErrorSchema},
    },
) 
async def update_user_handler(
    request: Request,
    schema: UpdateAccountDetailsRequestSchema,
    container: Container = Depends(init_container),
):
    """Обновление параметров пользователя. Обновляет только переданные поля"""
    mediator: Mediator = container.resolve(Mediator)
    updated_fields = {key: value for key, value in schema.dict().items() if key is not None and value is not None}
    print(updated_fields)
    try:
        user_details, *_ = await mediator.handle_command(UpdateUserDetailsCommand(user_id=request.state.user.id, **updated_fields))
    except ApplicationException as exception:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'error': exception.message})
    return AccountDetailsSchema.from_entity(user_details)

