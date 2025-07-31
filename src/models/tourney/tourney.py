from __future__ import annotations

import time
import asyncio
from typing import TYPE_CHECKING
from typing import Unpack

from pymongo.collection import Collection
from pymongo.asynchronous.collection import AsyncCollection
from ext.types import TournamentPayload, TourneyTeamPayload
from .team import TeamModel

if TYPE_CHECKING:
    from core.bot import Spruce


class TourneyModel:
    """
    Tourney class represents a tournament with various properties.
    """
    _cache: dict[int, 'TourneyModel'] = {}
    _col: Collection | AsyncCollection = None  # MongoDB collection name for tournaments
    bot : "Spruce" = None  # Reference to the bot instance

    def __init__(self, **kwargs: Unpack[TournamentPayload]) -> None:
        # print("Initializing TourneyModel with kwargs:", kwargs)
        self.guild_id: int = kwargs.get("guild")
        self.status: bool = kwargs.get("status", True) # True if the tournament is active, False otherwise
        self.name: str = str(kwargs.get("name", "New Tournament"))
        self.tag_filter: bool = kwargs.get('ftch', False)  # duplicate tag filter
        self.reg_channel: int = int(kwargs.get("rch"))
        self.slot_channel: int = kwargs.get("cch")
        self.group_channel: int = kwargs.get("gch")
        self.slot_manager: int = kwargs.get("mch") #slot manager channel id
        self.mentions: int = kwargs.get("mentions", 4) # minimum mentions required to register
        self.confirm_role: int = kwargs.get("crole") # confirmation role id
        self.total_slots: int = kwargs.get("tslot") # total slots available in the tournament
        self.team_count: int = kwargs.get("reged", 0) # number of teams registered in the tournament
        self.slot_per_group: int = kwargs.get("spg", 12) #number of slots per group (default: 12)
        self.created_at: int = int(kwargs.get("cat", time.time()))
        self.__teams : list[TeamModel] = []


        if kwargs.get("col"):
            TourneyModel._col = kwargs.get("col", None)

    def __repr__(self) -> str:
        return f"<Tournament guild={self.guild_id} status={self.status} rch={self.reg_channel} cch={self.slot_channel} crole={self.confirm_role} gch={self.group_channel} tslot={self.total_slots} reged={self.team_count} spg={self.slot_per_group} cgp={self.current_group} cat={self.created_at}>"

    def __str__(self) -> str:
        return f"Tournament(guild={self.guild_id}, status={self.status}, rch={self.reg_channel}, cch={self.slot_channel}, crole={self.confirm_role}, gch={self.group_channel}, tslot={self.total_slots}, reged={self.team_count}, spg={self.slot_per_group}, cgp={self.current_group}, cat={self.created_at})"


    def __eq__(self, value):
        if isinstance(value, int):
            return self.reg_channel == value
        
        elif isinstance(value, TourneyModel):
            return any([
                self.reg_channel == value.reg_channel,
                self.slot_manager == value.slot_manager,
            ])
        return False


    def validate(self) -> bool:
        """Validates the Tournament instance.

        Returns:
            bool: True if the instance is valid, False otherwise.
        """
        
        return all([
            isinstance(self.guild_id, int),
            isinstance(self.reg_channel, int),
            isinstance(self.slot_channel, int),
            isinstance(self.confirm_role, int),
            isinstance(self.group_channel, int),
            isinstance(self.total_slots, int) and self.total_slots > 0,
            isinstance(self.team_count, int) and self.team_count >= 0,
            isinstance(self.slot_per_group, int) and self.slot_per_group > 0 and self.slot_per_group <= 25,
            isinstance(self.created_at, int)
        ])


    def to_dict(self) -> TournamentPayload:
        """Converts the Tournament instance to a dictionary.

        Returns:
            TournamentPayload: A dictionary representation of the Tournament instance.
        """
        return {
            "name": self.name,
            "guild": self.guild_id,
            "status": self.status,
            "rch": self.reg_channel,
            "cch": self.slot_channel,
            "mentions": self.mentions,
            "ftch": self.tag_filter,
            "crole": self.confirm_role,
            "gch": self.group_channel,
            "tslot": self.total_slots,
            "reged": self.team_count,
            "spg": self.slot_per_group,
            "mch": self.slot_manager,
            "cat": self.created_at,
            "_v": 1,  # Versioning for future changes
        }
    

    
    async def save(self):
        if not self.validate():
            raise ValueError("Invalid Tournament instance. Cannot save to database.")
        
        if isinstance(self._col, Collection):
            self._col.update_one(
                {"rch": self.reg_channel, "guild": self.guild_id},
                {"$set": self.to_dict()},
                upsert=True
            )

        elif isinstance(self._col, AsyncCollection):
            await self._col.update_one(
                {"rch": self.reg_channel, "guild": self.guild_id},
                {"$set": self.to_dict()},
                upsert=True
            )

        return self
    

    @classmethod
    async def find_one(cls, **kwargs: Unpack[TournamentPayload]) -> TourneyModel | None:

        # async find from cache 
        _temp = cls(**kwargs)
        for tourney in cls._cache.values():
            if _temp == tourney:
                return tourney
            await asyncio.sleep(0)

        document: dict = cls._col.find_one(kwargs) if isinstance(cls._col, Collection) else await cls._col.find_one(kwargs)
        if document is None:
            return None
        # Create a new instance of TourneyModel with the fetched data
        
        _temp = cls(**document)
        cls._cache[_temp.reg_channel] = _temp

        return _temp


    @classmethod
    async def get(cls, reg_channel:int) -> TourneyModel | None:
        """Fetches a Tournament instance by its registration channel ID. from cache then from database"""
        if reg_channel in cls._cache:
            return cls._cache[reg_channel]

        _tourney = await cls.find_one(rch=reg_channel)
        if not _tourney:
            return None

        cls._cache[reg_channel] = _tourney
        return _tourney


    @classmethod
    async def get_by_guild(cls, guild_id:int):
        _query = {"guild": guild_id}
        
        document:list[dict] | None = None
        if isinstance(cls._col, Collection):
            document = cls._col.find(_query)
        else:
            document = await cls._col.find(_query)

        if document is None:
            return None

        return [cls(**doc) for doc in document]
    

    async def update(self, **kwargs: Unpack[TournamentPayload]) -> TourneyModel:
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        query = {"rch": self.reg_channel, "guild": self.guild_id}
        update_data = self.to_dict()
        if isinstance(self._col, Collection):
            self._col.update_one(query, {"$set": update_data}, upsert=True)
        elif isinstance(self._col, AsyncCollection):
            await self._col.update_one(query, {"$set": update_data}, upsert=True)

        self._cache[self.reg_channel] = self
        return self
    

    async def get_teams(self) -> list[TeamModel]:
        """Fetches all teams registered in the tournament."""
        if self.__teams:
            return self.__teams

        self.__teams = await TeamModel.find_by_tid(self.reg_channel)
        return self.__teams if self.__teams else []

    

    async def add_team(self, **kwargs: Unpack[TourneyTeamPayload]) -> None:
        """Adds a team to the tournament."""
        
        try:
            team = TeamModel(**kwargs)
            await team.save()
            self.__teams.append(team)
            self.team_count += 1
            await self.save()
            self._cache[self.reg_channel] = self  # Update cache
            return team

        except Exception as e:
            raise ValueError(f"Failed to add team: {e}")

    

    @classmethod
    async def delete(cls, reg_channel: int):
        """Deletes a Tournament instance from the database.

        Args:
            reg_channel (int): The registration channel ID of the tournament to delete.

        Returns:
            bool: True if the tournament was deleted, False otherwise.
        """
        _tourney = cls._cache.get(reg_channel)

        if _tourney is None:
            return False
        
        _name = _tourney.name
        await TeamModel.delete_by_tid(reg_channel)
        cls._cache.pop(reg_channel, None)
        result = cls._col.delete_one(
            filter={"rch": reg_channel}
        ) if isinstance(cls._col, Collection) else await cls._col.delete_one(
            filter={"rch": reg_channel}
        )
        
        if result.deleted_count > 0:
            cls._cache.pop(reg_channel, None)

            return _name
        
        return 
    


    
