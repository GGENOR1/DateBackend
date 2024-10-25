from dataclasses import dataclass

from app.infra.repositories.matches.base import BaseMatchesRepository
from app.logic.commands.base import BaseCommand, CommandHandler
from app.domain.entities.matches import Match
from app.logic.exceptions.matches import MatchWithThatUsersAlreadyExistsException

@dataclass(frozen=True)
class CreateMatchCommand(BaseCommand):
    user_id: int
    liked_by_user_id: int


@dataclass(frozen=True)
class CreateMatchCommandHandler(CommandHandler[CreateMatchCommand, Match]):
    matches_repository: BaseMatchesRepository

    async def handle(self, command: CreateMatchCommand) -> Match:
        if await self.matches_repository.check_match_exists_by_id(user_id=command.user_id, 
                                                               liked_by_user_id=command.liked_by_user_id):
            raise MatchWithThatUsersAlreadyExistsException(user_id=command.user_id, liked_by_user_id=command.liked_by_user_id)


        new_match = Match.create_match(user_id=command.user_id, liked_by_user_id=command.liked_by_user_id)
        print(f'{new_match=}')
        # TODO: считать ивенты

        await self.matches_repository.add_match(new_match)

        # TODO: Реализовать публикацию для отправки уведомлений о новом лайке
        
        # await self._mediator.publish(new_chat.pull_events())

        return new_match
    

