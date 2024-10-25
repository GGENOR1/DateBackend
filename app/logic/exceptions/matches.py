from dataclasses import dataclass

from app.logic.exceptions.base import LogicException


@dataclass(eq=False)
class MatchWithThatUsersAlreadyExistsException(LogicException):
    user_id: int
    liked_by_user_id: int

    @property
    def message(self):
        return f'Мэтч между "{self.user_id} и {self.liked_by_user_id}" уже существует.'