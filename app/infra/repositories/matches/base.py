from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.entities.matches import Match
@dataclass
class BaseMatchesRepository(ABC):
    @abstractmethod
    async def check_match_exists_by_id(self, user_id: int, 
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
    async def add_match(self, match: Match) -> None:
        """_summary_

        Args:
            like (Like): передается модель мэтча
        """
        ...
   