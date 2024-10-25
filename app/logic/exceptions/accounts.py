from dataclasses import dataclass

from app.logic.exceptions.base import LogicException


@dataclass(eq=False)
class AccountNotFoundException(LogicException):
    user_id: str

    @property
    def message(self):
        return 'Пользователь не найден'
    
@dataclass(frozen=False)
class UserWithThatEmailAlreadyExistsException(LogicException):
    email: str
    @property
    def message(self):
        return 'Пользователь с такой почтой уже существует'