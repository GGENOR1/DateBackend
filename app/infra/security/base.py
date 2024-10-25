from abc import ABC, abstractmethod


class IPasswordHasher(ABC):
    @abstractmethod
    def get_password_hash(self, password: str) -> str:
        ...
    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверить, что введенный пароль совпадает с хешем"""
        ...
    
    @abstractmethod
    def create_access_token(self, user_id: int)-> str:
        "Отдавать токен "
        ...