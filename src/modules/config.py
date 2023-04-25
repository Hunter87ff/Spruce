import pymongo
import os
from pymongo import MongoClient



version = "2.0.4"

owner_id = 885193210455011369
owner_tag = "hunter#6967"

bot_id = 931202912888164474

support_server = "https://discord.gg/vMnhpAyFZm"
support_server_id = 947443790053015623
prefix = "&"

maindb = MongoClient(os.environ["mongo_url"])

spot_id = os.environ["spot_id"]
spot_secret = os.environ["spot_secret"]
m_host = 'node1.kartadharta.xyz'        
m_host_psw =  "kdlavalink"    
################## LOG ####################

erl = 1015166083050766366
stl = 1020027121231462400
cmdnf = 1020698810625826846
gjoin = 1028673206850179152
gleave = 1028673254606508072
################# emojis ####################
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
dev = "<:dev:1020696239689433139>"
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

#colors
blurple = 0x7289da
greyple = 0x99aab5
d_grey = 0x546e7a
d_theme = 0x36393F
l_grey = 0x979c9f
d_red = 0x992d22
red = 0xff0000
d_orange = 0xa84300
orange= 0xe67e22
d_gold = 0xc27c0e
gold = 0xf1c40f
magenta = 0xe91e63
purple = 0x9b59b6
d_blue = 0x206694 
blue = 0x0000ff
green = 0x00ff00
d_green = 0x1f8b4c
pink=0xff0066
teal = 0x1abc9c
d_teal = 0x11806a
yellow = 0xffff00
