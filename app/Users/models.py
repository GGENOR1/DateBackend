from geoalchemy2 import Geography
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, JSON, TIMESTAMP, ForeignKey, text, ARRAY
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()


class Roles(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    permissions = Column(JSON, nullable=False)

    def __repr__(self):
        return f"<Roles(id={self.id}, name='{self.name}', permissions='{self.permissions}')>"

    def __str__(self):
        return f"<Roles(id={self.id}, name='{self.name}', permissions='{self.permissions}')>"


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    registered_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"))

    def __str__(self):
        return f"User(id={self.id}, email={self.email}, username={self.username}, password={self.password}, registered_at={self.registered_at}, role_id={self.role_id})"

class UserDetails(Base):
    __tablename__ = 'user_details'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    zodiac_sign = Column(String, nullable=True)
    height = Column(Integer, nullable=True)
    description = Column(String, nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    location = Column(JSON, nullable=False)
    rating = Column(Integer, nullable=True)
    images = Column(JSON, nullable=True)
    educations = Column(String, nullable=True)
    children = Column(String, nullable=True)
    languages = Column(String, nullable=True)
    alcohol = Column(String, nullable=True)
    cigarettes = Column(String, nullable=True)
    # Relationship to the Users table
    user = relationship("Users")
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
