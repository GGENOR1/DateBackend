from dataclasses import dataclass

from app.domain.entities.likes import Like
from app.infra.repositories.likes.base import BaseLikesRepository
from app.logic.exceptions.likes import LikeNotFoundException, LikeWithThatUserAlreadyExistsException
from app.logic.queries.base import BaseQuery, BaseQueryHandler


@dataclass(frozen=True)
class GetLikeDetailQuery(BaseQuery):
    like_oid: str

    
@dataclass(frozen=True)
class GetLikeDetailQueryHandler(BaseQueryHandler):
    likes_repository: BaseLikesRepository

    async def handle(self, query: GetLikeDetailQuery) -> Like:
        like = await self.likes_repository.get_like_by_oid(oid=query.like_oid)

        if not like:
            raise LikeNotFoundException(like_oid=query.like_oid)

        return like
    

@dataclass(frozen=True)
class CheckLikeQuery(BaseQuery):
    user_id: int
    liked_user_id: int

    
@dataclass(frozen=True)
class CheckLikeQueryHandler(BaseQueryHandler):
    likes_repository: BaseLikesRepository

    async def handle(self, query: CheckLikeQuery) -> bool:
        
        like = await self.likes_repository.check_like_exists_by_id(user_id=query.user_id, liked_by_user_id=query.liked_user_id)
        print(like)
        if like:
            raise LikeWithThatUserAlreadyExistsException(user_id=query.liked_user_id)
        
        return like