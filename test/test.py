from modules import config
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
        self.dbc = self.db["tourneydb"]["tourneydbc"]

    def tfind(self, obj):
        return Tourney(self.db["tourneydb"]["tourneydbc"].find_one(obj))

print(Database().tfind({"rch":1207725131456315482}).tname)