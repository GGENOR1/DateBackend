from dataclasses import asdict, dataclass
from typing import List, Optional

from pydantic import EmailStr

from app.domain.entities.accounts import User, UserDetails
from app.domain.postgresql.models.accounts import UserDetailsORM, UserORM
from app.infra.repositories.accounts.accounts import IUserRepository
from app.infra.security.base import IPasswordHasher
from app.logic.commands.base import BaseCommand, CommandHandler
from app.logic.exceptions.accounts import AccountNotFoundException, UserWithThatEmailAlreadyExistsException


@dataclass(frozen=True)
class CreateUserCommand(BaseCommand):
    email: EmailStr
    password: str
    username: str



@dataclass(frozen=True)
class CreateUserCommandHandler(CommandHandler[CreateUserCommand, User]):
    user_repository: IUserRepository
    security_repository: IPasswordHasher
    async def handle(self, command: CreateUserCommand) -> User:
        if await self.user_repository.check_user_email(email=command.email):
            raise UserWithThatEmailAlreadyExistsException(command.email)
        
        # TODO: вот так по примеру добавть валидацию пароля и почты
        # title = Title(value=command.title)
        
        print(f'{command.email=}, {command.password=}, {command.username=}')
        new_user = User.create_user(email=command.email,
                                    password=self.security_repository.get_password_hash(password=command.password), 
                                    username=command.username)
        new_user_orm = UserORM.from_entity(new_user)
        # TODO: считать ивенты
        print(f'{new_user=}')
        print(f'{new_user_orm=}')
        await self.user_repository.create(new_user_orm, new_user_orm)
        # await self._mediator.publish(new_chat.pull_events())

        return new_user_orm
    


@dataclass(frozen=True)
class DeleteUserCommand(BaseCommand):
    user_id: int


@dataclass(frozen=True)
class DeleteUserCommandHandler(CommandHandler[DeleteUserCommand, None]):
    user_repository: IUserRepository
    async def handle(self, command: DeleteUserCommand) -> None:
        
        user = await self.user_repository.get_user_by_id(user_id=command.user_id)
        
        if not user:
            raise AccountNotFoundException(command.user_id)
        
        # TODO: Тут как то надо подумать, если по какой то причине аккаунт есть, 
        # а в связанной его нет
        
        # TODO: Можно пделать через флаги, если пользователь удален,
        # то просто менять флаг в таблицу с ролями как удаленный, либо какой
        # либо реализовать просто в той же таблице если пользователь заблокирован

        id = await self.user_repository.delete_user_by_id(user_id=command.user_id)


        # await self.user_repository.create(new_user_orm, new_user_orm)
        # await self._mediator.publish(new_chat.pull_events())

@dataclass(frozen=True)
class UpdateUserDetailsCommand(BaseCommand):
    user_id: int
    zodiac_sign: Optional[str] = None
    height: Optional[int] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    educations: Optional[str] = None
    children: Optional[str] = None
    languages: Optional[str] = None
    alcohol: Optional[str] = None
    cigarettes: Optional[str] = None


@dataclass(frozen=True)
class UpdateUserDetailsCommandHandler(CommandHandler[UpdateUserDetailsCommand, UserDetails]):
    user_repository: IUserRepository
    async def handle(self, command: UpdateUserDetailsCommand) -> UserDetails:
        
        user = await self.user_repository.get_user_by_id(user_id=command.user_id)
        
        if not user:
            raise AccountNotFoundException(command.user_id)
        user_details = await self.user_repository.get_user_details_by_id(user_id=command.user_id)
        
        fields_to_update = {k: v for k, v in asdict(command).items() if v is not None and k != 'user_id'}
        for field, value in fields_to_update.items():
            setattr(user_details, field, value)  # Подменяем значения полей
        
        updated_user = await self.user_repository.update_user_details(user_id=command.user_id, user=user_details)
        return updated_user
        # # TODO: Тут как то надо подумать, если по какой то причине аккаунт есть, 
        # # а в связанной его нет
        
        # # TODO: Можно пделать через флаги, если пользователь удален,
        # # то просто менять флаг в таблицу с ролями как удаленный, либо какой
        # # либо реализовать просто в той же таблице если пользователь заблокирован

        # id = await self.user_repository.delete_user_by_id(user_id=command.user_id)


        # await self.user_repository.create(new_user_orm, new_user_orm)
        # await self._mediator.publish(new_chat.pull_events()) 