from geoalchemy2 import Geography
from sqlalchemy import ARRAY, JSON, TIMESTAMP, Column, ForeignKey, Integer, MetaData, String, text

from sqlalchemy.orm import relationship

from app.domain.entities.accounts import User, UserDetails
# from app.domain.postgresql.models.base import BaseORM
from app.domain.postgresql.models.mixins import CreatedAtOnlyMixin, CreatedRoleMixin, IdMixin, UUIDOidMixin
from sqlalchemy.ext.declarative import declarative_base
metadata = MetaData()

BaseORM = declarative_base(metadata=metadata)

class RolesORM(BaseORM, UUIDOidMixin):
    __tablename__ = 'roles'
    # __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    permissions = Column(JSON, nullable=False)

    def __repr__(self):
        return f"<Roles(id={self.id}, name='{self.name}', permissions='{self.permissions}')>"

    def __str__(self):
        return f"<Roles(id={self.id}, name='{self.name}', permissions='{self.permissions}')>"


class UserORM(BaseORM, IdMixin, CreatedAtOnlyMixin, CreatedRoleMixin):
    __tablename__ = 'users'
    # __table_args__ = {'extend_existing': True}
    # id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    # registered_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    # role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"))
    @staticmethod
    def from_entity(entity: User) -> "UserORM":
        return UserORM(
    
            email=entity.email,
            username=entity.username,
            password=entity.password,
        )

    def to_entity(self) -> User:
        return User(
            id=self.id,
            email=self.email,
            username=self.username,
            password=self.password,
            registered_at=self.registered_at
        )

    # def __str__(self):
    #     return f"User(id={self.id}, email={self.email}, username={self.username}, password={self.password}, registered_at={self.registered_at}, role_id={self.role_id})"

class UserDetailsORM(BaseORM, UUIDOidMixin, IdMixin):
    __tablename__ = 'user_details'
    # __table_args__ = {'extend_existing': True}
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    zodiac_sign = Column(String, nullable=True)
    height = Column(Integer, nullable=True)
    description = Column(String, nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    location = Column(JSON, nullable=True)
    rating = Column(Integer, nullable=True)
    images = Column(JSON, nullable=True)
    educations = Column(String, nullable=True)
    children = Column(String, nullable=True)
    languages = Column(String, nullable=True)
    alcohol = Column(String, nullable=True)
    cigarettes = Column(String, nullable=True)
    # Relationship to the Users table
    # user = relationship("users")
    geolocation = Column(Geography(geometry_type='POINT', srid=4326), nullable=True)
    def __str__(self):
        return (f"User"
                f"(id={self.id}, "
                f"user_id={self.user_id}, "
                f"first_name={self.first_name}, "
                f"last_name={self.last_name}, "
                f"age={self.age}, "
                f" gender={self.gender}) "
                f" zodiac_sign={self.zodiac_sign} "
                f"height={self.height} "
                f"description={self.description} "
                f"tags={self.tags} "
                f"location={self.location} "
                f"rating={self.rating} "
                f"images={self.images} "
                f"cigarettes={self.cigarettes} "
                f"alcohol={self.alcohol} "
                f"languages={self.languages} "
                f"children={self.children} "
                f"educations={self.educations} "
                f"geolocation={self.geolocation}"
                )

    def __repr__(self):
        return (f"User"
                f"(id={self.id}, "
                f"user_id={self.user_id}, "
                f"first_name={self.first_name}, "
                f"last_name={self.last_name}, "
                f"age={self.age},"
                f" gender={self.gender})"
                f" zodiac_sign={self.zodiac_sign}"
                f"height={self.height}"
                f"description={self.description}"
                f"tags={self.tags}"
                f"location={self.location}"
                f"rating={self.rating}"
                f"images={self.images}"
                f"cigarettes={self.cigarettes}"
                f"alcohol={self.alcohol}"
                f"languages={self.languages}"
                f"children={self.children}"
                f"educations={self.educations}"
                f"geolocation={self.geolocation}"
                )
    @staticmethod
    def from_entity(entity: UserDetails) -> "UserDetailsORM":
        return UserDetailsORM(

                id=entity.id,
                user_id=entity.user_id,
                first_name=entity.first_name,
                last_name=entity.last_name,
                age=entity.age,
                 gender=entity.gender,
                 zodiac_sign=entity.zodiac_sign,
                height=entity.height,
                description=entity.description,
                tags=entity.tags,
                location=entity.location,
                rating=entity.rating,
                images=entity.images,
                cigarettes=entity.cigarettes,
                alcohol=entity.alcohol,
                languages=entity.languages,
                children=entity.children,
                educations=entity.educations,
                geolocation=entity.geolocation,
        )