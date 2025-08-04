from __future__ import annotations

import time
import asyncio
from typing import TYPE_CHECKING, Self
from typing import Unpack

from ext import Logger
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
    _REGISTER_CHANNEL_CACHE: set[int] = set()  # Cache for registered tournament channels


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
        self.__teams : list[TeamModel] = []  # List to hold teams registered in the tournament



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
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("name must be a non-empty string")
        
        if len(self.name) > 30:
            raise ValueError("name must be less than 30 characters long")

        if not isinstance(self.status, bool):
            raise ValueError("status must be a boolean")

        if not isinstance(self.mentions, int) or self.mentions <= 0:
            raise ValueError("mentions must be a positive integer")

        if not isinstance(self.tag_filter, bool):
            raise ValueError("tag_filter must be a boolean")

        if not isinstance(self.guild_id, int):
            raise ValueError("guild_id must be an integer")
        
        if not isinstance(self.reg_channel, int):
            raise ValueError("reg_channel must be an integer")
        
        if not isinstance(self.slot_channel, int):
            raise ValueError("slot_channel must be an integer")
        
        if not isinstance(self.confirm_role, int):
            raise ValueError("confirm_role must be an integer")
        
        if not isinstance(self.group_channel, int):
            raise ValueError("group_channel must be an integer")
        
        if not isinstance(self.total_slots, int) or self.total_slots <= 0:
            raise ValueError("total_slots must be a positive integer")
        
        if not isinstance(self.team_count, int) or self.team_count < 0:
            raise ValueError("team_count must be a non-negative integer")
        
        if not isinstance(self.slot_per_group, int) or self.slot_per_group <= 0 or self.slot_per_group > 25:
            raise ValueError("slot_per_group must be an integer between 1 and 25")
        
        if not isinstance(self.created_at, int):
            raise ValueError("created_at must be an integer")
        
        return True


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
        self.validate()
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
    async def is_register_channel(cls, reg_channel:int) -> bool:
        """Checks if a given channel ID is a registered tournament channel."""
        return reg_channel in cls._REGISTER_CHANNEL_CACHE


    @classmethod
    async def get_by_guild(cls, guild_id:int) -> list[Self]:
        _query = {"guild": guild_id}
        
        document:list[dict] | None = None
        if isinstance(cls._col, Collection):
            document = cls._col.find(_query)
        else:
            document = await cls._col.find(_query)

        if document is None:
            return []

        return [cls(**doc) for doc in document]
    
    @classmethod
    async def get_by_slot_manager(cls, slot_manager:int) -> TourneyModel | None:
        """Fetches all tournaments that have a specific slot manager channel."""
        # Check cache first
        for tourney in cls._cache.values():
            if tourney.slot_manager == slot_manager:
                return tourney
            
        _query = {"mch": slot_manager}
        document: dict | None = None
        
        if isinstance(cls._col, Collection):
            document = cls._col.find_one(_query)
        else:
            document = await cls._col.find_one(_query)

        if document is None:
            return None
        
        _tourney = cls(**document)
        if cls._cache.get(_tourney.reg_channel):
            return cls._cache[_tourney.reg_channel]
        
        cls._cache[_tourney.reg_channel] = _tourney
        cls._REGISTER_CHANNEL_CACHE.add(_tourney.reg_channel)

        return _tourney



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
    
    def create_team(self, **kwargs: Unpack[TourneyTeamPayload]) -> TeamModel:
        """Creates a new team instance for the tournament."""
        team = TeamModel(**kwargs)
        team.tid = self.reg_channel
        return team

    async def get_teams(self) -> set[TeamModel]:
        """Fetches all teams registered in the tournament."""
        if self.__teams:
            return self.__teams

        self.__teams = await TeamModel.find_by_tid(self.reg_channel)
        return self.__teams
    
    
    async def get_team_by_player_id(self, player_id:int):
        """Fetches a team by a player's ID.""" 
        _teams : list[TeamModel] = []

        for team in await self.get_teams():
            if player_id in team.members:
                _teams.append(team)

        return _teams 
    
    async def get_team_by_id(self, team_id:int) -> TeamModel | None:
        """Fetches a team by its ID."""
        for team in await self.get_teams():
            if team._id == team_id:
                return team
        return None
    

    async def validate_team(self, team: TeamModel) -> bool:
        """Validates if a team can be added to the tournament."""
        team.validate()

        if self.tag_filter:
            for _team in await self.get_teams():
                if len(_team.members.intersection(team.members)) > 0:
                    raise ValueError("Duplicate tags found in the team members.")

        if team.tid != self.reg_channel:
            raise ValueError("Team is not registered in this tournament.")
        
        if self.team_count >= self.total_slots:
            raise ValueError("Tournament is full. Cannot add more teams.")
        
        if len(team.members) < self.mentions:
            raise ValueError(f"Team does not meet the minimum mentions requirement of {self.mentions} members.")
                
        return True    


    async def add_team(self, team : TeamModel) -> None:
        """Adds a team to the tournament."""
        
        try:
            await self.validate_team(team)
            await team.save()
            self.__teams.append(team)
            self.team_count += 1
            await self.save()
            self._cache[self.reg_channel] = self  # Update cache
            return team

        except Exception as e:
            raise ValueError(str(e))


    async def remove_team(self, team: TeamModel) -> bool:
        """Removes a team from the tournament."""
        if team not in self.__teams:
            raise ValueError("Team not found in the tournament.")
        await team.delete()
        self.__teams.remove(team)
        self.team_count -= 1
        await self.save()
        
        self._cache[self.reg_channel] = self  # Update cache
        return True


    @classmethod
    async def load_all(cls) -> list[TourneyModel]:
        """Loads all tournaments from the database and caches them."""
        if isinstance(cls._col, Collection):
            documents = cls._col.find({})

        elif isinstance(cls._col, AsyncCollection):
            documents = await cls._col.find({})

        if documents is None:
            return []

        for doc in documents:
            _tourney = cls(**doc)
            cls._cache[_tourney.reg_channel] = _tourney
            cls._REGISTER_CHANNEL_CACHE.add(_tourney.reg_channel)
        Logger.info(f"Loaded {len(cls._cache)} tournaments from the database.")
        return cls._cache.values()


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
            cls._REGISTER_CHANNEL_CACHE.discard(reg_channel)
            return _name
        
        return 
    


    
