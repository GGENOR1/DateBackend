from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.entities.likes import Like


@dataclass
class BaseLikesRepository(ABC):
    @abstractmethod
    async def check_like_exists_by_id(self, user_id: int, 
                                      liked_by_user_id: int) -> bool:
        """

        Args:
            user_id (int): ID пользователя, от которого лайк
            liked_by_user_id (int): ID пользователя, которого лайкают

        Returns:
            bool: Существет или нет
        """
        ...

    @abstractmethod
    async def add_like(self, like: Like) -> None:
        """_summary_

        Args:
            like (Like): передается модель лайка
        """
        ...

    @abstractmethod
    async def get_like_by_oid(self, oid: str) -> Like | None:
        """_summary_

        Args:
            oid (str): oid лайка

        Returns:
            Like | None: 
        """
        ...

    # @abstractmethod
    # async def check_like(self, ) -> Like | None:
    #     """_summary_

    #     Args:
    #         oid (str): oid лайка

    #     Returns:
    #         Like | None: 
    #     """
    #     ...

