from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from typing import Iterable

from app.domain.entities.messages import (
    Chat,
    Message,
)
from app.infra.repositories.filters.messages import GetMessagesFilters


@dataclass
class BaseChatsRepository(ABC):
    @abstractmethod
    async def check_chat_exists_by_title(self, title: str) -> bool:
        ...
    
    @abstractmethod
    async def check_chat_exists_by_users(self, first_participants: int, second_participants: int) -> bool:
        """_summary_

        Args:
            first_participants (int): ID первого участника
            second_participants (int): ID второго участника

        Returns:
            bool: false - существует чат, true - отсутсвует
        """
        ...

    @abstractmethod
    async def get_chat_by_oid(self, oid: str) -> Chat | None:
        ...

    @abstractmethod
    async def add_chat(self, chat: Chat) -> None:
        ...

    @abstractmethod
    async def get_all_chats(self, limit: int, offset: int) -> Iterable[Chat]:
        ...

    @abstractmethod
    async def get_all_chats_by_user(self, limit: int, offset: int, user_id: int) -> Iterable[Chat]:
        """Получение всех чатов пользователя

        Args:
            limit (int): _description_
            offset (int): _description_
            user_id (int): _description_

        Returns:
            Iterable[Chat]: _description_
        """
        ...

    @abstractmethod
    async def delete_chat_by_oid(self, chat_oid: str) -> None:
        ...

    @abstractmethod
    async def add_last_message_to_chat(self, chat_oid: str, message_oid: str) -> None:
        """Обновление последнего сообщения в чате

        Args:
            chat_oid (str): Oid чата
        """
        ...


    @abstractmethod
    async def add_telegram_listener(self, chat_oid: str, telegram_chat_id: str):
        ...




    # @abstractmethod
    # async def get_all_chat_listeners(self, chat_oid: str) -> Iterable[ChatListener]:
    #     ...


@dataclass
class BaseMessagesRepository(ABC):
    @abstractmethod
    async def add_message(self, message: Message) -> None:
        ...

    @abstractmethod
    async def get_messages(self, chat_oid: str, filters: GetMessagesFilters) -> tuple[Iterable[Message], int]:
        ...
    
    @abstractmethod
    async def get_message(self, chat_oid: str, message_oid: str) -> Message:
        """Получение сообщения из чата по его oid

        Args:
            chat_oid (str): oid чата
            messages_oid (str): oid чата сообщения

        Returns:
            Message: Сообщение
        """

        ...
    @abstractmethod
    async def get_count_unread_messages(self, chat_oid: str, user_id: int) -> int:
        """Получение колличество непрочтенных сообщений в чате у пользователя

        Args:
            chat_oid (str): oid чата
            user_id (int): id пользователя

        Returns:
            int: Колличество непрочтенных сообщений
        """
        ...
