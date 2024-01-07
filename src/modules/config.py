from os import environ as env
import pymongo,discord
from discord.ext import commands
from pymongo import MongoClient
from discord.ui import Button, View
shards = 10
version = "2.0.1"
bot_id = 931202912888164474
owner_id = 885193210455011369
owner_tag = "hunter87ff"
support_server = "https://discord.gg/vMnhpAyFZm"
invite_url = "https://sprucebot.tech/invite"
support_server_id = 947443790053015623
status = ["500k+ Members", '&help', "You", "Tournaments", "Feedbacks", "Text2Speech","Music", "Translate"]
maindb = ""
try: maindb = MongoClient(env["mongo_url"])
except:  maindb = MongoClient(env["MONGO_URL"])
dbc = maindb["tourneydb"]["tourneydbc"]
cfdbc = maindb["configdb"]["configdbc"]
cfdata = cfdbc.find_one({"config_id": 87})
spdb = MongoClient(cfdata["spdb"])
token = cfdata["TOKEN2"]
prefix = cfdata["prefix"]
spot_id = cfdata["spot_id"]
spot_secret = cfdata["spot_secret"]
cogs_path = cfdata["cogs"] #main prospective
bws = cfdata["bws"]
m_host = cfdata["m_host"]
m_host_psw = cfdata["m_host_psw"]
#openai_key = cfdata["openai_key"]
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
vf = "<:vf:959508659153535016>"
cross = "<:cross1:975460389565399141>"
owner = "<:owner:968371297744744448>"
tick = "<:tick:975460256748568656>"
partner = "<:partner:968372588533383178>"
ping = "<:g_latency:968371843335610408>"
music_disk = "<a:music_disk:1020370054665207888>"
cup = "<a:cup:999246631604080711>"
role = "<:role:1022568952573984828>"
pubg = "<:pubg:1008283449288835073>"
bgmi = "<:bgmi:1008283336143282216>"
developer = "<:dev:1020696239689433139>"
ff = "<:ff:1008282958349746176>"
like = "<:like:1014922246072053840>"
mod = "<:mod:999353993035780258>"
servers = "<:servers:1018845797556703262>"
cod = "<:cod:1008283105452380250>"
newstate = "<:newstate:1014922927776477205>"
setting = "<:setting:968374105961300008>"
valo = "<:valorant:1008283511247081542>"
reddot = "<:reddot:973870004606992444>"
user = "<:user:1006581167048368189>"
defean = "<:defean:969894009331933205>"
loading = "<a:loading:969894982024568856>"
default_tick = "✅"
default_cross = "❌"
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


#functions
async def voted(ctx, bot):
	if cfdata["vote_only"] == False: return "yes"
	vtl = bot.get_channel(votel)
	messages = [message async for message in vtl.history(limit=1000)]
	for i in messages:
		if i.author.id == 1096272690211471421:  #monitoring webhook id
			if f"<@{ctx.author.id}>" in i.content:
				if "day" not in str(ctx.message.created_at - i.created_at): return "yes"
				else: return None
		else: return None


async def vtm(ctx):
	btn = Button(label="Vote Now", url=f"https://top.gg/bot/{bot_id}/vote")
	await ctx.send(embed=discord.Embed(
	 color=cyan, description="Vote Now To Unlock This Command"),
	               view=View().add_item(btn))


def dev():
	def predicate(ctx):
		return ctx.message.author.id == owner_id
	return commands.check(predicate)


def notuser(message):
	if message.author.bot: return True
	if message.webhook_id: return True
	else: return None
