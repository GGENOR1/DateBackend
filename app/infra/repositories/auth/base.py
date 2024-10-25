from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class IAuthService(ABC):
    @abstractmethod
    async def check_email(self, email: str) -> bool:
        ...
    async def authenticate_user(self, email: str, password: str):
        ...

