from fastapi import APIRouter, HTTPException
from fastapi import (
    Depends,
    status,
)

from app.application.api.matches.schemas import CreateMatchRequestSchema, CreateMatchResponseSchema
from app.application.api.schemas import ErrorSchema
from app.domain.exceptions.base import ApplicationException
from app.logic.commands.matches import CreateMatchCommand
from app.logic.init import init_container
from app.logic.mediator.base import Mediator
from punq import Container


router = APIRouter(tags=['Matches'])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    description='Эндпоинт создает новый мэтч, если такой мэтч существует, возвращается 400 ошибка',
    responses={
        status.HTTP_201_CREATED: {'model': CreateMatchResponseSchema},
        status.HTTP_400_BAD_REQUEST: {'model': ErrorSchema},
    }
)
async def create_match_handler(
    id: int,
    schema: CreateMatchRequestSchema,
    container: Container = Depends(init_container),
) -> CreateMatchResponseSchema:
    """Создать новый мэтч"""
    mediator: Mediator = container.resolve(Mediator)
    try:
        match, *_ = await mediator.handle_command(CreateMatchCommand(user_id=id, liked_by_user_id=schema.liked_by_user_id))
    except ApplicationException as exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'error': exception.message})

    return CreateMatchResponseSchema.from_entity(match)



# @router.get(
#     "/{match_oid}",
#     status_code=status.HTTP_200_OK,
#     description='Эндпоинт получает мэтч по id, если лайка не существует, возвращается 400 ошибка',
#     responses={
#         status.HTTP_200_OK: {'model': LikeDetailsSchema},
#         status.HTTP_400_BAD_REQUEST: {'model': ErrorSchema},
#     }
# )
# async def get_like_handler(
#     like_oid: str,
#     container: Container = Depends(init_container),
# ) -> LikeDetailsSchema:
#     """Получить лайк по id"""
#     mediator: Mediator = container.resolve(Mediator)
#     try:
#         like = await mediator.handle_query(GetLikeDetailQuery(like_oid=like_oid))
#     except ApplicationException as exception:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'error': exception.message})

#     return LikeDetailsSchema.from_entity(like)
