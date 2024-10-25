from dataclasses import dataclass
from typing import ClassVar

from app.domain.events.base import BaseEvent


@dataclass
class UserDeletedEvent(BaseEvent):
    title: ClassVar[str] = 'User Has Been Deleted'

    id: int
