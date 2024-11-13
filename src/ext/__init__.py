from ext.logger import Logger
import ext.constants as constants
import ext.emoji as emoji
import ext.color as color
from ext.db import Database
import ext.error as error
import ext.permissions as permissions
import locale

__all__ = (
    "Database", 
    "Tourney", 
    "Logger",
    "constants",
    "emoji",
    "color",
    "locale",
    "permissions",
    "error"
    )

class Tourney:
    def __init__(self, obj):
        self.tname:str = obj["t_name"]
        self.rch:int = obj["rch"]
        self.mentions:int = obj["mentions"]
        self.cch:int = obj["cch"]
        self.crole:int = obj["crole"]
        self.gch:int= obj["gch"]
        self.tslot:int = obj["tslot"]
        self.prefix:str = obj["prefix"]
        self.prize:str = obj["prize"]
        self.faketag:str = obj["faketag"]
        self.reged:int = obj["reged"]
        self.status:str = obj["status"]
        self.pub:str = obj["pub"]
        self.spg:int = obj["spg"]
        self.auto_grp = obj["auto_grp"]
        self.cgp = obj["cgp"]


