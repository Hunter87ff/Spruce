from os import environ as env
from discord import Embed
from discord.ext import commands
from pymongo import MongoClient
from discord.ui import Button, View
from dotenv import load_dotenv
from requests import post as webpost #used by external modules
from requests import get as webget   #used by external modules
from ext import Logger
load_dotenv()
logger = Logger()
shards =  int(env["shards"]) or 20
version = env["version"] or "2.0.5"
print(version)
bot_id = 931202912888164474
owner_id = 885193210455011369
owner_tag = "hunter87ff"
support_server = "https://discord.gg/vMnhpAyFZm"
invite_url = "https://sprucebot.tech/invite"
support_server_id = 947443790053015623
status = ["500k+ Members", '&help', "You", "Tournaments", "Feedbacks", "Text2Speech","Music", "Translate"]
try: maindb = MongoClient(env["mongo_url"])
except:  maindb = MongoClient(env["MONGO_URL"])
dbc = maindb["tourneydb"]["tourneydbc"]
gtadbc =  maindb["gtamountdb"]["gtamountdbc"]
cfdbc = maindb["configdb"]["configdbc"]
cfdata = cfdbc.find_one({"config_id": 87})
spdb = MongoClient(cfdata["spdb"])
token = cfdata[env["tkn"]]
prefix = env["prefix"] or "&"
spot_id = cfdata["spot_id"]
spot_secret = cfdata["spot_secret"]
cogs_path = "./src/core" #cfdata["cogs"] #main prospective
bws = cfdata["bws"]
m_host = cfdata["m_host"]
m_host_psw = cfdata["m_host_psw"]
gh_api = cfdata["git_api"]
gh_action = "https://api.github.com/repos/hunter87ff/spruce/actions/workflows/py_application.yml/dispatches"
gh_action_run = "https://api.github.com/repos/hunter87ff/Spruce/actions/workflows/py_application.yml/runs"
GEMAPI = cfdata["gemapi"]

################## LOG ####################
erl = 1015166083050766366
stwbh = cfdata["stwbh"]
stl = 1020027121231462400
dml = cfdata["dml"]
cmdnf = 1020698810625826846
gjoin = 1028673206850179152
gleave = 1028673254606508072
votel = 1099588071986573362
tdlog = 1112411458513408090
################# emojis ####################
arow = "<a:arow:969894198515998720>"
bgmi = "<:bgmi:1008283336143282216>"
cross = "<:cross1:975460389565399141>"
cpu="<:cpu:1220349275368718366>"
cup = "<a:cup:999246631604080711>"
cod = "<:cod:1008283105452380250>"
defean = "<:defean:969894009331933205>"
dot_green="<:dot_green:1219980719728627813>"
developer = "<:dev:1020696239689433139>"
ff = "<:ff:1008282958349746176>"
invite="<:invites:968901936327848016> "
loading = "<a:loading:969894982024568856>"
like = "<:like:1014922246072053840>"
mod = "<:mod:999353993035780258>"
music_disk = "<a:music_disk:1020370054665207888>"
newstate = "<:newstate:1014922927776477205>"
owner = "<:owner:968371297744744448>"
partner = "<:partner:968372588533383178>"
wifi = "<:ping:1255441122692562944>"
ping = "<:g_latency:968371843335610408>"
pubg = "<:pubg:1008283449288835073>"
role = "<:role:1022568952573984828>"
reddot = "<:reddot:973870004606992444>"
ram="<:RAM:1220349738843504743>"
servers = "<:servers:1018845797556703262>"
setting = "<:setting:968374105961300008>"
tick = "<:tick:975460256748568656>"
user = "<:user:1006581167048368189>"
valo = "<:valorant:1008283511247081542>"
vf = "<:vf:959508659153535016>"
default_tick = "✅"
default_cross = "❌"
default_ticket = "🎟️"
heart = "❤️"
next_btn = "<:next:1120742875450310796>"
play_btn = "<:play_btn:1019504469299441674>"
pause_btn = "<:Pause:1019217055712559195>"
stop_btn = "<:stop:1019218566475681863>"
loop_btn = "<:loop_btn:1019219071046258708>"
queue_btn = "<:queue:1019219174070951967>"

#colors
blurple = 0x7289da
greyple = 0x99aab5
d_grey = 0x546e7a
d_theme = 0x36393F
l_grey = 0x979c9f
d_red = 0x992d22
red = 0xff0000
d_orange = 0xa84300
orange = 0xe67e22
d_gold = 0xc27c0e
gold = 0xf1c40f
magenta = 0xe91e63
purple = 0x9b59b6
d_blue = 0x206694
blue = 0x0000ff
green = 0x00ff00
d_green = 0x1f8b4c
pink = 0xff0066
teal = 0x1abc9c
cyan = 0x1abc9c
d_teal = 0x11806a
yellow = 0xffff00

votes = []
async def vote_add(bot):
    global votes
    vtl = bot.get_channel(votel)
    votes = [message async for message in vtl.history(limit=500)]
	
#functions
async def voted(ctx, bot):
	if cfdata["vote_only"] == False: return "yes"
	vtl = bot.get_channel(votel)
	# messages = [message async for message in vtl.history(limit=1000)]
	for i in votes:
		if i.author.id == 1096272690211471421:  #monitoring webhook id
			if f"<@{ctx.author.id}>" in i.content:
				if "day" not in str(ctx.message.created_at - i.created_at): return "yes"
				else: return None
		else: pass

async def vote_check(message):
    global votes
    if message.channel.id == votel:
        votes.append(message)
			
async def vtm(ctx):
	btn = Button(label="Vote Now", url=f"https://top.gg/bot/{bot_id}/vote")
	await ctx.send(embed=Embed(color=cyan, description="Vote Now To Unlock This Command"),view=View().add_item(btn))

def dev():
	def predicate(ctx):
		return ctx.message.author.id == owner_id
	return commands.check(predicate)

def notuser(message):
	return True if message.author.bot or message.webhook_id else False

