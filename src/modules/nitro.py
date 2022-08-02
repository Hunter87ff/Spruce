
import os 
import discord
from discord.ext import commands
#from asyncio import sleep
#import datetime
#from datetime import datetime, timedelta
import pymongo
from pymongo import MongoClient
#from discord.ui import Button, View



dburl = os.environ["mongo_url"]
maindb = MongoClient(dburl)
nitrodbc = maindb["nitrodb"]["nitrodbc"]








async def nitrof(message):
    webhook = discord.utils.get(await message.channel.webhooks(), name="Spruce")
    if webhook == None:
        webhook = await message.channel.create_webhook(name="Spruce")
    wurl = webhook.url
   
            
    words = message.content.split()
    for word in words:
        if word[0] == ":" and word[-1] == ":":
            emjn = word.replace(":", "")
            emoji = discord.utils.get(bot.emojis, name=emjn)
            if emoji != None:
                if emoji.name in message.content:
                    msg = message.content.replace(":","").replace(f"{emoji.name}" , f"{emoji}")
                gnitro = nitrodbc.find_one({"guild" : message.guild.id})
                if gnitro == None:
                    return
                if gnitro != None and gnitro["nitro"] == "enabled":
                    allowed_mentions = discord.AllowedMentions(everyone = False, roles=False, users=True)
                    await message.delete()
                    await webhook.send(avatar_url=message.author.display_avatar, content=msg, username=message.author.name, allowed_mentions= allowed_mentions)
