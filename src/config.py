
from os import getenv
from typing import TYPE_CHECKING
from dotenv import load_dotenv


load_dotenv()
if TYPE_CHECKING:
    from models import Tester


OWNER_ID = 885193210455011369
DEVELOPERS = [ OWNER_ID ]

SHARDS = int(getenv("SHARDS", 1))
PREFIX = getenv("PREFIX", "&")
VERSION = getenv("VERSION", "2.1.0")
IS_DEV_ENV = getenv("MODE") == "development"

TRANSLATE_KEY = getenv("TRANSLATE_KEY", None)
BOT_TOKEN = getenv("BOT_TOKEN")
MONGO_URI = getenv("MONGO_URI", "mongodb://localhost:27017/")
GEMINI_KEY = getenv("GEMINI_KEY", None)
X_CLIENT_ID = getenv("X_CLIENT_ID", "")
X_CLIENT_SECRET = getenv("X_CLIENT_SECRET", "")
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "SPOTIFY_CLIENT_SECRET")

LOCAL_LAVA  = ["http://localhost:8787", "hunter87"] if getenv("LOCAL_LAVA", None) else None
DOMAIN = "sprucebot.tech"
BASE_URL = f"https://{DOMAIN}"
INVITE_URL = f"https://dsc.gg/sprucebot"

SUPPORT_SERVER = "https://discord.gg/vMnhpAyFZm"
SUPPORT_SERVER_ID = 947443790053015623

TESTERS :list["Tester"] = []
TESTING_GUILDS = [
    1380276604852502528,
    937038620756426832
]

# dependencies
LAVALINK_JAR = str(f"https://github.com/lavalink-devs/Lavalink/releases/download/{getenv('LAVALINK_VERSION', '4.1.1')}/Lavalink.jar")


# log channel ids
client_error_log = 1015166083050766366
client_start_log = 1020027121231462400
cmd_not_found_log = 1020698810625826846
guild_join_log = 1028673206850179152
guild_leave_log = 1028673254606508072
tourney_delete_log = 1112411458513408090
query_error_log = 1110257961290440824
paylog = 1233044089398755378


# LIMITS
MAX_TOURNEYS_PER_GUILD = 3
MAX_SCRIM_PER_GUILD = 3
MAX_SLOTS_PER_TOURNEY = 1000
MAX_SLOTS_PER_GROUP = 25
MAX_MENTIONS_COUNT = 11
MAX_UNBAN_LIMIT=200

# Esports Config
TAG_IGNORE_ROLE = "tag-ignore"
TOURNEY_MOD_ROLE = "tourney-mod"
SCRIM_MOD_ROLE = "scrim-mod"
SPRUCE_MOD_ROLE = "spruce-mod"
LOG_CHANNEL_NAME = "spruce-logs"
SCRIM_LOG_CHANNEL_NAME = "scrim-logs"
TOURNEY_LOG_CHANNEL_NAME = "tourney-logs"

LAVA_PLUGINS = {
    "lava_search.jar" : "https://github.com/topi314/LavaSearch/releases/download/1.0.0/lavasearch-plugin-1.0.0.jar",
    "lavasrc.jar" : "https://github.com/topi314/LavaSrc/releases/download/4.7.2/lavasrc-plugin-4.7.2.jar",
    "youtube.jar" : "https://github.com/lavalink-devs/youtube-source/releases/download/1.13.3/youtube-plugin-1.13.3.jar"
}
