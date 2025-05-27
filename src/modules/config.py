
from os import environ as env
from dotenv import load_dotenv
load_dotenv()
from ext.emoji import *
from ext.color import *
from ext import Logger
from ext import Database
logger = Logger


SHARDS = int(env.get("SHARDS", 1))
VERSION = env.get("version", "2.0.6")
OWNER_ID = 885193210455011369
DEVELOPERS = [
     885193210455011369
]
IS_DEV_ENV = env.get("MODE") == "development"
LOCAL_LAVA  = ["http://localhost:8787", "hunter87"] if env.get("LOCAL_LAVA", None) else None
DOMAIN = "sprucebot.tech"
BASE_URL = f"https://{DOMAIN}"
INVITE_URL = f"{BASE_URL}/invite"
SUPPORT_SERVER = "https://discord.gg/vMnhpAyFZm"
SUPPORT_SERVER_ID = 947443790053015623
PREFIX = env.get("PREFIX", "&")
SLEEP_TIME = 21464 


################## LOG ####################
###########################################
client_error_log = 1015166083050766366
client_start_log = 1020027121231462400
cmd_not_found_log = 1020698810625826846
guild_join_log = 1028673206850179152
guild_leave_log = 1028673254606508072
tourney_delete_log = 1112411458513408090
paylog = 1233044089398755378


def get_db():
    """
    Returns a Database Object
    """
    return Database()