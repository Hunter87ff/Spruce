
import discord
from discord.ext import commands
#from asyncio import sleep
import pymongo
from pymongo import MongoClient
import re
import datetime
from modules import config




maindb = config.maindb
#maindb = MongoClient(os.environ["mongo_url"])
db = maindb["tourneydb"]

dbc = maindb["tourneydb"]["tourneydbc"]
tourneydbc=dbc

gtamountdbc = maindb["gtamountdb"]["gtamountdbc"]
gtadbc = gtamountdbc






async def ch_handel(channel):
	tourch = dbc.find_one({"tid" : channel.id%1000000000000 })

	if tourch != None:
		gtad = gtadbc.find_one({"guild" : channel.guild.id%1000000000000})
		gta = gtad["gta"]
		gtadbc.update_one({"guild" : channel.guild.id%1000000000000}, {"$set" : {"gta" : gta - 1}})
		print("A Tournament Deleted")
		dbc.delete_one({"tid" : channel.id%1000000000000 })
		print("dbc document deleted")
