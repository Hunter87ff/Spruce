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
        self.members: set[int] = set(kwargs.get("members", [self.captain])) # set of member user ids

        if kwargs.get("_col"):
            TeamModel._col = kwargs.get("_col", None)


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
    
    def validate(self, save=False) -> None:
        """Validates the team data."""
        if not self.tid:
            raise ValueError("Team must have a tournament ID (tid).")
        
        if save and not self._id:
            raise ValueError("Team must have a message ID (_id).")

        if not self.name:
            raise ValueError("Team name cannot be empty.")

        if len(self.name) > 25:
            raise ValueError("Team name cannot exceed 25 characters.")

        if not isinstance(self.captain, int):
            raise ValueError("Team must have a captain.")
        
        if not self.members:
            raise ValueError("Team must have at least one member.")
        
        if len(self.members) > 11:
            raise ValueError("Team cannot have more than 11 members.")
        


    async def save(self) -> None:
        """Saves the team to the database."""
        self.validate(True)
        query = [{"_id": self._id}, {"$set": self.to_dict()}]
        if isinstance(TeamModel._col, AsyncCollection):
            await TeamModel._col.update_one(query[0], query[1], upsert=True)

        if isinstance(TeamModel._col, Collection):
            TeamModel._col.update_one(query[0], query[1], upsert=True)

        return self
    

    async def delete(self) -> bool:
        """Deletes the team from the database."""
        if isinstance(TeamModel._col, AsyncCollection):
            result = await TeamModel._col.delete_one({"_id": self._id})
        else:
            result = TeamModel._col.delete_one({"_id": self._id})

        return result.deleted_count > 0

    @classmethod
    async def find_by_tid(cls, tid: int):
        """Fetches a team by its tournament ID."""
        if cls._col is None:
            raise ValueError("Collection is not set for TeamModel.")
        
        query = {"tid": tid}
        if isinstance(cls._col, AsyncCollection):
            documents = cls._col.find(query)
            document_list = await documents.to_list(length=None)
        else:
            documents = cls._col.find(query)
            document_list = list(documents)

        if not document_list:
            return []

        _teams = [cls(**doc) for doc in document_list]
        return _teams
    
    
    @classmethod
    async def delete_by_tid(cls, tid: int) -> bool:
        """Deletes a team by its tournament ID."""
        if cls._col is None:
            raise ValueError("Collection is not set for TeamModel.")
        
        if isinstance(cls._col, AsyncCollection):
            result = await cls._col.delete_many({"tid": tid})
        else:
            result = cls._col.delete_many({"tid": tid})
        
        return result.deleted_count > 0
