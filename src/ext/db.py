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
    cluster: MongoClient = None

    def __init__(self, mongo_uri: str = None):

        """Initialize MongoDB connections and configuration data"""
        if not Database.cluster:
            try:
                # Primary MongoDB client and collections
                Logger.info("Database Connecting...")
                Database.cluster = MongoClient(mongo_uri or os.environ["MONGO_URI"])
                Logger.info("Database Connected.")

            except Exception as e:
                Logger.warning(message=f"Error loading database or configuration data: {e}", _module="ext.db.Database")
                return
            
        self.sprucedb = self.cluster["sprucedb"]
        self.config_col =self.sprucedb["configs"]
        self.dbc = self.sprucedb["tourney"]
        self.primedbc = self.sprucedb["prime"]
        self.testers = self.sprucedb["testers"]
        self.scrims = self.sprucedb["scrims"]
        self.autoroles = self.sprucedb["autoroles"]
        self.tournaments = self.sprucedb["tournaments"]
        self.teams = self.sprucedb["teams"]
        init(self)  # Initialize models