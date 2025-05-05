"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2022 hunter87.dev@gmail.com
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.
"""
from ext.db import Database
tourneys = Database().dbc


class Tourney:
    """
    Tourney class represents a tournament with various properties.
    """
    def __init__(self, obj: dict):
        self.obj = obj 

    @staticmethod
    def findOne(registration_channel:int):
        """
        Find a tournament by registration channel and guild ID.
        """
        result = tourneys.find_one({"rch": registration_channel})
        return Tourney(result) if result else None

    @property
    def tname(self) -> str:
        """Returns the name of the tournament"""
        return self.obj.get("tname", "")

    @tname.setter
    def tname(self, value: str):
        """Sets the name of the tournament"""
        self.obj["tname"] = value
        tourneys.update_one({"rch": self.rch}, {"$set": {"tname": value}})

    @property
    def mentions(self) -> int:
        """Returns the number mentions required to register in mention based tournament"""
        return self.obj.get("mentions", 0)

    @mentions.setter
    def mentions(self, value: int):
        """Sets the number of mentions required"""
        self.obj["mentions"] = value
        tourneys.update_one({"rch": self.rch}, {"$set": {"mentions": value}})

    @property
    def rch(self) -> int:
        """Returns the registration channel for the tournament"""
        return self.obj.get("rch", 0)

    @rch.setter
    def rch(self, value: int):
        """Sets the registration channel"""
        self.obj["rch"] = value
        tourneys.update_one({"rch": self.rch}, {"$set": {"rch": value}})

    @property
    def cch(self) -> int:
        """Returns the confirmation channel for the registered teams"""
        return self.obj.get("cch", 0)

    @cch.setter
    def cch(self, value: int):
        """Sets the confirmation channel"""
        self.obj["cch"] = value
        tourneys.update_one({"rch": self.rch}, {"$set": {"cch": value}})

    @property
    def crole(self) -> int:
        """Returns the confirmation role for the registered teams"""
        return self.obj.get("crole", 0)

    @crole.setter
    def crole(self, value: int):
        """Sets the confirmation role"""
        self.obj["crole"] = value
        tourneys.update_one({"rch": self.rch}, {"$set": {"crole": value}})

    @property
    def gch(self) -> int:
        """Returns the group division channel for the tournament"""
        return self.obj.get("gch", 0)

    @gch.setter
    def gch(self, value: int):
        """Sets the group division channel"""
        self.obj["gch"] = value
        tourneys.update_one({"rch": self.rch}, {"$set": {"gch": value}})

    @property
    def tslot(self) -> int:
        """Returns the total slots for the tournament"""
        return self.obj.get("tslot", 0)

    @tslot.setter
    def tslot(self, value: int):
        """Sets the total slots"""
        self.obj["tslot"] = value
        tourneys.update_one({"rch": self.rch}, {"$set": {"tslot": value}})

    @property
    def prefix(self) -> str:
        """Returns the prefix for the tournament"""
        return self.obj.get("prefix", "")

    @prefix.setter
    def prefix(self, value: str):
        """Sets the prefix"""
        self.obj["prefix"] = value
        tourneys.update_one({"rch": self.rch}, {"$set": {"prefix": value}})

    @property
    def prize(self) -> str:
        """Returns the prize for the tournament"""
        return self.obj.get("prize", "")

    @prize.setter
    def prize(self, value: str):
        """Sets the prize"""
        self.obj["prize"] = value
        tourneys.update_one({"rch": self.rch}, {"$set": {"prize": value}})

    @property
    def faketag(self) -> str:
        """Returns the fake tag for the tournament"""
        return self.obj.get("faketag", "")

    @faketag.setter
    def faketag(self, value: str):
        """Sets the fake tag"""
        self.obj["faketag"] = value
        tourneys.update_one({"rch": self.rch}, {"$set": {"faketag": value}})

    @property
    def reged(self) -> int:
        """Returns the number of registered teams"""
        return self.obj.get("reged", 0)

    @reged.setter
    def reged(self, value: int):
        """Sets the number of registered teams"""
        self.obj["reged"] = value
        tourneys.update_one({"rch": self.rch}, {"$set": {"reged": value}})

    @property
    def status(self) -> str:
        """Returns the status of the tournament"""
        return self.obj.get("status", "")

    @status.setter
    def status(self, value: str):
        """Sets the status"""
        self.obj["status"] = value
        tourneys.update_one({"rch": self.rch}, {"$set": {"status": value}})

    @property
    def pub(self) -> str:
        """Returns the publication status of the tournament"""
        return self.obj.get("pub", "")

    @pub.setter
    def pub(self, value: str):
        """Sets the publication status"""
        self.obj["pub"] = value
        tourneys.update_one({"rch": self.rch}, {"$set": {"pub": value}})

    @property
    def spg(self) -> int:
        """Returns the slots per group for the tournament"""
        return self.obj.get("spg", 0)

    @spg.setter
    def spg(self, value: int):
        """Sets the slots per group"""
        self.obj["spg"] = value
        tourneys.update_one({"rch": self.rch}, {"$set": {"spg": value}})

    @property
    def auto_grp(self) -> int:
        """Returns the auto group division status of the tournament"""
        return self.obj.get("auto_grp", None)

    @auto_grp.setter
    def auto_grp(self, value: int):
        """Sets the auto group division status"""
        self.obj["auto_grp"] = value
        tourneys.update_one({"rch": self.rch}, {"$set": {"auto_grp": value}})

    @property
    def cgp(self) -> int:
        """Returns the current group division status of the tournament"""
        return self.obj.get("cgp", None)

    @cgp.setter
    def cgp(self, value: int):
        """Sets the current group division status"""
        self.obj["cgp"] = value
        tourneys.update_one({"rch": self.rch}, {"$set": {"cgp": value}})


class Scrim:
    def __init__(self, obj:dict):
        self.guild_id:int = obj.get("guild_id")
        self.slot:int = obj.get("slot")
        self.time:str = obj.get("time")
        self.zone:str = obj.get("zone")
        self.channel_id:int = obj.get("channel_id")
        self.role_id:int = obj.get("role_id")
        self.status:str = obj.get("status")
        self.started:bool = obj.get("started")
        self.reged:int = obj.get("reged")


class ScrimOpenPayload:
    def __init__(self, obj:dict):
        self.started=bool(obj.get("started", False))
        self.slot:int = obj.get("slot")
        self.channel_id:int = obj.get("channel_id")
