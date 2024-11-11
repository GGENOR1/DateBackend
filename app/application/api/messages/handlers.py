from fastapi import (
    Depends,
    Request,
    status,
)
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter

from fastapi.security import OAuth2PasswordBearer
from punq import Container

from app.application.api.messages.filters import (
    GetAllChatsFilters,
    GetMessagesFilters,
)
from app.application.api.messages.schemas import (
    # AddTelegramListenerResponseSchema,
    AddTelegramListenerSchema,
    ChatDetailSchema,
    # ChatListenerListItemSchema,
    CreateChatRequestSchema,
    CreateChatResponseSchema,
    CreateMessageResponseSchema,
    CreateMessageSchema,
    GetAllChatsQueryResponseSchema,
    GetMessagesQueryResponseSchema,
    MessageDetailSchema,
)
from app.application.api.schemas import ErrorSchema
from app.domain.exceptions.base import ApplicationException
from app.infra.auth.auth import check_user_role
from app.infra.repositories.accounts.accounts import IUserRepository
from app.logic.commands.messages import (
    AddTelegramListenerCommand,
    CreateChatCommand,
    CreateMessageCommand,
    DeleteChatCommand,
)
from app.logic.init import init_container
from app.logic.mediator.base import Mediator
from app.logic.queries.messages import (
    GetAllChatsListenersQuery,
    GetAllChatsQuery,
    GetChatDetailQuery,
    GetMessagesQuery,
)
from app.services.accounts import IUserService





router = APIRouter(tags=['Chat'])


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    description='Эндпоинт создаёт новый чат, если чат между двумя пользователям сущесествет, то возвращается 400 ошибка',
    responses={
        status.HTTP_201_CREATED: {'model': CreateChatResponseSchema},
        status.HTTP_400_BAD_REQUEST: {'model': ErrorSchema},
    },
    summary='Создание нового чата между пользователями'
)
async def create_chat_handler(
    schema: CreateChatRequestSchema,
    container: Container = Depends(init_container),
) -> CreateChatResponseSchema:
    """Создать новый чат."""
    mediator: Mediator = container.resolve(Mediator)

    try:
        chat, *_ = await mediator.handle_command(CreateChatCommand(first_participants_id=schema.first_participants_id,
                                                                   second_participants_id=schema.second_participants_id))
    except ApplicationException as exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'error': exception.message})

    return CreateChatResponseSchema.from_entity(chat)


@router.post(
    '/{chat_oid}/messages',
    status_code=status.HTTP_201_CREATED,
    description='Ручка на добавление нового сообщения в чат с переданным ObjectID',
    responses={
        status.HTTP_201_CREATED: {'model': CreateMessageSchema},
        status.HTTP_400_BAD_REQUEST: {'model': ErrorSchema},
    },
    summary='Ручка на добавление нового сообщения в чат'
)
async def create_message_handler(
    chat_oid: str,
    schema: CreateMessageSchema,
    container: Container = Depends(init_container),
) -> CreateMessageResponseSchema:
    """Добавить новое сообщение в чат."""
    mediator: Mediator = container.resolve(Mediator)

    try:
        message, *_ = await mediator.handle_command(CreateMessageCommand(text=schema.text, chat_oid=chat_oid, 
                                                                         recipient_id=schema.recipient_id, sender_id=schema.sender_id))
    except ApplicationException as exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'error': exception.message})

    return CreateMessageResponseSchema.from_entity(message)


@router.get(
    '/{chat_oid}/',
    status_code=status.HTTP_200_OK,
    description='Получить информацию о чате ',
    responses={
        status.HTTP_200_OK: {'model': ChatDetailSchema},
        status.HTTP_400_BAD_REQUEST: {'model': ErrorSchema},
    },
    dependencies=[Depends(check_user_role(["admin", "user"]))],
    summary="Получить информацию о чате"
)
async def get_chat_with_messages_handler(
    chat_oid: str,
    request: Request,
    container: Container = Depends(init_container),
) -> ChatDetailSchema:
    mediator: Mediator = container.resolve(Mediator)

    try:
        chat, count = await mediator.handle_query(GetChatDetailQuery(chat_oid=chat_oid, user_id=request.state.user.id))
        print(f"В get_chat_with_messages_handler {chat=}")
        print(f"Получение колличтесва сообщений в хендлере {count}")
    except ApplicationException as exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'error': exception.message})

    return ChatDetailSchema.from_entity_details(chat, count)


@router.get(
    '/{chat_oid}/messages/',
    status_code=status.HTTP_200_OK,
    description='Все отправленные сообщения в чате',
    responses={
        status.HTTP_200_OK: {'model': GetMessagesQueryResponseSchema},
        status.HTTP_400_BAD_REQUEST: {'model': ErrorSchema},
    },
)
async def get_chat_messages_handler(
    chat_oid: str,
    filters: GetMessagesFilters = Depends(),
    container: Container = Depends(init_container),
) -> GetMessagesQueryResponseSchema:
    mediator: Mediator = container.resolve(Mediator)

    try:
        messages, count = await mediator.handle_query(
            GetMessagesQuery(chat_oid=chat_oid, filters=filters.to_infra()),
        )
    except ApplicationException as exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'error': exception.message})

    return GetMessagesQueryResponseSchema(
        count=count,
        limit=filters.limit,
        offset=filters.offset,
        items=[MessageDetailSchema.from_entity(message) for message in messages],
    )

# TODO: 1) Проверять удален ли чат и отдавать
@router.get(
    '/',
    dependencies=[Depends(check_user_role(["admin", "user"]))],
    status_code=status.HTTP_200_OK,
    description='Получить все существющие чаты на данный момент',
    responses={
        status.HTTP_200_OK: {'model': GetAllChatsQueryResponseSchema},
        status.HTTP_400_BAD_REQUEST: {'model': ErrorSchema},
    },
    summary='Получить список всех чатов пользователя',
)
async def get_all_chats_by_user_handler(
    request: Request,
    filters: GetAllChatsFilters = Depends(),
    container: Container = Depends(init_container),
) -> GetAllChatsQueryResponseSchema:
    mediator: Mediator = container.resolve(Mediator)
    print(request.state.user.id)
    try:
        chats, count = await mediator.handle_query(
            GetAllChatsQuery(filters=filters.to_infra(), user_id=request.state.user.id),
        )
        
    except ApplicationException as exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'error': exception.message})

    return GetAllChatsQueryResponseSchema(
        count=count,
        limit=filters.limit,
        offset=filters.offset,
        items=[ChatDetailSchema.convert_dict_to_chat(chat) for chat in chats],
    )


# @router.get(
#     '/{chat_oid}/listeners/',
#     status_code=status.HTTP_200_OK,
#     description='Получить всех слушателей из ТП в конкретном чате.',
#     responses={
#         status.HTTP_200_OK: {'model': list[ChatListenerListItemSchema]},
#         status.HTTP_400_BAD_REQUEST: {'model': ErrorSchema},
#     },
#     summary='Получить список всех слушателей в ТП',
#     operation_id='getAllChatListeners',
# )
# async def get_all_chat_listeners_handler(
#     chat_oid: str,
#     container: Container = Depends(init_container),
# ) -> list[ChatListenerListItemSchema]:
#     mediator: Mediator = container.resolve(Mediator)

#     try:
#         chat_listeners = await mediator.handle_query(GetAllChatsListenersQuery(chat_oid=chat_oid))
#     except ApplicationException as exception:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'error': exception.message})

#     return [ChatListenerListItemSchema.from_entity(chat_listener=chat_listener) for chat_listener in chat_listeners]


@router.delete(
    '/{chat_oid}/',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Удаляет чат только у текущего пользователя',
    description='Удаляет чат только у текущего пользователя на основе "chat_oid"',
    dependencies=[Depends(check_user_role(["admin", "user"]))],
)
async def delete_chat_handler(
    request: Request,
    chat_oid: str,
    container: Container = Depends(init_container),
) -> None:
    mediator: Mediator = container.resolve(Mediator)

    try:
        await mediator.handle_command(DeleteChatCommand(chat_oid=chat_oid, user_id=request.state.user.id))
    except ApplicationException as exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'error': exception.message})

@router.delete(
    '/{chat_oid}/all',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Удаляет чат у обоих пользователей',
    description='Удаляет чат только у обоих пользователей на основе "chat_oid"',
    dependencies=[Depends(check_user_role(["admin", "user"]))],
)
async def delete_chat__all_handler(
    chat_oid: str,
    container: Container = Depends(init_container),

) -> None:
    mediator: Mediator = container.resolve(Mediator)

    try:
        await mediator.handle_command(DeleteChatCommand(chat_oid=chat_oid))
    except ApplicationException as exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'error': exception.message})


# @router.post(
#     '/{chat_oid}/listeners/',
#     status_code=status.HTTP_201_CREATED,
#     summary='Add telegram tech support listener to chat',
#     description='Add telegram tech support listener to chat',
#     operation_id='addTelegramListenerToChat',
#     response_model=AddTelegramListenerResponseSchema,
# )
# async def add_chat_listener_handler(
#     chat_oid: str,
#     schema: AddTelegramListenerSchema,
#     container: Container = Depends(init_container),
# ) -> AddTelegramListenerResponseSchema:
#     mediator: Mediator = container.resolve(Mediator)

#     try:
#         listener, *_ = await mediator.handle_command(
#             AddTelegramListenerCommand(
#                 chat_oid=chat_oid,
#                 telegram_chat_id=schema.telegram_chat_id,
#             ),
#         )
#     except ApplicationException as exception:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'error': exception.message})

#     return AddTelegramListenerResponseSchema.from_entity(listener)
