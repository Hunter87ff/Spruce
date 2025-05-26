
from os import environ as env
from dotenv import load_dotenv
load_dotenv()
from ext.emoji import *
from ext.color import *
from ext import Logger
from ext import Database

logger = Logger
SHARDS = int(env.get("SHARDS", 20))
VERSION = env.get("version", "2.0.6")
OWNER_ID = 885193210455011369
MAINTAINER = "hunter87ff"
IS_DEV_ENV = env.get("MODE") == "development"
LOCAL_LAVA  = ["http://localhost:8787", "hunter87"] if env.get("LOCAL_LAVA", None) else None
DOMAIN = "sprucebot.tech"
BASE_URL = f"https://{DOMAIN}"
INVITE_URL = f"{BASE_URL}/invite"
SUPPORT_SERVER = "https://discord.gg/vMnhpAyFZm"
SUPPORT_SERVER_ID = 947443790053015623
PREFIX = env.get("PREFIX", "&")
SLEEP_TIME = 21464 #service restart
gh_action = f"https://api.github.com/repos/{MAINTAINER}/spruce/actions/workflows/py_application.yml/dispatches"

class activeModules:
      music = False # due to some issues this module will be disabled for a while
      tourney = True
      scrims = False
      moderation = True
      utils = True
      role = True



################## LOG ####################
error_log_channel_id = 1015166083050766366
start_log_channel_id = 1020027121231462400
cmdnf = 1020698810625826846
gjoin = 1028673206850179152
gleave = 1028673254606508072
votel = 1099588071986573362
tdlog = 1112411458513408090
paylog = 1233044089398755378


def get_db():
    """
    Returns a Database Object
    """
    return Database()