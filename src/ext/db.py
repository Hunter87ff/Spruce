"""
This project is licensed under the GNU GPL v3.0.
Copyright (C) 2022-present hunter87.dev@gmail.com
Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.
"""

import os
from ext import Logger
from pymongo import MongoClient
from models import init


class Database:
    _instance = None
    mongo_uri:str = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.load_data()
        return cls._instance


    def load_data(self):
        """Initialize MongoDB connections and configuration data"""
        if hasattr(self, 'maindb'):  # Check if already loaded
            return
        try:
            # Primary MongoDB client and collections
            Logger.info("Database Connecting...")
            self.cluster = MongoClient(self.mongo_uri or os.environ["MONGO_URI"])
            self.sprucedb = self.cluster["sprucedb"]
            self.config_col =self.sprucedb["configs"]
            self.dbc = self.sprucedb["tourney"]
            self.primedbc = self.sprucedb["prime"]
            self.paydbc = self.sprucedb["payment"]
            self.guildbc = self.sprucedb["guilds"]
            self.testers = self.sprucedb["testers"]
            self.scrims = self.sprucedb["scrims"]
            self.autoroles = self.sprucedb["autoroles"]
            init(self)  # Initialize models
            Logger.info("Database Connected.")
   
        except Exception as e:
            Logger.warning(message=f"Error loading database or configuration data: {e}", _module="ext.db.Database")
