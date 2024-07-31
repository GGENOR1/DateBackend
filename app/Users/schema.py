from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class RoleSchema(BaseModel):
    id: int
    name: str
    permissions: dict

    class Config:
        orm_mode = True

class UserSchema(BaseModel):
    id: int
    email: str
    username: str
    password: str
    registered_at: datetime
    role_id: int
    
    class Config:
        orm_mode = True

class UserAddSchema(BaseModel):
    email: str
    username: str
    password: str
    registered_at: datetime
    role_id: int
    
    class Config:
        orm_mode = True

    def __str__(self):
        return f" email={self.email}, username={self.username}, password={self.password}, registered_at={self.registered_at}, role_id={self.role_id})"
    

class UserUpdateSchema(BaseModel):
    username: str
    password: str
    role_id: int
    
    class Config:
        orm_mode = True

    def __str__(self):
        return f"  username={self.username}, password={self.password}, role_id={self.role_id})"