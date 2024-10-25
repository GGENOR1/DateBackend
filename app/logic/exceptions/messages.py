from dataclasses import dataclass

from app.logic.exceptions.base import LogicException


@dataclass(eq=False)
class ChatWithThatTitleAlreadyExistsException(LogicException):
    title: str

    @property
    def message(self):
        return f'Чат с таким названием "{self.title}" уже существует.'

@dataclass(eq=False)
class ChatWithThatUsersAlreadyExistsException(LogicException):

    @property
    def message(self):
        return f'Чат между данными пользователями уже существует.'
    
@dataclass(eq=False)
class ChatWithSelfUserException(LogicException):

    @property
    def message(self):
        return f'Чат с самим собой нельзя создать'
    

@dataclass(eq=False)
class ChatNotFoundException(LogicException):
    chat_oid: str

    @property
    def message(self):
        return 'Чат с таким ID не найден.'
