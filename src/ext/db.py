"""
This project is licensed under the GNU GPL v3.0.
Copyright (C) 2022 hunter87.dev@gmail.com
Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.
"""

from pymongo import MongoClient
import os
from ext import Logger

class Database:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            # cls._instance._registers = None  # Initialize _registers
            cls._instance.load_data()
        return cls._instance


    def load_data(self):
        """Initialize MongoDB connections and configuration data"""
        if hasattr(self, 'maindb'):  # Check if already loaded
            return
        try:
            # Primary MongoDB client and collections
            Logger.info("Database Connecting...")
            self.maindb = MongoClient(os.environ["MONGO_URI"])
            self.sprucedb = self.maindb["sprucedb"]
            self.config_col =self.sprucedb["configs"]

            self.dbc = self.sprucedb["tourney"]
            self.primedbc = self.sprucedb["prime"]
            self.paydbc = self.sprucedb["payment"]
            self.scrims = self.sprucedb["scrims"]
            self.guildbc = self.sprucedb["guilds"]
            self.testers = self.sprucedb["testers"]
            
            Logger.info("Database Connected.")
   
        except Exception as e:
            Logger.warning(message=f"Error loading database or configuration data: {e}", _module="ext.db.Database")


    # @property
    # def registers(self):
    #     """Returns the set of registration channel ids"""
    #     if self._registers: return self._registers
    #     else:
    #         self._registers:set[int] = set([x['rch'] for x in list(self.dbc.find({}, {"_id":0, "rch":1}))])
    #         return self._registers
