from fastapi import APIRouter, HTTPException
from fastapi import (
    Depends,
    status,
)
from punq import Container
from app.application.api.likes.schemas import CreateLikeRequestSchema, CreateLikeResponseSchema, LikeDetailsSchema
from app.application.api.schemas import ErrorSchema
from app.domain.exceptions.base import ApplicationException
from app.logic.commands.likes import CreateLikeCommand
from app.logic.init import init_container
from app.logic.mediator.base import Mediator
from app.logic.queries.likes import CheckLikeQuery, GetLikeDetailQuery

router = APIRouter(tags=['Likes'])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    description='Эндпоинт создает новый лайк, если такой лайк существует, возвращается 400 ошибка',
    responses={
        status.HTTP_201_CREATED: {'model': CreateLikeResponseSchema},
        status.HTTP_400_BAD_REQUEST: {'model': ErrorSchema},
    }
)
async def create_like_handler(
    id: int,
    schema: CreateLikeRequestSchema,
    container: Container = Depends(init_container),
) -> CreateLikeResponseSchema:
    """Создать новый лайк"""
    mediator: Mediator = container.resolve(Mediator)
    try:
        like, *_ = await mediator.handle_command(CreateLikeCommand(user_id=id, liked_by_user_id=schema.liked_by_user_id))
    except ApplicationException as exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'error': exception.message})

    return CreateLikeResponseSchema.from_entity(like)


@router.get(
    "/{like_oid}",
    status_code=status.HTTP_200_OK,
    description='Эндпоинт получает лайк по id, если лайка не существует, возвращается 400 ошибка',
    responses={
        status.HTTP_200_OK: {'model': LikeDetailsSchema},
        status.HTTP_400_BAD_REQUEST: {'model': ErrorSchema},
    }
)
async def get_like_handler(
    like_oid: str,
    container: Container = Depends(init_container),
) -> LikeDetailsSchema:
    """Получить лайк по id"""
    mediator: Mediator = container.resolve(Mediator)
    try:
        like = await mediator.handle_query(GetLikeDetailQuery(like_oid=like_oid))
    except ApplicationException as exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'error': exception.message})

    return LikeDetailsSchema.from_entity(like)



@router.get(
    "/{user_id}/check_like",
    status_code=status.HTTP_200_OK,
    description='Эндпоинт проверяет, имеется ли лайк между двумя пользователями, если существует, то 409',
)
async def check_like_handler(
    user_id: int,
    liked_user_id: int,
    container: Container = Depends(init_container),
):
    """Проерка лайка между двумя пользователями"""
    mediator: Mediator = container.resolve(Mediator)
    try:
        await mediator.handle_query(CheckLikeQuery(user_id, liked_user_id))
    except ApplicationException as exception:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={'error': exception.message})

   
# TODO: Создание эндпоинта, который будет получать все новые лайки пользователя 
# (в данному случае непросмотренные)