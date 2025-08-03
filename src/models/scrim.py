from __future__ import annotations

import asyncio
from datetime import datetime
from discord import Member
from typing import Any, TypedDict, Unpack
import pytz

from pymongo.results import DeleteResult

# for dynamic instance checking
from pymongo.collection import Collection
from pymongo.asynchronous.collection import AsyncCollection



IS_DEV_ENV = False  # Set this to True if you want to enable debug messages

class TeamPayload(TypedDict, total=False):
    name: str
    captain: int


class Team:
    def __init__(self, **kwargs: Unpack[TeamPayload]):
        self.name = kwargs.get("name", "Unknown")
        self.captain = kwargs.get("captain", 0)

    def __eq__(self, other):
        if isinstance(other, Team):
            return str(self.name).lower().strip() == other.name and self.captain == other.captain
        
        if isinstance(other, str):
            return str(self.name).lower().strip() == other.lower().strip()
        
        if isinstance(other, int):
            return self.captain == other
        
        return False


    def to_dict(self) -> dict:
        return {
            "name": self.name.lower().strip(),
            "captain": self.captain
        }


class ScrimPayload(TypedDict, total=False):
        status:bool
        name : str
        guild_id:int
        mentions:int
        reg_channel:int
        manage_channel:int
        slot_channel:int
        idp_role : int
        open_time:int
        close_time:int
        total_slots:int
        time_zone:str
        ping_role:int
        


class ScrimModel:
    col: Collection | AsyncCollection = None
    _cache : dict[int, "ScrimModel"] = {}
    _REGISTER_CHANNEL_CACHE : set[int] = set()
    def __init__(self, **kwargs: Unpack[ScrimPayload]):
        """
        Initializes a ScrimModel instance with the provided keyword arguments.
        """
        self.name: str = kwargs.get("name", "Scrim")
        self.status: bool = kwargs.get("status", False) #represents whether the scrim is active or not
        self.guild_id:int = kwargs.get("guild_id")
        self.mentions:int = kwargs.get("mentions", 4) #number of mentions required to register a team
        self.reg_channel:int = kwargs.get("reg_channel") #primary key
        self.slot_channel:int = kwargs.get("slot_channel", self.reg_channel)
        self.manage_channel = kwargs.get("manage_channel", None) #channel where the scrim is managed
        self.idp_role: int = kwargs.get("idp_role")
        self.ping_role:int = kwargs.get("ping_role", None)
        self.open_time:int = kwargs.get("open_time")
        self.close_time:int = kwargs.get("close_time")
        self.total_slots:int = kwargs.get("total_slots", 12)

        self.time_zone:str = kwargs.get("time_zone", "Asia/Kolkata")
        self._id:str = str(kwargs.get("_id", None))
        self.created_at:int = kwargs.get("created_at", int(datetime.now().timestamp())) #timestamp of when the scrim was created
        self.team_compulsion: bool = kwargs.get("team_compulsion", False) #if true, it will require a team to register
        self.multi_register:bool = kwargs.get("multi_register", False) #if true, it will allow duplicate teams to register
        self.duplicate_tag:bool = kwargs.get("duplicate_tag", False) #if true, it will check for duplicate tags in the registration channel        
        self.open_days:list[str] = kwargs.get("open_days", ["mo","tu","we","th","fr","sa","su"]) # List of days when the scrim is open
        self.clear_messages:bool = kwargs.get("clear_messages", True) #if true, it will purge the messages in the registration channel when the scrim is closed
        self.clear_idp_role:bool = kwargs.get("clear_idp_role", True) #if true, it will remove the idp role from the users when the scrim is closed

        self.teams:list[Team] = [Team(**team) for team in kwargs.get("teams", [])] # List of teams, initialized with Team instances
        self.reserved : list[Team] = [Team(**team) for team in kwargs.get("reserved", [])] # List of reserved teams, initialized with Team instances

        if kwargs.get("col"):
            ScrimModel.col = kwargs.get("col")


    def __eq__(self, other):
        if not isinstance(other, ScrimModel):
            return NotImplemented
        return self.reg_channel == other.reg_channel


    def __repr__(self):
        _content = "\033[1;33mScrimModel\033[0m("
        for key, value in self.__dict__.items():
            _content += f"  \033[1;35m{key}\033[0m = {value},"
        return _content + ")"


    def __str__(self):
        _content = "\033[1;33mScrimModel\033[0m("
        for key, value in self.__dict__.items():
            _content += f"  \033[1;35m{key}\033[0m = {value},"
        return _content + ")"



    def validate(self) -> bool:
        """
        Validates the ScrimModel instance.
        Returns:
            bool: True if the instance is valid, False otherwise.
        """
        if not self.reg_channel or not isinstance(self.reg_channel, int):
            raise ValueError(f"Invalid registration channel ID. Expected an integer, got {type(self.reg_channel).__name__}.")
        
        if not isinstance(self.guild_id, int):
            raise ValueError(f"Invalid guild ID. Expected an integer, got {type(self.guild_id).__name__}.")

        if not isinstance(self.open_time, int):
            raise ValueError(f"Invalid open time. Expected an integer, got {type(self.open_time).__name__}.")

        if not isinstance(self.close_time, int):
            raise ValueError(f"Invalid close time. Expected an integer, got {type(self.close_time).__name__}.")

        if not isinstance(self.total_slots, int):
            raise ValueError(f"Invalid total slots. Expected an integer, got {type(self.total_slots).__name__}.")
        
        if self.total_slots <= len(self.reserved):
            raise ValueError(f"Reserved must be less than total slots. Reserved: {len(self.reserved)}, Total Slots: {self.total_slots}")
        
        if not self.time_zone or not isinstance(self.time_zone, str):
            raise ValueError(f"Invalid time zone. Expected a string, got {type(self.time_zone).__name__}.")
        return True

    

    def to_dict(self) -> dict:
        """
        Converts the ScrimModel instance to a dictionary.
        Returns:
            dict: A dictionary representation of the ScrimModel instance.
        """
        _obj =  {
            "created_at": self.created_at,
            "close_time": self.close_time,
            "multi_register": self.multi_register,
            "duplicate_tag": self.duplicate_tag, 
            "guild_id": self.guild_id,
            "idp_role": self.idp_role,
            "mentions": self.mentions,
            "name": self.name,
            "ping_role": self.ping_role,
            "open_days": self.open_days,
            "open_time": self.open_time,
            "reserved": [team.to_dict() for team in self.reserved],
            "reg_channel": self.reg_channel,
            "slot_channel": self.slot_channel,
            "status": self.status,
            "total_slots": self.total_slots,
            "time_zone": self.time_zone,
            "teams": [team.to_dict() for team in self.teams],
            "team_compulsion": self.team_compulsion,
            "clear_messages": self.clear_messages,
            "clear_idp_role" : self.clear_idp_role,
        }
        
        if self.manage_channel:
            _obj["manage_channel"] = self.manage_channel
    
        return _obj


    def add_team(self, captain:int, name:str) -> Team:
        """
        Adds a team to the scrim.
        Args:
            captain (int): The ID of the team captain.
            team_name (str): The name of the team.
        Returns:
            Team: The added team.
        """

        if len(self.teams) + len(self.reserved) >= self.total_slots:
            raise Exception(f"Cannot add more teams. Total slots ({self.total_slots}) already filled with {len(self.teams) + len(self.reserved)} teams.")

        if isinstance(captain, Member):
            captain = captain.id

        new_team = Team(name=name, captain=captain)
        if not self.multi_register and captain in self.teams:
            raise ValueError(f"Multiple registration is not allowed and <@{captain}> is already registered.")

        self.teams.append(new_team)
        return new_team
    

    async def remove_team(self, team: Team):
        """
        Removes a team from the scrim.
        Args:
            team (Team): The team to remove.
        """
        if team in self.teams:
            self.teams.remove(team)

        elif team in self.reserved:
            self.reserved.remove(team)

        else:
            raise ValueError(f"Team {team.name} not found in scrim teams or reserved teams.")
    

    def add_reserved(self, captain:int, name:str) -> Team:
        if  isinstance(captain, Member):
            captain = captain.id

        new_team = Team(name=name, captain=captain)
        if not self.multi_register and new_team in self.reserved:
            raise ValueError(f"Duplicate reserved team is not allowed. <@{captain}> already has a reserved team")
        
        self.reserved.append(new_team)
        return new_team



    def clear_teams(self):
        """
        remove all the teams except the reserved teams. currently not implimented the next idea. for now it's just a wrapper
        """
        self.teams = []
 

    async def save(self):
        """
        Saves the ScrimModel instance to the database.
        Returns:
            UpdateResult: The result of the update operation.
                    
        Raises:
            ScrimAlreadyExists: If a scrim with the same registration channel already exists.
            ValueError: If the instance is not valid.
        """
        self.validate()
        if isinstance(self.col, AsyncCollection):
            _saved = await self.col.update_one(
                {"reg_channel": self.reg_channel},
                {"$set": self.to_dict()},
                upsert=True
            )
        else:
            _saved = self.col.update_one(
                {"reg_channel": self.reg_channel},
                {"$set": self.to_dict()},
                upsert=True
            )

        if _saved.modified_count > 0 or _saved.upserted_id:
            ScrimModel._cache[self.reg_channel] = self
            ScrimModel._REGISTER_CHANNEL_CACHE.add(self.reg_channel)

        return self


    async def delete(self):
        """
        Deletes the ScrimModel instance from the database.
        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        if self.reg_channel in self._cache:
            del ScrimModel._cache[self.reg_channel]
            self._REGISTER_CHANNEL_CACHE.discard(self.reg_channel)

        result: DeleteResult
        query = {"reg_channel": self.reg_channel, "guild_id": self.guild_id}

        if isinstance(self.col, Collection):
            result = self.col.delete_one(query)
        else:
            result = await self.col.delete_one(query)

        return result.deleted_count > 0


    @classmethod
    async def find_by_reg_channel(cls, channel_id:int) -> "ScrimModel | None":
        """
        Finds a ScrimModel instance by its registration channel ID.
        Args:
            channel_id (int): The registration channel ID.
        Returns:
            ScrimModel: The ScrimModel instance if found, None otherwise.
        """
        if channel_id in cls._cache:
            return cls._cache[channel_id]

        query = {"reg_channel": channel_id}
        data : dict[str, Any] = None

        if isinstance(cls.col, Collection):
            data = cls.col.find_one(query)
        else:
            data = await cls.col.find_one(query)

        if data:
            scrim = cls(**data)
            cls._cache[channel_id] = scrim
            cls._REGISTER_CHANNEL_CACHE.add(channel_id)
            return scrim

        return None


    @classmethod
    async def find_one(cls, **kwargs: Unpack[ScrimPayload]) -> "ScrimModel | None":
        """        Finds a single ScrimModel instance based on the provided keyword arguments.
        Args:
            **kwargs: Keyword arguments to filter the ScrimModel instances.
        Returns:
            ScrimModel: The first ScrimModel instance that matches the filter, or None if no match is found.
        """
        if "reg_channel" in kwargs:
            channel_id = kwargs["reg_channel"]

            if channel_id in cls._cache:
                return cls._cache[channel_id]

        data : dict[str, Any] = None

        if isinstance(cls.col, Collection):
            data = cls.col.find_one(kwargs)
        else:
            data = await cls.col.find_one(kwargs)

        if data:
            scrim = cls(**data)
            cls._cache[scrim.reg_channel] = scrim
            return scrim

        cls._cache[kwargs.get("reg_channel", None)] = None
        return None


    @classmethod
    async def find(cls, **kwargs: Unpack[ScrimPayload]) -> list["ScrimModel"]:
        """
        Finds all ScrimModel instances.
        Returns:
            list[ScrimModel]: A list of all ScrimModel instances.
        """
        data : list[dict[str, Any]] = []

        if isinstance(cls.col, Collection):
            data = cls.col.find(kwargs).to_list(length=None)
        else:
            data = await cls.col.find(kwargs).to_list(length=None)

        return [cls(**item) for item in data]
    

    async def skip_to_next_day(self):
        """
        Skips the scrim to the next day.
        This method updates the open and close times to the next day based on the current time zone.
        """
        self.open_time += 24 * 60 * 60  # Add 24 hours in seconds
        self.close_time += 24 * 60 * 60  # Add 24 hours in seconds
        await self.save()

    def next_open_time(self):
        self.open_time += 24 * 60 * 60


    def next_close_time(self):
        self.close_time += 24 * 60 * 60


    def open(self, next=False, clear_teams=False):
        """
        Opens the scrim and sets the status to True.
        Args:
            next (bool): If True, sets the next open time.
            clear_teams (bool): If True, clears the teams in the scrim.
        """
        self.status = True
        if next:
            self.next_open_time()

        if clear_teams:
            self.clear_teams()


    def close(self, next=False):
        """
        Closes the scrim and sets the status to False.
        Args:
            next (bool): If True, sets the next close time.
        """
        self.status = False
        if next:
            self.next_close_time()


    def disable(self):
        self.status = None


    def is_open_day(self) -> bool:
        """
        Checks if the scrim is open on the current day.
        """
        tz = pytz.timezone(self.time_zone)
        current_day = datetime.now(tz).strftime("%a").lower()[0:2]
        return current_day in self.open_days
    

    def is_inactive(self):
        """detect if last open time is 30 ago"""
        last_open_time = datetime.fromtimestamp(self.open_time)
        current_time = datetime.now()
        return (current_time - last_open_time).total_seconds() > 30 * 60


    @classmethod
    async def load_all(cls):
        """
        Loads all scrim instances from the database.
        """
        if isinstance(cls.col, Collection):
            data = cls.col.find({}).to_list(length=None)
        else:
            data = await cls.col.find({}).to_list(length=None)

        for item in data:
            _scrim = cls(**item)
            cls._cache[_scrim.reg_channel] = _scrim
            cls._REGISTER_CHANNEL_CACHE.add(_scrim.reg_channel)
            await asyncio.sleep(0.1)  # Yield control to the event loop

        return cls._cache.values()