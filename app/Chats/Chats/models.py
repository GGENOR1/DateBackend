from fastapi.encoders import ENCODERS_BY_TYPE
from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Annotated, Any, Callable, List, Optional, Dict
from datetime import datetime
from pydantic_core import core_schema

from app.Account.schema import UserAccountReturnToChat


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, context=None):
        """
        Валидация ObjectId, используется для проверки корректности ObjectId.

        :param v: Значение для проверки.
        :return: ObjectId, если значение корректно, иначе выбрасывает исключение.
        """
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, schema, handler):
        """
        Возвращает JSON-схему для сериализации ObjectId в строку.

        :param schema: Схема, которую нужно обновить.
        :param handler: Обработчик, который может быть использован для 
        манипуляции схемой.
        """
        schema.update(type="string")

class Message(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")  # Используем ObjectId для MongoDB
    chat_id: PyObjectId  # Или ObjectId, если используется MongoDB
    sender_id: int       # ID отправителя из PostgreSQL
    recipient_id: int       # ID получателя из PostgreSQL Вопрос актуаллен ли?
    content: str         # Содержимое сообщения
    sent_at: datetime = Field(default_factory=datetime.utcnow)  # Время отправки
    read_by: bool = False  # Статус прочтения
    visibility_sender: bool = True  # Видимость для отправителя
    visibility_recipient: bool = True  # Видимость для получателя
    visibility_all: bool = True  # Общая видимость

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Chat(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")  # Если используем MongoDB
    participants: List[int]  # Список ID пользователей из PostgreSQL
    last_message: Optional[Message] = None  # Последнее сообщение (опционально)
    created_at: datetime = Field(default_factory=datetime.utcnow)  # Время создания
    updated_at: datetime = Field(default_factory=datetime.utcnow)  # Время последнего обновления 
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ChatResponse(BaseModel):
    id: str
    participants: List[UserAccountReturnToChat]
    last_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True