from __future__ import annotations
import asyncio

from .team import TeamModel
from typing import Unpack, TYPE_CHECKING
from bson import ObjectId
from pymongo.collection import Collection
from pymongo.asynchronous.collection import AsyncCollection

from ext.types import TourneyRoundPayload

if TYPE_CHECKING:
    from core.bot import Spruce


class TourneyRoundModel:
    """ TourneyRoundModel class represents a round in a tournament with various properties.
    """
    _cache : dict[str, 'TourneyRoundModel'] = {}
    _col : Collection | AsyncCollection = None  # MongoDB collection name for rounds
    bot : "Spruce" = None  # Reference to the bot instance

    def __init__(self, **kwargs: Unpack[TourneyRoundPayload]) -> None:
        self._id = kwargs.get("_id", None)
        self.tid: int = kwargs.get("tid")  # Tournament ID
        self.name: str = kwargs.get("name", "New Round")
        self.slot_per_group: int = kwargs.get("spg", 12)  # Number of slots per group (default: 12)
        self.slots: int = kwargs.get("slots", 0)  # Total number of slots
        self.teams: list[int] = kwargs.get("teams", [])
        self._teams : list[TeamModel] = kwargs.get("_teams", [])


    def __eq__(self, value: object) -> bool:

        if isinstance(value, int):
            return self._id == value
        if isinstance(value, TourneyRoundModel):
            return self._id == value._id
        return False


    def to_dict(self) -> dict:
        return {
            "_id": self._id,
            "name": self.name,
            "spg": self.slot_per_group,
            "slots": self.slots,
            "teams": self.teams
        }
    

    async def get_teams(self) -> list[TeamModel]:
        if not self._teams:
            if not TourneyRoundModel._col:
                raise ValueError("Collection is not set for TourneyRoundModel.")
            query = {"_id": {"$in": self.teams}}
            if isinstance(TourneyRoundModel._col, AsyncCollection):
                data = await TourneyRoundModel._col.find(query).to_list(length=None)
            else:
                data = TourneyRoundModel._col.find(query).to_list(length=None)

            self._teams = [TeamModel(**team) for team in data]
        
        return self._teams
    

    async def get_team_by_captain(self, captain_id: int) -> TeamModel | None:
        _teams = self._teams or await self.get_teams()
        for team in _teams:
            if team.captain == captain_id:
                return team
            await asyncio.sleep(0)  # Yield control to the event loop
        return None


    async def save(self) -> None:
        if not TourneyRoundModel._col:
            raise ValueError("Collection is not set for TourneyRoundModel.")

        query = [{"_id": self._id}, {"$set": self.to_dict()}]
        if isinstance(TourneyRoundModel._col, AsyncCollection):
            await TourneyRoundModel._col.update_one(query[0], query[1], upsert=True)

        if isinstance(TourneyRoundModel._col, Collection):
            TourneyRoundModel._col.update_one(query[0], query[1], upsert=True)

        return None



    @classmethod
    async def get(cls, _id: ObjectId | str) -> TourneyRoundModel:

        if not TourneyRoundModel._col:
            raise ValueError("Collection is not set for TourneyRoundModel.")
        
        if isinstance(_id, str):
            _doc = cls._cache.get(_id)
            if _doc:
                return _doc

        query = {"_id": _id}
        if isinstance(TourneyRoundModel._col, AsyncCollection):
            data = await TourneyRoundModel._col.find_one(query)
        else:
            data = TourneyRoundModel._col.find_one(query)

        if data:
            return TourneyRoundModel(**data)
        
        return None
