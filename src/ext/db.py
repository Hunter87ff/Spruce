"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

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
            cls._instance.load_data()
        return cls._instance

    def load_data(self):
        """Initialize MongoDB connections and configuration data"""
        if hasattr(self, 'maindb'):  # Check if already loaded
            return
        try:
            # Primary MongoDB client and collections
            Logger.info("Database Connecting...")
            self.maindb = MongoClient(os.environ["mongo_url"])
            self.sprucedb = self.maindb["sprucedb"]
            self.cfdbc = self.sprucedb["configs"]

            self.dbc = self.sprucedb["tourney"]
            self.primedbc = self.sprucedb["prime"]
            self.paydbc = self.sprucedb["payment"]
            self.scrims = self.sprucedb["scrims"]
            self.guildbc = self.sprucedb["guilds"]

            # Load configuration data from the main config collection
            config_doc = self.cfdbc.find_one({"config_id": 87})
            if config_doc is None:
                Logger.warning("No config found with config_id 87, using empty config.")
                config_doc = {}

            self.cfdata = dict(config_doc)
            self.token = self.cfdata.get(os.environ.get("TOKEN_KEY", "token")) or "YOUR_DISCORD_BOT_TOKEN"

            self.GEMAPI = self.cfdata.get("gemapi")
            self.spot_id = self.cfdata.get("spot_id")
            self.spot_secret = self.cfdata.get("spot_secret")
            self.bws = self.cfdata.get("bws")
            self.m_host = self.cfdata.get("m_host")
            self.m_host_psw = self.cfdata.get("m_host_psw")
            self.gh_api = self.cfdata.get("gh_api")
            self.gh_token = self.cfdata.get("gh_token", self.gh_api)

            Logger.info("Database Connected.")

        except Exception as e:
            Logger.warning(message=f"Error loading database or configuration data: {e}", _module="ext.db.Database")

    @property
    def registers(self):
        """Returns the set of registration channel ids"""
        if hasattr(self, '_registers') and self._registers:
            return self._registers
        else:
            self._registers = set([x['rch'] for x in list(self.dbc.find({}, {"_id":0, "rch":1}))])
            return self._registers