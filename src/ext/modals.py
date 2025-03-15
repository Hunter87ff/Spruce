"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2022 hunter87.dev@gmail.com
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.
"""
 

class Tourney:
    """
    Tourney class represents a tournament with various properties.
    """
    def __init__(self, obj: dict):
        self.obj = obj 

    @property
    def tname(self) -> str:
        """Returns the name of the tournament"""
        return self.obj.get("tname", "")

    @property
    def rch(self) -> int:
        """Returns the registration channel for the tournament"""
        return self.obj.get("rch", 0)
    
    @property
    def cch(self) -> int:
        """Returns the confirmation channel for the registered teams"""
        return self.obj.get("cch", 0)
    
    @property
    def crole(self) -> int:
        """Returns the confirmation role for the registered teams"""
        return self.obj.get("crole", 0)
    
    @property
    def gch(self) -> int:
        """Returns the group division channel for the tournament"""
        return self.obj.get("gch", 0)
    
    @property
    def tslot(self) -> int:
        """Returns the total slots for the tournament"""
        return self.obj.get("tslot", 0)
    
    @property
    def prefix(self) -> str:
        """Returns the prefix for the tournament"""
        return self.obj.get("prefix", "")
    
    @property
    def prize(self) -> str:
        """Returns the prize for the tournament"""
        return self.obj.get("prize", "")
    
    @property
    def faketag(self) -> str:
        """Returns the fake tag for the tournament"""
        return self.obj.get("faketag", "")
    
    @property
    def reged(self) -> int:
        """Returns the number of registered teams"""
        return self.obj.get("reged", 0)
    
    @property
    def status(self) -> str:
        """Returns the status of the tournament"""
        return self.obj.get("status", "")
    
    @property
    def pub(self) -> str:
        """Returns the publication status of the tournament"""
        return self.obj.get("pub", "")
    
    @property
    def spg(self) -> int:
        """Returns the slots per group for the tournament"""
        return self.obj.get("spg", 0)
    
    @property
    def auto_grp(self) -> int:
        """Returns the auto group division status of the tournament"""
        return self.obj.get("auto_grp", None)
    
    @property
    def cgp(self) -> int:
        """Returns the current group division status of the tournament"""
        return self.obj.get("cgp", None)


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
