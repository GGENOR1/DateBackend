from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from shapely import Point
from shapely import wkb
from app.domain.entities.accounts import User, UserDetails
from app.domain.postgresql.models.accounts import UserORM
from geoalchemy2.shape import to_shape
# from app.domain.entities.accounts import Account

class Location(BaseModel):
    latitude: str = None
    longitude: str = None
    city: str = None
    country: str = None

class Geolocation(BaseModel):
    latitude: float | None
    longitude: float | None


class AccountSchema(BaseModel):
    email: str
    username: str
    role_id: int
    registered_at: datetime

    @classmethod
    def from_entity(cls, user: User) -> 'AccountSchema':
        return cls(
            email=user.email,
            username=user.username,
            role_id=user.role_id,
            registered_at=user.registered_at
           
        )
    
class AccountDetailsSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    zodiac_sign: Optional[str] = None
    height: Optional[int] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    location: Optional[Location] = None
    rating: Optional[int] = None
    # images: Optional[List[str]] = None
    educations: Optional[str] = None
    children: Optional[str] = None
    languages: Optional[str] = None
    alcohol: Optional[str] = None
    cigarettes: Optional[str] = None
    geolocation: Optional[Geolocation] = None
    
    @classmethod
    def from_entity(cls, user: UserDetails) -> 'AccountDetailsSchema':
        # print(user.geolocation)
        if user.geolocation:
            geolocation_point: Point = to_shape(user.geolocation)
            latitude = geolocation_point.y
            longitude = geolocation_point.x
        else: 
            latitude = None
            longitude = None

        # print(f"{longitude=}, {latitude=}")
        return cls(
            first_name=user.first_name,
            last_name=user.last_name,
            age=user.age,
            gender=user.gender,
            zodiac_sign=user.zodiac_sign,
            height=user.height,
            description=user.description,
            tags=user.tags,
            location=user.location,
            rating=user.rating,
            #=user.#=
            educations=user.educations,
            children=user.children,
            languages=user.languages,
            alcohol=user.alcohol,
            cigarettes=user.cigarettes,
            geolocation=Geolocation(latitude=latitude, longitude=longitude)
            )
    
class CreateUserResponseSchema(BaseModel):
    id: int
    email: str
    username: str
    role_id: int
    registered_at: datetime
    @classmethod
    def from_entity(cls, user: User) -> 'CreateUserResponseSchema':
        return cls(
            id=user.id,
            email=user.email,
            username=user.username,
            role_id=user.role_id,
            registered_at=user.registered_at
           
        )
    
class DeleteUserResponseSchema(BaseModel):
    email: str
    @classmethod
    def from_entity(cls, user: User) -> 'DeleteUserResponseSchema':
        return cls(
            id=user.id,
        )
    
class CreateUserRequestSchema(BaseModel):
    email: str
    username: str
    password: str




class UpdateAccountDetailsResponseSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    zodiac_sign: Optional[str] = None
    height: Optional[int] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    location: Optional[Location] = None
    rating: Optional[int] = None
    # images: Optional[List[str]] = None
    educations: Optional[str] = None
    children: Optional[str] = None
    languages: Optional[str] = None
    alcohol: Optional[str] = None
    cigarettes: Optional[str] = None
    geolocation: Optional[Geolocation] = None
    
    @classmethod
    def from_entity(cls, user: UserDetails) -> 'UpdateAccountDetailsResponseSchema':
        geolocation_point: Point = to_shape(user.geolocation)
        latitude = geolocation_point.y
        longitude = geolocation_point.x
        print(f"{longitude=}, {latitude=}")
        return cls(
            first_name=user.first_name,
            last_name=user.last_name,
            age=user.age,
            gender=user.gender,
            zodiac_sign=user.zodiac_sign,
            height=user.height,
            description=user.description,
            tags=user.tags,
            location=user.location,
            rating=user.rating,
            #=user.#=
            educations=user.educations,
            children=user.children,
            languages=user.languages,
            alcohol=user.alcohol,
            cigarettes=user.cigarettes,
            geolocation=Geolocation(latitude=latitude, longitude=longitude)
            )
    
class UpdateAccountDetailsRequestSchema(BaseModel):
    """Модель для запроса на обновление данных аккаунта """
    zodiac_sign: Optional[str] = None
    height: Optional[int] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    educations: Optional[str] = None
    children: Optional[str] = None
    languages: Optional[str] = None
    alcohol: Optional[str] = None
    cigarettes: Optional[str] = None
