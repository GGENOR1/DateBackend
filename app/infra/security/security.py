from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext




from app.infra.security.base import IPasswordHasher
from app.settings import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordHasher(IPasswordHasher):

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        print(f"{plain_password=}")
        print(f"{hashed_password=}")
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, user_id: int):
        try:
            payload = {"sub": user_id, "exp": datetime.utcnow() + timedelta(minutes=1000)}
            print(f"{payload=}")
            return jwt.encode(payload, settings.secret_key , settings.algorithm)
        except Exception as e:
            print(e)
            return None