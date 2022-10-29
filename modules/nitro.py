
import os 
import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
from modules import config




maindb = config.maindb
nitrodbc = maindb["nitrodb"]["nitrodbc"]








async def nitrof(message):
    if message.author.bot:
        return
    try:
        gnitro = nitrodbc.find_one({"guild" : message.guild.id})
    except:
        return

    if gnitro != None and gnitro["nitro"] == "enabled":
        try:
            webhook = discord.utils.get(await message.channel.webhooks(), name="Spruce")

        except:
            message.reply("Missing Permissions - `manage_messages` , `manage_webhooks`")

        if webhook == None:
            try:
                webhook = await message.channel.create_webhook(name="Spruce")

            except:
                await message.reply("Missing Permissions - `manage_messages` , `manage_webhooks`")
       
                
        words = message.content.split()
        for word in words:
            if word[0] == ":" and word[-1] == ":":
                emjn = word.replace(":", "")
                emoji = discord.utils.get(bot.emojis, name=emjn)
                if emoji != None:
                    if emoji.name in message.content:
                        msg = message.content.replace(":","").replace(f"{emoji.name}" , f"{emoji}")
                        allowed_mentions = discord.AllowedMentions(everyone = False, roles=False, users=True)
                        nick = message.author.nick
                        if message.author.nick == None:
                            nick = message.author.name
                        await webhook.send(avatar_url=message.author.display_avatar, content=msg, username=nick, allowed_mentions= allowed_mentions)
                        await message.delete()
                        

