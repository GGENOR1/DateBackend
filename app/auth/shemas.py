from datetime import datetime

from pydantic import BaseModel, EmailStr


class SUserAuthWithCode(BaseModel):
    code: int
    email: EmailStr
    password: str

    def __str__(self):
        return f"Email={self.email}"


class SUserAuth(BaseModel):
    email: EmailStr
    password: str

    def __str__(self):
        return f"Email={self.email}"


class SUserRegistration(BaseModel):
    email: EmailStr

    def __str__(self):
        return f"Email={self.email}"

class SUserConfirmCode(BaseModel):
    email: EmailStr
    code: int
    def __str__(self):
        return f"Email={self.email}"

class SUserRegistrationWithCode(BaseModel):
    code: int
    email: str
    username: str
    password: str
    registered_at: datetime
    role_id: int

    class Config:
        orm_mode = True

    def __str__(self):
        return f" email={self.email}, username={self.username}, password={self.password}, registered_at={self.registered_at}, role_id={self.role_id})"

