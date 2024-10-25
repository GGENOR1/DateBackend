from dataclasses import dataclass

from app.logic.exceptions.base import LogicException


@dataclass(eq=False)
class LikeWithThatUserAlreadyExistsException(LogicException):
    user_id: str

    @property
    def message(self):
        return f'Лайк этому пользователю "{self.user_id}" уже существует.'
    
    
@dataclass(eq=False)
class LikeNotFoundException(LogicException):
    like_oid: str

    @property
    def message(self):
        return 'Лайк с таким ID не найден.'