from dataclasses import dataclass

from app.domain.entities.likes import Like
from app.infra.repositories.likes.base import BaseLikesRepository
from app.logic.commands.base import BaseCommand, CommandHandler
from app.logic.exceptions.likes import LikeWithThatUserAlreadyExistsException


@dataclass(frozen=True)
class CreateLikeCommand(BaseCommand):
    user_id: int
    liked_by_user_id: int

@dataclass(frozen=True)
class CreateLikeCommandHandler(CommandHandler[CreateLikeCommand, Like]):
    likes_repository: BaseLikesRepository

    async def handle(self, command: CreateLikeCommand) -> Like:
        if await self.likes_repository.check_like_exists_by_id(user_id=command.user_id, 
                                                               liked_by_user_id=command.liked_by_user_id):
            raise LikeWithThatUserAlreadyExistsException(command.liked_by_user_id)


        new_like = Like.create_like(user_id=command.user_id, liked_by_user_id=command.liked_by_user_id)
        print(f'{new_like=}')
        # TODO: считать ивенты

        await self.likes_repository.add_like(new_like)

        # TODO: Реализовать публикацию для отправки уведомлений о новом лайке
        
        # await self._mediator.publish(new_chat.pull_events())

        return new_like