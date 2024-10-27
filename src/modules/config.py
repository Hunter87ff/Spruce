from os import environ as env
import sys
from dotenv import load_dotenv
load_dotenv()

import discord
from discord import Embed, Message
from discord.ext import commands
from discord.ui import Button, View
from requests import post as webpost #used by external modules
from requests import get as webget   #used by external modules
from ext.emoji import *
from ext.color import *
from ext import Logger
from ext import Database

logger = Logger
shards =  int(env.get("shards")) or 20
version = env.get("version", "2.0.6")
bot_id = 931202912888164474
owner_id = 885193210455011369
owner_tag = "hunter87ff"
MAINTAINER = "hunter87ff"
LOCAL_LAVA  = False
BASE_URL = "https://sprucbot.tech"
support_server = "https://discord.gg/vMnhpAyFZm"
invite_url = f"{BASE_URL}/invite"
invite_url2 = f"https://discord.com/oauth2/authorize?client_id={bot_id}&permissions=8&scope=bot"
support_server_id = 947443790053015623
status = ["550k+ Members", '&help', "You", "Tournaments", "Feedbacks", "Text2Speech","Music", "Translate"]
prefix = env.get("prefix", "&")


DOMAIN = "sprucbot.tech"
gh_action = f"https://api.github.com/repos/{MAINTAINER}/spruce/actions/workflows/py_application.yml/dispatches"
gh_action_run = f"https://api.github.com/repos/{MAINTAINER}/Spruce/actions/workflows/py_application.yml/runs"


################## LOG ####################
erl = 1015166083050766366
stl = 1020027121231462400
cmdnf = 1020698810625826846
gjoin = 1028673206850179152
gleave = 1028673254606508072
votel = 1099588071986573362
tdlog = 1112411458513408090
paylog = 1233044089398755378
################# emojis ####################



# TEXT CONSTANTS
PROCESSING = "Processing..."



def get_db():
    """
    Returns a Database Object
    """
    return Database()


votes = []
async def vote_add(bot:commands.Bot):
    global votes
    vtl = bot.get_channel(votel)
    votes = [message async for message in vtl.history(limit=500)]
	
#functions
async def voted(ctx:commands.Context, bot:commands.Bot):
	if get_db().cfdata["vote_only"] == False: return "yes"
	vtl = bot.get_channel(votel)
	for i in votes:
		if i.author.id == 1096272690211471421:  #monitoring webhook id
			if f"<@{ctx.author.id}>" in i.content:
				if "day" not in str(ctx.message.created_at - i.created_at): return "yes"
				else: return None
		else: pass

async def vote_check(message:Message):
    global votes
    if message.channel.id == votel:
        votes.append(message)
			
async def vtm(ctx:commands.Context):
	btn = Button(label="Vote Now", url=f"https://top.gg/bot/{bot_id}/vote")
	await ctx.send(embed=Embed(color=cyan, description="Vote Now To Unlock This Command"),view=View().add_item(btn))

def dev():
	def predicate(ctx:commands.Context):
		return ctx.message.author.id in get_db().cfdata["devs"]
	return commands.check(predicate)

def owner_only():
    def predicate(ctx:commands.Context):
        return (ctx.message.author.id == owner_id)
    return commands.check(predicate)

def notuser(message:Message):
	return True if message.author.bot or message.webhook_id else False

async def is_dev(ctx:commands.Context | discord.Interaction):
    if isinstance(ctx, discord.Interaction): 
        if ctx.user.id not in get_db().cfdata["devs"]:
              await ctx.response.send_message("Command is under development", ephemeral=True)
              return False

    elif isinstance(ctx, commands.Context): 
        if ctx.author.id not in get_db().cfdata["devs"]:
              await ctx.send("Command is under development", ephemeral=True)
              return False
    return True
    
