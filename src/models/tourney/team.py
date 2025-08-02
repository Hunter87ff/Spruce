from __future__ import annotations
from ext.types import TourneyTeamPayload
from typing import Unpack, TYPE_CHECKING
from pymongo.collection import Collection
from pymongo.asynchronous.collection import AsyncCollection


if TYPE_CHECKING:
    from core.bot import Spruce


class TeamModel:
    """
    TeamModel class represents a team in a tournament with various properties.
    """
    _col : Collection | AsyncCollection = None  # MongoDB collection name for teams
    _bot : "Spruce" = None  # Reference to the bot instance

    def __init__(self, **kwargs: Unpack[TourneyTeamPayload]) -> None:
        self._id: int = kwargs.get("_id") #confirm message id
        self.tid : int = kwargs.get("tid") # tournament registration channel id
        self.name: str = kwargs.get("name", "New Team")
        self.captain: int = kwargs.get("capt") # captain's user id
        self.members: set[int] = set(kwargs.get("members", [])) # set of member user ids

        if kwargs.get("col"):
            TeamModel._col = kwargs.get("col", None)


    def __eq__(self, value: object) -> bool:
        if isinstance(value, int):
            return self.captain == value
        
        elif isinstance(value, TeamModel):
            return self._id == value._id
        
        return False
    

    def to_dict(self) -> dict:
        return {
            "_id": self._id,
            "tid" : self.tid,
            "name": self.name,
            "capt": self.captain,
            "members": list(self.members)
        }
    

    async def save(self) -> None:
        if not TeamModel._col:
            raise ValueError("Collection is not set for TeamModel.")
        query = [{"_id": self._id}, {"$set": self.to_dict()}]
        if isinstance(TeamModel._col, AsyncCollection):
            await TeamModel._col.update_one(query[0], query[1], upsert=True)

        if isinstance(TeamModel._col, Collection):
            TeamModel._col.update_one(query[0], query[1], upsert=True)

        return self
    


    @classmethod
    async def find_by_tid(cls, tid: int):
        """Fetches a team by its tournament ID."""
        if not cls._col:
            raise ValueError("Collection is not set for TeamModel.")
        
        query = {"tid": tid}
        if isinstance(cls._col, AsyncCollection):
            document = await cls._col.find_one(query)
        else:
            document = cls._col.find(query)

        if not document:
            return None

        _teams = [cls(**doc) for doc in document]
        return _teams
    
    
    @classmethod
    async def delete_by_tid(cls, tid: int) -> bool:
        """Deletes a team by its tournament ID."""
        if not cls._col:
            raise ValueError("Collection is not set for TeamModel.")
        
        result = await cls._col.delete_one({"tid": tid})
        return result.deleted_count > 0
