"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2022 hunter87.dev@gmail.com
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.
"""


class Tourney:
    def __init__(self, obj:dict):
        self.tname: str = obj.get("t_name", "")
        self.rch: int = obj.get("rch", 0)
        self.mentions: int = obj.get("mentions", 0)
        self.cch: int = obj.get("cch", 0)
        self.crole: int = obj.get("crole", 0)
        self.gch: int = obj.get("gch", 0)
        self.tslot: int = obj.get("tslot", 0)
        self.prefix: str = obj.get("prefix", "")
        self.prize: str = obj.get("prize", "")
        self.faketag: str = obj.get("faketag", "")
        self.reged: int = obj.get("reged", 0)
        self.status: str = obj.get("status", "")
        self.pub: str = obj.get("pub", "")
        self.spg: int = obj.get("spg", 0)
        self.auto_grp = obj.get("auto_grp", None)
        self.cgp = obj.get("cgp", None)