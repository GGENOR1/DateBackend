from dataclasses import dataclass
from app.logic.exceptions.base import LogicException


@dataclass(eq=False)
class UserNotFoundException(LogicException):


    @property
    def message(self):
        return 'Проверьте корректность логина/пароля'
    
@dataclass(eq=False)
class TokentCanNotTakeException(LogicException):


    @property
    def message(self):
        return 'Проверьте корректность логина/пароля'