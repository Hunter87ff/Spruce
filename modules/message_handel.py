import discord
from discord.ext import commands
#from asyncio import sleep
import os
import pymongo
from pymongo import MongoClient
import re



maindb = MongoClient(os.environ["mongo_url"])    
db = maindb["tourneydb"]
dbc = db["tourneydbc"]
tourneydbc=dbc


bot = commands.Bot(command_prefix=",")


async def gali_dia(message):
    if "fuck" in message.content:
        await message.channel.purge(limit=1)
        return await message.channel.send("gali mat de , warna yeli photo khich ke mala chadha dunga!")


def find_team(message):
    """Finds team name from a message"""
    content = message.content.lower()
    teamname = re.search(r"team.*", content)
    if teamname is None:
        return f"{message.author}'s team"

    teamname = re.sub(r"<@*#*!*&*\d+>|team|name|[^\w\s]", "", teamname.group()).strip()
    teamname = f"Team {teamname.title()}" if teamname else f"{message.author}'s team"
    return teamname


async def tourney(message):
    await gali_dia(message)
    #await bot.process_commands(message)


    if message.author.bot:
        return

    guild = message.guild
    td = tourneydbc.find_one({"tid" : message.channel.id%1000000000000}) #onluy fixed value needed
    if td is None:
        return


    
    if message.channel.id  == int(td["rch"]):

        crole = discord.utils.get(guild.roles, id=int(td["crole"]))
        cch = discord.utils.get(guild.channels, id = int(td["cch"]))
        rch = discord.utils.get(guild.channels, id = int(td["rch"]))
        ments = td["mentions"]
        rgs = td["reged"]
        tslot = td["tslot"]


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
            team_name = find_team(message)
            emb = discord.Embed(color=0x1abc9c, description=f"**{rgs}) TEAM NAME: [{team_name.upper()}](https://discordapp.com/channels/{message.channel.guild.id}/{message.channel.id}/{message.id})**\n**Players** : {(', '.join(m.mention for m in message.mentions)) if message.mentions else message.author.mention} ")
            return await cch.send(message.author.mention, embed=emb)

        elif len(message.mentions) < ments:
            #await bot.process_commands(message)
            return await message.reply(f"Minimum {ments} Required For Successfull Registration")


    if message.channel.id  != int(td["rch"]):
        #await bot.process_commands(message)
        print("fucked")

    await bot.process_commands(message)
