
import discord
from discord.ext import commands
from asyncio import sleep
import pymongo
from pymongo import MongoClient
import re
from modules import  config
import datetime




maindb = config.maindb  
dbc = maindb["tourneydb"]["tourneydbc"]
tourneydbc=dbc

gtamountdbc = maindb["gtamountdb"]["gtamountdbc"]
gtadbc = gtamountdbc







bot = commands.Bot(command_prefix=",")


def find_team(message):
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
    ctx = message
    guild = message.guild
    td = tourneydbc.find_one({"tid" : message.channel.id%1000000000000})

    if message.author.bot:
        return
    

    if td is None:
        return
    
    elif td["status"] == "paused":
        await message.author.send("Registration Paused")

    if td is not None and message.channel.id  == int(td["rch"]) and td["status"] == "started":
        messages = await message.channel.history(limit=td["tslot"]).flatten()
        crole = discord.utils.get(guild.roles, id=int(td["crole"]))
        cch = discord.utils.get(guild.channels, id = int(td["cch"]))
        rch = discord.utils.get(guild.channels, id = int(td["rch"]))
        ments = td["mentions"]
        rgs = td["reged"]
        tslot = td["tslot"]

            
        if crole in message.author.roles:
            return await message.channel.send("Already Registered", delete_after=5)
            

        if rgs > tslot:
            overwrite = rch.overwrites_for(message.guild.default_role)
            overwrite.update(send_messages=False)
            await rch.set_permissions(guild.default_role, overwrite=overwrite)
            #await bot.process_commands(message)
            return await rch.send("**Registration Closed**")
            
        
        elif len(message.mentions) == ments or len(message.mentions) > ments:
            for fmsg in messages:
                if td["faketag"] == "no":
                    #print("Fake Tag No")

                    if fmsg.author != ctx.author:
                        print("Test 1 Passed")
                        for mentio in fmsg.mentions:
                            if mentio in message.mentions:
                                print("Test 2 Passed")
                                fakeemb = discord.Embed(title=f"The Member You Tagged is Already Registered In A Team. If You Think He Used `Fake Tags`, You can Contact `Management Team`", color=0xffff00)
                                fakeemb.add_field(name="Team", value=f"[Registration Link](https://discordapp.com/channels/{guild.id}/{message.channel.id}/{fmsg.id})")
                                fakeemb.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
                                await message.delete()
                                return await ctx.channel.send(embed=fakeemb, delete_after=60)

                            if mentio not in message.mentions:
                                #print("Mention Unique")
                                await message.author.add_roles(crole)
                                print("Role given")
                                await message.add_reaction("✅")
                                #print("Reaction de dia")
                                reg_update(message)
                                #print("db Updated")
                                team_name = find_team(message)
                                femb = discord.Embed(color=0xffff00, description=f"**{rgs}) TEAM NAME: [{team_name.upper()}](https://discordapp.com/channels/{message.channel.guild.id}/{message.channel.id}/{message.id})**\n**Players** : {(', '.join(m.mention for m in message.mentions)) if message.mentions else message.author.mention} ")
                                femb.set_author(name=message.guild.name, icon_url=message.guild.icon_url)
                                femb.timestamp = datetime.datetime.utcnow()
                                return await cch.send(message.author.mention, embed=femb)

                if td["faketag"] == "yes":
                    #print("Fake Tag Yes")
                    await message.author.add_roles(crole)
                    await message.add_reaction("✅")
                    reg_update(message)
                    team_name = find_team(message)
                    nfemb = discord.Embed(color=0xffff00, description=f"**{rgs}) TEAM NAME: [{team_name.upper()}](https://discordapp.com/channels/{message.channel.guild.id}/{message.channel.id}/{message.id})**\n**Players** : {(', '.join(m.mention for m in message.mentions)) if message.mentions else message.author.mention} ")
                    nfemb.set_author(name=message.guild.name, icon_url=message.guild.icon_url)
                    nfemb.timestamp = datetime.datetime.utcnow()
                    return await cch.send(message.author.mention, embed=nfemb)


        elif len(message.mentions) < ments:
            #await bot.process_commands(message)
            return await message.reply(f"Minimum {ments} Required For Successfull Registration")

