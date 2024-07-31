from pydantic import BaseModel

from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class Location(BaseModel):
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
class Geolocation(BaseModel):
    latitude: float
    longitude: float
class UserAccountCreate(BaseModel):
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
    images: Optional[List[str]] = None
    educations: Optional[str] = None
    children: Optional[str] = None
    languages: Optional[str] = None
    alcohol: Optional[str] = None
    cigarettes: Optional[str] = None
    geolocation: Optional[Geolocation] = None
    class Config:
        orm_mode = True

class UserAccountReturn(BaseModel):
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
    class Config:
        orm_mode = True


class UserAccountReturnToListCard(BaseModel):
    user_id: Optional[int] = None
    first_name: Optional[str] = None
    age: Optional[int] = None
    tags: Optional[List[str]] = None
    location: Optional[Location] = None
    # images: Optional[List[str]] = None
    geolocation: Optional[Geolocation] = None
    distance: Optional[float] = None
    class Config:
        orm_mode = True

class UserAccountReturnToListMatches(BaseModel):
    user_id: Optional[int] = None
    first_name: Optional[str] = None
    age: Optional[int] = None
    location: Optional[Location] = None
    # images: Optional[List[str]] = None
    geolocation: Optional[Geolocation] = None
    distance: Optional[float] = None
    view: Optional[bool] = None
    class Config:
        orm_mode = True
class UserAccountUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    height: Optional[int] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    educations: Optional[str] = None
    children: Optional[str] = None
    languages: Optional[str] = None
    alcohol: Optional[str] = None
    cigarettes: Optional[str] = None
    location: Optional[Location] = None

    class Config:
        orm_mode = True
