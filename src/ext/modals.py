"""
This project is licensed under the GNU GPL v3.0.
Copyright (C) 2022-present hunter87.dev@gmail.com
Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.
"""
from datetime import datetime
from pymongo.collection import Collection
from pymongo.asynchronous.collection import AsyncCollection
from ext.types import TournamentPayload


from typing import Unpack


class Tourney:
    """
    Tourney class represents a tournament with various properties.
    """
    _col : AsyncCollection | Collection = None
    tourneys = _col
    
    def __init__(self, obj: dict):
        self.obj = obj 
        self.name: str = obj.get("tname", obj.get("t_name", "Tournament"))
        self.guild_id: int = obj.get("guild_id", 0)
        self.registration_channel: int = obj.get("rch")
        self.confirmation_channel: int = obj.get("cch")
        self.confirmation_role: int = obj.get("crole")
        self.group_channel: int = obj.get("gch")
        self.slot_manager : int = obj.get("mch")
        self.total_slots:int = obj.get("tslot", 0)
        self.registered:int = obj.get("reged", 0)
        self.auto_group:str = obj.get("auto_grp", None)
        self.published:str = obj.get("pub", None)
        self.slot_per_group:int = obj.get("spg", 0)
        self.current_group:int = obj.get("cgp", None)
        self.created_at:datetime = obj.get("created_at", datetime.now())


    def to_dict(self):
        return {
            "tname": self.name,
            "guild": self.guild_id,
            "status": self.status,
            "rch": self.registration_channel,
            "cch": self.confirmation_channel,
            "crole": self.confirmation_role,
            "gch": self.group_channel,
            "mch": self.slot_manager,
            "tslot": self.total_slots,
            "reged": self.registered,
            "auto_grp": self.auto_group,
            "pub": self.published,
            "spg": self.slot_per_group,
            "cgp": self.current_group,
            "created_at": self.created_at,
        }

    def __str__(self):
        return f"Tourney({str(self.obj)})"
    

    def get(self, key: str):
        """
        Get the value of a specific key from the tournament object.
        """
        return self.obj.get(key, None)
    
    
    def set(self, key: str, value):
        """
        Set the value of a specific key in the tournament object.
        """
        self.obj[key] = value
        Tourney._col.update_one({"rch": self.rch}, {"$set": {key: value}})


    def save(self):
        """
        Save the tournament object to the database.
        """
        Tourney._col.update_one({"rch": self.rch}, {"$set": self.obj}, upsert=True)



    @staticmethod
    def findOne(registration_channel:int):
        """
        Find a tournament by registration channel and guild ID.
        """
        result = Tourney._col.find_one({"rch": registration_channel})
        return Tourney(result) if result else None
    

    @classmethod
    async def find_one(cls, **kwargs: Unpack[TournamentPayload]) -> "Tourney":
        if isinstance(cls._col, AsyncCollection):
            result =  await cls._col.find_one(kwargs)
        else:
            result = cls._col.find_one(kwargs)

        return cls(**result) if result else None



    @property
    def tname(self) -> str:
        """Returns the name of the tournament"""
        return self.obj.get("tname", self.obj.get("t_name", "Tournament"))

    @tname.setter
    def tname(self, value: str):
        """Sets the name of the tournament"""
        self.obj["tname"] = value
        Tourney._col.update_one({"rch": self.rch}, {"$set": {"tname": value}})

    @property
    def mentions(self) -> int:
        """Returns the number mentions required to register in mention based tournament"""
        return self.obj.get("mentions", 0)

    @mentions.setter
    def mentions(self, value: int):
        """Sets the number of mentions required"""
        self.obj["mentions"] = value
        Tourney._col.update_one({"rch": self.rch}, {"$set": {"mentions": value}})

    @property
    def rch(self) -> int:
        """Returns the registration channel for the tournament"""
        return self.obj.get("rch", 0)

    @rch.setter
    def rch(self, value: int):
        """Sets the registration channel"""
        self.obj["rch"] = value
        Tourney._col.update_one({"rch": self.rch}, {"$set": {"rch": value}})

    @property
    def cch(self) -> int:
        """Returns the confirmation channel for the registered teams"""
        return self.obj.get("cch", 0)

    @cch.setter
    def cch(self, value: int):
        """Sets the confirmation channel"""
        self.obj["cch"] = value
        Tourney._col.update_one({"rch": self.rch}, {"$set": {"cch": value}})

    @property
    def crole(self) -> int:
        """Returns the confirmation role for the registered teams"""
        return self.obj.get("crole", 0)

    @crole.setter
    def crole(self, value: int):
        """Sets the confirmation role"""
        self.obj["crole"] = value
        Tourney._col.update_one({"rch": self.rch}, {"$set": {"crole": value}})

    @property
    def gch(self) -> int:
        """Returns the group division channel for the tournament"""
        return self.obj.get("gch", 0)

    @gch.setter
    def gch(self, value: int):
        """Sets the group division channel"""
        self.obj["gch"] = value
        Tourney._col.update_one({"rch": self.rch}, {"$set": {"gch": value}})

    @property
    def tslot(self) -> int:
        """Returns the total slots for the tournament"""
        return self.obj.get("tslot", 0)

    @tslot.setter
    def tslot(self, value: int):
        """Sets the total slots"""
        self.obj["tslot"] = value
        Tourney._col.update_one({"rch": self.rch}, {"$set": {"tslot": value}})

    @property
    def prefix(self) -> str:
        """Returns the prefix for the tournament"""
        return self.obj.get("prefix", "")

    @prefix.setter
    def prefix(self, value: str):
        """Sets the prefix"""
        self.obj["prefix"] = value
        Tourney._col.update_one({"rch": self.rch}, {"$set": {"prefix": value}})

    @property
    def prize(self) -> str:
        """Returns the prize for the tournament"""
        return self.obj.get("prize", "")

    @prize.setter
    def prize(self, value: str):
        """Sets the prize"""
        self.obj["prize"] = value
        Tourney._col.update_one({"rch": self.rch}, {"$set": {"prize": value}})

    @property
    def faketag(self) -> str:
        """Returns the fake tag for the tournament"""
        return self.obj.get("faketag", "yes")

    @faketag.setter
    def faketag(self, value: str):
        """Sets the fake tag"""
        self.obj["faketag"] = value
        Tourney._col.update_one({"rch": self.rch}, {"$set": {"faketag": value}})

    @property
    def reged(self) -> int:
        """Returns the number of registered teams"""
        return self.obj.get("reged", 0)

    @reged.setter
    def reged(self, value: int):
        """Sets the number of registered teams"""
        self.obj["reged"] = value
        Tourney._col.update_one({"rch": self.rch}, {"$set": {"reged": value}})

    @property
    def status(self) -> str:
        """Returns the status of the tournament"""
        return self.obj.get("status", "")

    @status.setter
    def status(self, value: str):
        """Sets the status"""
        self.obj["status"] = value
        Tourney._col.update_one({"rch": self.rch}, {"$set": {"status": value}})

    @property
    def pub(self) -> str:
        """Returns the publication status of the tournament"""
        return self.obj.get("pub", "")

    @pub.setter
    def pub(self, value: str):
        """Sets the publication status"""
        self.obj["pub"] = value
        Tourney._col.update_one({"rch": self.rch}, {"$set": {"pub": value}})

    @property
    def spg(self) -> int:
        """Returns the slots per group for the tournament"""
        return self.obj.get("spg", 0)

    @spg.setter
    def spg(self, value: int):
        """Sets the slots per group"""
        self.obj["spg"] = value
        Tourney._col.update_one({"rch": self.rch}, {"$set": {"spg": value}})

    @property
    def auto_grp(self) -> int:
        """Returns the auto group division status of the tournament"""
        return self.obj.get("auto_grp", None)

    @auto_grp.setter
    def auto_grp(self, value: int):
        """Sets the auto group division status"""
        self.obj["auto_grp"] = value
        Tourney._col.update_one({"rch": self.rch}, {"$set": {"auto_grp": value}})

    @property
    def cgp(self) -> int:
        """Returns the current group division status of the tournament"""
        return self.obj.get("cgp", None)

    @cgp.setter
    def cgp(self, value: int):
        """Sets the current group division status"""
        self.obj["cgp"] = value
        Tourney._col.update_one({"rch": self.rch}, {"$set": {"cgp": value}})

