from datetime import datetime
import functools
# from pymongo import MongoClient
from typing import TypedDict, Unpack
from ext.types.errors import ScrimAlreadyExists
from ext.db import Database

_db_ =  Database()   #MongoClient("mongodb://localhost:27017/")  # Adjust the connection string as needed
_scrim_col = _db_.scrims    # _db_["test"]["scrims"]  # Adjust the database and collection names as needed
_scrim_cache_by_channel: dict[int, "ScrimModel | None"]  = {}


class ReservedSlot:
    def __init__(self, captain_id: int, team_name: str):
        self.captain_id = captain_id
        self.team_name = team_name

    def to_dict(self) -> dict:
        return {
            "captain": self.captain_id,
            "name": self.team_name
        }


class Team:
    def __init__(self, name: str, captain_id: int):
        self.name = name
        self.captain_id = captain_id

    def __eq__(self, other):
        if not isinstance(other, Team):
            return NotImplemented
        return self.name.lower() == other.name.lower() and self.captain_id == other.captain_id

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "captain": self.captain_id
        }
    

class ScrimPayload(TypedDict, total=False):
        status:bool
        name : str
        guild_id:int
        mentions:int
        reg_channel:int
        slot_channel :int
        idp_role : int
        open_time:int
        close_time:int
        total_slots:int
        team_count:int
        time_zone:str
        ping_role:int
        duplicate_tag_check:bool
        reserved : dict[int,str]


class ScrimModel:

    def __init__(self, **kwargs:Unpack[ScrimPayload]):
        """
        Initializes a ScrimModel instance with the provided keyword arguments.
        """
        self.name: str = kwargs.get("name", "Scrim")
        self.status: bool = kwargs.get("status", False) #represents whether the scrim is active or not
        self.guild_id:int = kwargs.get("guild_id")
        self.mentions:int = kwargs.get("mentions", 4) #number of mentions required to register a team
        self.reg_channel:int = kwargs.get("reg_channel") #primary key
        self.slot_channel:int = kwargs.get("slot_channel", self.reg_channel)
        self.idp_role: int = kwargs.get("idp_role")
        self.ping_role:int = kwargs.get("ping_role", None)
        self.open_time:int = kwargs.get("open_time")
        self.close_time:int = kwargs.get("close_time")
        self.total_slots:int = kwargs.get("total_slots", 12)
        self.team_count:int = kwargs.get("team_count", 0)
        self.teams:list[Team] = [Team(**team) for team in kwargs.get("teams", [])] #[{team_name, captain_id}, ...]
        self.time_zone:str = kwargs.get("time_zone", "Asia/Kolkata")
        self._id:str = str(kwargs.get("_id", None))
        self.created_at:int = kwargs.get("created_at", int(datetime.now().timestamp())) #timestamp of when the scrim was created
        self.team_compulsion: bool = kwargs.get("team_compulsion", False) #if true, it will require a team to register
        self.duplicate_team:bool = kwargs.get("duplicate_team", False) #if true, it will allow duplicate teams to register
        self.duplicate_tag_check:bool = kwargs.get("duplicate_tag_check", True) #if true, it will check for duplicate tags in the registration channel
        self.reserved : list[Team] = [Team(**team) for team in kwargs.get("reserved", [])] #[{team_name, captain_id}, ...]
        self.open_days:list[str] = kwargs.get("open_days", ["mo","tu","we","th","fr","sa","su"]) # List of days when the scrim is open
        self.clear_messages:bool = kwargs.get("clear_messages", True) #if true, it will purge the messages in the registration channel when the scrim is closed
        self.clear_idp_role:bool = kwargs.get("clear_idp_role", True) #if true, it will remove the idp role from the users when the scrim is closed


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
        
        if not self.guild_id or not isinstance(self.guild_id, int):
            raise ValueError(f"Invalid guild ID. Expected an integer, got {type(self.guild_id).__name__}.")
        
        if not self.open_time or not isinstance(self.open_time, int):
            raise ValueError(f"Invalid open time. Expected an integer, got {type(self.open_time).__name__}.")
        
        if not self.close_time or not isinstance(self.close_time, int):
            raise ValueError(f"Invalid close time. Expected an integer, got {type(self.close_time).__name__}.")
        
        if not self.total_slots or not isinstance(self.total_slots, int):
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
        return {
            "created_at": self.created_at,
            "close_time": self.close_time,
            "duplicate_team": self.duplicate_team,
            "duplicate_tag_check": self.duplicate_tag_check, 
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
            "team_count": self.team_count, #deprecated, use teams instead
            "time_zone": self.time_zone,
            "teams": [team.to_dict() for team in self.teams],
            "team_compulsion": self.team_compulsion,
            "clear_messages": self.clear_messages,
            "clear_idp_role" : self.clear_idp_role,
        }
    

    @functools.lru_cache(maxsize=128)
    def find_teams(self, team_name:str=None, captain_id:int=None) -> list[Team]:
        """
        Finds a team by its name or captain ID.
        Args:
            team_name (str): The name of the team.
            captain_id (int): The ID of the team captain.
        Returns:
            int: The captain ID if found, None otherwise.
        """
        teams : list[Team] = []
        if team_name and not captain_id:
            teams = [team for team in self.teams if team.name.lower() == team_name.lower()]

        elif captain_id and not team_name:
            teams = [team for team in self.teams if team.captain_id == captain_id]
        
        elif team_name and captain_id:
            teams = [team for team in self.teams if team.name.lower() == team_name.lower() and team.captain_id == captain_id]
        
        return teams
    

    def add_team(self, captain_id:int, team_name:str) -> Team:
        """
        Adds a team to the scrim.
        Args:
            captain_id (int): The ID of the team captain.
            team_name (str): The name of the team.
        Returns:
            Team: The added team.
        """
        new_team = Team(name=team_name, captain_id=captain_id)
        if not self.duplicate_team and new_team in self.teams:
            raise ValueError(f"Duplicate team is not allowed. <@{captain_id}> already has a team named {team_name}.")
        
        self.teams.append(new_team)
        self.team_count += 1
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
        if not self._id:
            _existing = ScrimModel.find_one(reg_channel=self.reg_channel)

            if _existing and _existing == self:
                return
            
            raise ScrimAlreadyExists("A scrim with this registration channel already exists.")

        self.validate()

        _saved = _scrim_col.update_one(
            {"reg_channel": self.reg_channel},
            {"$set": self.to_dict()},
            upsert=True
        )


        if _saved.modified_count > 0 or _saved.upserted_id:
            _scrim_cache_by_channel[self.reg_channel] = self

        return _saved


    def delete(self):
        """
        Deletes the ScrimModel instance from the database.
        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        if self.reg_channel in _scrim_cache_by_channel:
            del _scrim_cache_by_channel[self.reg_channel]

        result = _scrim_col.delete_one({"reg_channel": self.reg_channel})
        return result.deleted_count > 0


    @staticmethod
    def find_by_reg_channel(channel_id:int) -> "ScrimModel | None":
        """
        Finds a ScrimModel instance by its registration channel ID.
        Args:
            channel_id (int): The registration channel ID.
        Returns:
            ScrimModel: The ScrimModel instance if found, None otherwise.
        """
        if channel_id in _scrim_cache_by_channel:
            return _scrim_cache_by_channel[channel_id]
        
        data = _scrim_col.find_one({"reg_channel": channel_id})
        if data:
            scrim = ScrimModel(**data)
            _scrim_cache_by_channel[channel_id] = scrim
            return scrim
        _scrim_cache_by_channel[channel_id] = None

        return None


    @staticmethod
    def find_one(**kwargs:Unpack[ScrimPayload]) -> "ScrimModel | None":
        """        Finds a single ScrimModel instance based on the provided keyword arguments.
        Args:
            **kwargs: Keyword arguments to filter the ScrimModel instances.
        Returns:
            ScrimModel: The first ScrimModel instance that matches the filter, or None if no match is found.
        """
        if "reg_channel" in kwargs:
            channel_id = kwargs["reg_channel"]
            if channel_id in _scrim_cache_by_channel:
                return _scrim_cache_by_channel[channel_id]
            
        data = _scrim_col.find_one(kwargs)
        if data:
            scrim = ScrimModel(**data)
            _scrim_cache_by_channel[scrim.reg_channel] = scrim
            return scrim
        
        _scrim_cache_by_channel[kwargs.get("reg_channel", None)] = None
        return None


    @staticmethod
    def find(**kwargs: Unpack[ScrimPayload]) -> list["ScrimModel"] :
        """
        Finds all ScrimModel instances.
        Returns:
            list[ScrimModel]: A list of all ScrimModel instances.
        """
        data = _scrim_col.find(kwargs).to_list(length=None)
        return [ScrimModel(**item) for item in data]
    

# sm = ScrimModel.find()