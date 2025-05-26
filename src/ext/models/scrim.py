import functools
from typing import TypedDict, Unpack
from ext.db import Database

_db_ = Database()
_scrim_col = _db_.scrims


class ScrimPayload(TypedDict, total=False):
        registration_channel:int 
        guild_id:int 
        start_time:int 
        end_time:int  
        registered_teams:int  
        slot_channel :int  
        total_slots:int  
        time_zone:str 
        start_message : str 
        end_message : str  


class ScrimModel:

    def __init__(self, **kwargs:Unpack[ScrimPayload]):
        self.registration_channel:int = kwargs.get("registration_channel") #primary key
        self.guild_id:int = kwargs.get("guild_id")
        self.start_time:int = kwargs.get("start_time")
        self.end_time:int = kwargs.get("end_time")
        self.registered_teams:int = kwargs.get("registered_teams", 0)
        self.slot_channel :int = kwargs.get("slot_channel", None)
        self.total_slots:int = kwargs.get("total_slots", 0)
        self.time_zone:str = kwargs.get("time_zone", "Asia/Kolkata")
        self.start_message : str = kwargs.get("start_message", "")
        self.end_message : str = kwargs.get("end_message", "")
        if kwargs.get("_id"):
            self._id:str = str(kwargs.get("_id", None))


    def __eq__(self, other):
        if not isinstance(other, ScrimModel):
            return NotImplemented
        return self.registration_channel == other.registration_channel


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
        if not self.registration_channel or not isinstance(self.registration_channel, int):
            return False
        if not self.guild_id or not isinstance(self.guild_id, int):
            return False
        if not self.start_time or not isinstance(self.start_time, int):
            return False
        if not self.end_time or not isinstance(self.end_time, int):
            return False
        if not self.total_slots or not isinstance(self.total_slots, int):
            return False
        if not self.time_zone or not isinstance(self.time_zone, str):
            return False
        return True

    

    def to_dict(self) -> dict:
        """
        Converts the ScrimModel instance to a dictionary.
        Returns:
            dict: A dictionary representation of the ScrimModel instance.
        """
        return {
            "registration_channel": self.registration_channel,
            "guild_id": self.guild_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "registered_teams": self.registered_teams,
            "slot_channel": self.slot_channel,
            "total_slots": self.total_slots,
            "time_zone": self.time_zone,
            "start_message": self.start_message,
            "end_message": self.end_message
        }
    

    def save(self):
        if not self._id:
            _existing = ScrimModel.find_one(channel_id=self.registration_channel)
            if _existing and _existing == self:
                return 

        return _scrim_col.update_one(
            {"channel_id": self.registration_channel},
            {"$set": self.to_dict()},
            upsert=True
        )


    def delete(self):
        """
        Deletes the ScrimModel instance from the database.
        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        result = _scrim_col.delete_one({"registration_channel": self.registration_channel})
        return result.deleted_count > 0


    @staticmethod
    @functools.lru_cache(maxsize=128)
    def find_one(**kwargs:Unpack[ScrimPayload]) -> "ScrimModel":
        data = _scrim_col.find_one(kwargs)
        if data:
            return ScrimModel(**data)
        return None
    

    @staticmethod
    @functools.lru_cache(maxsize=128)
    def find_by_start_time(start_time):
        return ScrimModel.find_one(start_time=start_time)
        


    @staticmethod
    @functools.lru_cache(maxsize=128)
    def find(
        **kwargs: Unpack[ScrimPayload]
    ) -> list["ScrimModel"]:
        """
        Finds all ScrimModel instances.
        Returns:
            list[ScrimModel]: A list of all ScrimModel instances.
        """
        data = _scrim_col.find(kwargs).to_list(length=None)
        return [ScrimModel(**item) for item in data]
    
