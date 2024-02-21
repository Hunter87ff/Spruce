from modules import config
__all__ = ("Database",)


class Tourney:
    def __init__(self, obj):
        self.tname = obj["t_name"]
        self.rch = obj["rch"]
        self.tid = obj["tid"]
        self.cch = obj["cch"]
        self.crole = obj["crole"]
        self.gch = obj["gch"]
        self.tslot = obj["tslot"]
        self.prefix = obj["prefix"]
        self.faketag = obj["faketag"]
        self.reged = obj["reged"]
        self.status = obj["status"]
        self.pub = obj["pub"]
        self.spg = obj["spg"]
        self.auto_grp = obj["auto_grp"]
        self.cgp = obj["cgp"]


class Database:
    def __init__(self):
        self.db = config.maindb
        self.sdb = config.spdb
        self.dbc = self.db["tourneydb"]["tourneydbc"]
        
    def find_one(self, obj) -> Tourney:
        return Tourney(self.db["tourneydb"]["tourneydbc"].find_one(obj))

    def find(self, obj) -> list[Tourney]:
        return [Tourney(i) for i in self.db["tourneydb"]["tourneydbc"].find(obj)]

    def insert(self, obj) -> None:
        return self.db["tourneydb"]["tourneydbc"].insert_one(obj)

    def update_one(self, obj, obj2) -> None:
        self.db["tourneydb"]["tourneydbc"].update_one(obj, obj2)

    def update_many(self, obj, obj2) -> None:
        self.db["tourneydb"]["tourneydbc"].update_many(obj, obj2)

    def delete_one(self, obj)  -> None:
        self.db["tourneydb"]["tourneydbc"].delete_one(obj)


