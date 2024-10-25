from dataclasses import dataclass
from typing import Iterable, List

from app.domain.entities.messages import (
    Chat,
    # ChatListener,
    Message,
)
from app.infra.repositories.accounts.accounts import IUserRepository
from app.infra.repositories.filters.messages import (
    GetAllChatsFilters,
    GetMessagesFilters,
)
from app.infra.repositories.messages.base import (
    BaseChatsRepository,
    BaseMessagesRepository,
)
from app.logic.exceptions.messages import ChatNotFoundException
from app.logic.queries.base import (
    BaseQuery,
    BaseQueryHandler,
)


@dataclass(frozen=True)
class GetChatDetailQuery(BaseQuery):
    chat_oid: str
    user_id: int


@dataclass(frozen=True)
class GetMessagesQuery(BaseQuery):
    chat_oid: str
    filters: GetMessagesFilters


@dataclass(frozen=True)
class GetAllChatsQuery(BaseQuery):
    filters: GetAllChatsFilters
    user_id: int


@dataclass(frozen=True)
class GetAllChatsListenersQuery(BaseQuery):
    chat_oid: str


@dataclass(frozen=True)
class GetChatDetailQueryHandler(BaseQueryHandler):
    chats_repository: BaseChatsRepository
    account_repository: IUserRepository

    messages_repository: BaseMessagesRepository  # TODO: забирать сообщения отдельно

    async def handle(self, query: GetChatDetailQuery) -> Chat:
        chat = await self.chats_repository.get_chat_by_oid(oid=query.chat_oid)
        
        if not chat:
            raise ChatNotFoundException(chat_oid=query.chat_oid, )
        updated_chats = await self._enrich_chats_with_participants(chat=chat, user_id=query.user_id)
        count = await self.messages_repository.get_count_unread_messages(chat_oid=query.chat_oid, user_id=query.user_id)
        print(f"Непрочитанных сообщений пользователя {query.user_id} в чате {query.chat_oid}: {count}")
        return updated_chats, count
    
    async def _enrich_chats_with_participants(self, user_id: int, chat: Chat,) -> Chat:
        updated_participants = []
        for participant in chat.participants:
            if participant.user_id == user_id:
                    continue
            user_details = await self.account_repository.get_user_details_by_id(participant.user_id)
            enriched_participant = {
                    'user_id': participant.user_id,
                    'last_name': user_details.last_name,
                    'first_name': user_details.first_name,
            }
            updated_participants.append(enriched_participant)

        chat.participants = updated_participants
        message = await self.messages_repository.get_message(message_oid=chat.last_message )
        print(f"Получаю сообщение при получении чата {message}")
        chat.last_message = message
        return chat


@dataclass(frozen=True)
class GetMessagesQueryHandler(BaseQueryHandler):
    messages_repository: BaseMessagesRepository

    async def handle(self, query: GetMessagesQuery) -> Iterable[Message]:
        return await self.messages_repository.get_messages(
            chat_oid=query.chat_oid,
            filters=query.filters,
        )


@dataclass(frozen=True)
class GetAllChatsQueryHandler(BaseQueryHandler[GetAllChatsQuery, Iterable[Chat]]):
    chats_repository: BaseChatsRepository
    account_repository: IUserRepository
    messages_repository: BaseMessagesRepository
    async def handle(self, query: GetAllChatsQuery) -> Iterable[Chat]:  # type: ignore
        chats, count = await self.chats_repository.get_all_chats_by_user(filters=query.filters, user_id=query.user_id)
        print(f"При получении всеъх чатов в хендлере GetAllChatsQueryHandler {chats=}")
        # TODO: ЗЗдесь нужно проходится по всем участникам чата и выводить подробную инфу в поле participants
        updated_chats = await self._enrich_chats_with_participants_and_unread_count(id=query.user_id, chats=chats)
        print(f"Обновленные данные о чате получаем {updated_chats=}")

        return updated_chats, count
    
    async def _enrich_chats_with_participants_and_unread_count(self, id: int, chats: Iterable[Chat]) -> Iterable[dict]:
        enriched_chats = []
        for chat in chats:
            updated_participants = []
            for participant in chat.participants:
                if participant.user_id == id:
                    continue
                user_details = await self.account_repository.get_user_details_by_id(participant.user_id)
                enriched_participant = {
                    'user_id': participant.user_id,
                    'last_name': user_details.last_name,
                    'first_name': user_details.first_name,
                }
                updated_participants.append(enriched_participant)

            # Получаем количество непрочитанных сообщений для каждого чата
            unread_count = await self.messages_repository.get_count_unread_messages(chat_oid=chat.oid, user_id=id)
            message = await self.messages_repository.get_message(message_oid=chat.last_message )
            print(f"Получаю сообщение при получении чата {message}")
            
            # Создаем временный объект с дополнительным полем unread_messages_count
            enriched_chat = {
                'oid': chat.oid,
                "created_at": chat.created_at,
                "updated_at": chat.updated_at,
                "delete_by_first": chat.delete_by_first,
                'delete_by_second': chat.delete_by_second,
                'participants': updated_participants  ,       
                'unread_messages_count': unread_count,  # Добавляем количество непрочитанных сообщений
                'last_message': message,
            }

            enriched_chats.append(enriched_chat)
        
        return enriched_chats


# @dataclass(frozen=True)
# class GetAllChatsListenersQueryHandler(BaseQueryHandler[GetAllChatsListenersQuery, Iterable[ChatListener]]):
#     chats_repository: BaseChatsRepository

#     async def handle(self, query: GetAllChatsListenersQuery) -> ChatListener:
#         # TODO: убрать два запроса
#         chat = await self.chats_repository.get_chat_by_oid(oid=query.chat_oid)

#         if not chat:
#             raise ChatNotFoundException(chat_oid=query.chat_oid)

#         return await self.chats_repository.get_all_chat_listeners(chat_oid=query.chat_oid)
