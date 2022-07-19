
import discord
from discord.ext import commands
from asyncio import sleep
import pymongo
from pymongo import MongoClient
import re
import os
from modules import config
import datetime




maindb = config.maindb  
db = maindb["tourneydb"]
dbc = db["tourneydbc"]
tourneydbc=dbc
gtamountdbc = maindb["gtamountdb"]["gtamountdbc"]
gtadbc = gtamountdbc







bot = commands.Bot(command_prefix=",")


def find_team(message):
    """Finds team name from a message"""
    content = message.content.lower()
    teamname = re.search(r"team.*", content)
    if teamname is None:
        return f"{message.author}'s team"

    teamname = re.sub(r"<@*#*!*&*\d+>|team|name|[^\w\s]", "", teamname.group()).strip()
    teamname = f"Team {teamname.title()}" if teamname else f"{message.author}'s team"
    return teamname


def reg_update(message):
    df = dbc.find_one({"tid" : message.channel.id%1000000000000})
    rgd = df["reged"] 
    dbc.update_one({"tid" : message.channel.id%1000000000000}, {"$set":{"reged": rgd + 1}})



async def tourney(message):
    if message.author.bot:
        return
    guild = message.guild
    ctx = message
    td = tourneydbc.find_one({"tid" : message.channel.id%1000000000000})
    messages = await message.channel.history(limit=td["tslot"]).flatten()
    
    if td is None:
        return
    
    elif td["status"] == "paused":
        await message.author.send("Registration Paused")

    if message.channel.id  == int(td["rch"]) and td["status"] == "started":

        crole = discord.utils.get(guild.roles, id=int(td["crole"]))
        cch = discord.utils.get(guild.channels, id = int(td["cch"]))
        rch = discord.utils.get(guild.channels, id = int(td["rch"]))
        ments = td["mentions"]
        rgs = td["reged"]
        tslot = td["tslot"]
        
        
        for fmsg in messages:
            if td["faketag"] == "no":
                if message.mentions == fmsg.mentions:
                    await message.channel.purge(limit=1)
                    return await ctx.channel.send("Dont use tags of registered players")


        if crole in message.author.roles:
            return await message.reply("Already Registered")
            

        if rgs > tslot:
            overwrite = rch.overwrites_for(message.guild.default_role)
            overwrite.update(send_messages=False)
            await rch.set_permissions(guild.default_role, overwrite=overwrite)
            #await bot.process_commands(message)
            return await rch.send("**Registration Closed**")
            
        
        elif len(message.mentions) == ments or len(message.mentions) > ments:
            await message.author.add_roles(crole)
            await message.add_reaction("✅")
            reg_update(message)
            team_name = find_team(message)
            emb = discord.Embed(color=0xffff00, description=f"**{rgs}) TEAM NAME: [{team_name.upper()}](https://discordapp.com/channels/{message.channel.guild.id}/{message.channel.id}/{message.id})**\n**Players** : {(', '.join(m.mention for m in message.mentions)) if message.mentions else message.author.mention} ")
            emb.set_author(name=message.guild.name, icon_url=message.guild.icon_url)
            emb.timestamp = datetime.datetime.utcnow()
            return await cch.send(message.author.mention, embed=emb)

        elif len(message.mentions) < ments:
            #await bot.process_commands(message)
            await ctx.channel.purge(limit=1)
            lmemb = discord.Embed(description=f"{message.author.mention}\nMinimum {ments} Mentions Required For Successfull Registration", color=0xffff00)
            return await message.channel.send(embed=lmemb, delete_after=5)


    if message.channel.id  != int(td["rch"]):
        #await bot.process_commands(message)
        print("Not Tournament")

    await bot.process_commands(message)
