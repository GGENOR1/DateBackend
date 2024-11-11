from dataclasses import dataclass

from app.domain.entities.messages import (
    Chat,
    # ChatListener,
    Message,
)
from app.domain.values.messages import (
    Text,
    Title,
)
from app.infra.repositories.messages.base import (
    BaseChatsRepository,
    BaseMessagesRepository,
)
from app.logic.commands.base import (
    BaseCommand,
    CommandHandler,
)
from app.logic.exceptions.messages import (
    ChatNotFoundException,
    ChatWithSelfUserException,
    ChatWithThatUsersAlreadyExistsException,
)


@dataclass(frozen=True)
class CreateChatCommand(BaseCommand):
    first_participants_id: int
    second_participants_id: int


@dataclass(frozen=True)
class CreateChatCommandHandler(CommandHandler[CreateChatCommand, Chat]):
    chats_repository: BaseChatsRepository

    async def handle(self, command: CreateChatCommand) -> Chat:
        if await self.chats_repository.check_chat_exists_by_users(first_participants=command.first_participants_id,
                                                                second_participants=command.second_participants_id):
            raise ChatWithThatUsersAlreadyExistsException()
        if command.first_participants_id==command.second_participants_id:
            raise ChatWithSelfUserException()
        new_chat = Chat.create_chat(first_participant=command.first_participants_id, 
                                    second_participant=command.second_participants_id)
        
        print(f'Новый чат при вызове ивента  = {new_chat=}')
        # TODO: считать ивенты
        await self.chats_repository.add_chat(new_chat)
        # print(f"хз что ту выводится но пробуем {new_chat.pull_events()}")
        # TODO: посмототреть что тут и сделать
        await self._mediator.publish(new_chat.pull_events())

        return new_chat


@dataclass(frozen=True)
class CreateMessageCommand(BaseCommand):
    text: str
    chat_oid: str
    sender_id: int
    recipient_id: int


@dataclass(frozen=True)
class CreateMessageCommandHandler(CommandHandler[CreateMessageCommand, Chat]):
    message_repository: BaseMessagesRepository
    chats_repository: BaseChatsRepository

    async def handle(self, command: CreateMessageCommand) -> Message:
        chat = await self.chats_repository.get_chat_by_oid(oid=command.chat_oid)
        
        if not chat:
            raise ChatNotFoundException(chat_oid=command.chat_oid)
        print(f'Чат в хендлере {type(chat.participants)}')
        message = Message(text=Text(value=command.text), chat_oid=command.chat_oid,
                          sender_id=command.sender_id, recipient_id=command.recipient_id)
        chat.add_message(message)
        await self.message_repository.add_message(message=message)
        # Когда приходит новое сообщение, нужно:
        # - Обновлять состояние поля last_message в самом чате
        # - Уведомлять об этом пользователя (отображать)
        await self.chats_repository.add_last_message_to_chat(chat_oid=command.chat_oid, message_oid=message.oid)


        #TODO: РАзобраться и сделать

        await self._mediator.publish(chat.pull_events())

        return message


@dataclass(frozen=True)
class DeleteChatCommand(BaseCommand):
    user_id: int
    chat_oid: str


@dataclass(frozen=True)
class DeleteChatCommandHandler(CommandHandler[DeleteChatCommand, None]):
    chats_repository: BaseChatsRepository
    messages_repository: BaseMessagesRepository

    async def handle(self, command: DeleteChatCommand) -> None:
        chat = await self.chats_repository.get_chat_by_oid(oid=command.chat_oid)

        if not chat:
            raise ChatNotFoundException(chat_oid=command.chat_oid)

        print(f"Чат при удалении только у пользователя {chat=}")
        
        
        print(f"Чат при удалении только у пользователя после изменения флага {chat=}")
        chat.delete(command.user_id)
        print(f"Чат при удалении только у пользователя после изменения флага {chat=}")
        print(f"Пользователи {chat.participants=}")
        
        await self.chats_repository.delete_chat_by_oid(chat=chat)
        await self.messages_repository.delete_all_message_by_user(chat_oid=command.chat_oid, user_id=command.user_id)
        #TODO: Посмотреть что отдает и разобраться почему веб сокет отдает ошибку отправки
        # await self.messages_repository.delete
        # await self._mediator.publish(chat.pull_events())


@dataclass(frozen=True)
class AddTelegramListenerCommand(BaseCommand):
    chat_oid: str
    telegram_chat_id: str


# @dataclass(frozen=True)
# class AddTelegramListenerCommandHandler(CommandHandler[AddTelegramListenerCommand, ChatListener]):
#     chats_repository: BaseChatsRepository

#     async def handle(self, command: AddTelegramListenerCommand) -> ChatListener:
#         chat = await self.chats_repository.get_chat_by_oid(oid=command.chat_oid)

#         if not chat:
#             raise ChatNotFoundException(chat_oid=command.chat_oid)

#         listener = ChatListener(oid=command.telegram_chat_id)
#         chat.add_listener(listener)

#         await self.chats_repository.add_telegram_listener(
#             chat_oid=command.chat_oid,
#             telegram_chat_id=command.telegram_chat_id,
#         )
#         await self._mediator.publish(chat.pull_events())

#         return listener
