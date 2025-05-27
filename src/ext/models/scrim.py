import functools
from pymongo import MongoClient
from typing import TypedDict, Unpack
from ext.db import Database

_db_ =  Database()   #MongoClient("mongodb://localhost:27017/")  # Adjust the connection string as needed
_scrim_col = _db_.scrims    # _db_["test"]["scrims"]  # Adjust the database and collection names as needed


class ScrimPayload(TypedDict, total=False):
        status:bool
        name : str
        guild_id:int
        mentions:int
        reg_channel:int
        slot_channel :int
        idp_role : int
        start_time:str
        end_time:str
        total_slots:int
        team_count:int
        auto_clean:bool
        time_zone:str
        ping_role:int
        reserved : list[int]
        


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
        self.start_time:str = kwargs.get("start_time", "10:00 AM")
        self.end_time:str = kwargs.get("end_time", "4:00 PM")
        self.total_slots:int = kwargs.get("total_slots", 12)
        self.team_count:int = kwargs.get("team_count", 0)
        self.time_zone:str = kwargs.get("time_zone", "Asia/Kolkata")
        self.reserved : list[int] = kwargs.get("reserved", [])
        self.auto_clean:bool = bool(kwargs.get("auto_clean", True))
        self._id:str = str(kwargs.get("_id", None))



    def __eq__(self, other):
        if not isinstance(other, ScrimModel):
            return NotImplemented
        return self.reg_channel == other.reg_channel


    def __repr__(self):
        _content = "\033[1;33mScrimModel\033[0m(\n"
        for key, value in self.__dict__.items():
            _content += f"  \033[1;35m{key}\033[0m = {value},\n"
        return _content + ")"


    def __str__(self):
        _content = "\033[1;33mScrimModel\033[0m(\n"
        for key, value in self.__dict__.items():
            _content += f"  \033[1;35m{key}\033[0m = {value},\n"
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
        if not self.start_time or not isinstance(self.start_time, str):
            raise ValueError(f"Invalid start time. Expected a string, got {type(self.start_time).__name__}.")
        if not self.end_time or not isinstance(self.end_time, str):
            raise ValueError(f"Invalid end time. Expected a string, got {type(self.end_time).__name__}.")
        if not self.total_slots or not isinstance(self.total_slots, int):
            raise ValueError(f"Invalid total slots. Expected an integer, got {type(self.total_slots).__name__}.")
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
            "name": self.name,
            "status": self.status,
            "mentions" : self.mentions,
            "guild_id": self.guild_id,
            "reg_channel": self.reg_channel,
            "slot_channel": self.slot_channel,
            "idp_role": self.idp_role,
            "ping_role": self.ping_role,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "total_slots": self.total_slots,
            "team_count": self.team_count,
            "time_zone": self.time_zone,
            "reserved": self.reserved,
            "auto_clean" : False
        }
    

    def save(self):
        if not self._id:
            _existing = ScrimModel.find_one(channel_id=self.reg_channel)
            if _existing and _existing == self:
                return
        self.validate()

        return _scrim_col.update_one(
            {"channel_id": self.reg_channel},
            {"$set": self.to_dict()},
            upsert=True
        )


    def delete(self):
        """
        Deletes the ScrimModel instance from the database.
        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        result = _scrim_col.delete_one({"reg_channel": self.reg_channel})
        return result.deleted_count > 0


    @staticmethod
    @functools.lru_cache(maxsize=128)
    def find_one(**kwargs:Unpack[ScrimPayload]) -> "ScrimModel":
        data = _scrim_col.find_one(kwargs)
        if data:
            return ScrimModel(**data)
        return None
    

    @staticmethod
    def find_by_start_time(start_time):
        return ScrimModel.find_one(start_time=start_time, status=True)


    @staticmethod
    def find(**kwargs: Unpack[ScrimPayload]) -> list["ScrimModel"]:
        """
        Finds all ScrimModel instances.
        Returns:
            list[ScrimModel]: A list of all ScrimModel instances.
        """
        data = _scrim_col.find(kwargs).to_list(length=None)
        return [ScrimModel(**item) for item in data]
    

# sm = ScrimModel.find()