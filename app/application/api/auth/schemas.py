from pydantic import BaseModel, EmailStr


class AuthorizationResponseSchema(BaseModel):
    token: str

    @classmethod
    def from_entity(cls, token: str) -> 'AuthorizationResponseSchema':
        return cls(
           token=token,
        )

class AuthorizationShema(BaseModel):
    code: int
    email: EmailStr
    password: str