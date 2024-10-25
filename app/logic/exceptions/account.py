from dataclasses import dataclass

from app.logic.exceptions.base import LogicException


@dataclass(eq=False)
class AccountNotFoundException(LogicException):
    account: int

    @property
    def message(self):
        return 'Пользователь с таким ID не найден.'
    
@dataclass(eq=False)
class AccountDetailsNotFoundException(LogicException):
    account: int

    @property
    def message(self):
        return 'Подробных данных о пользователе не найдено'