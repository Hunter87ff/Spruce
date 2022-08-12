import os
import discord
from discord.ext import commands
from asyncio import sleep
import pymongo
from pymongo import MongoClient
import re
from modules import config
import datetime




maindb = config.maindb #MongoClient(os.environ["mongo_url"])
dbc = maindb["tourneydb"]["tourneydbc"]
tourneydbc=dbc

gtamountdbc = maindb["gtamountdb"]["gtamountdbc"]
gtadbc = gtamountdbc







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





#Fake Tag Check
async def ft_ch(message):
    ctx = message
    td = tourneydbc.find_one({"tid" : message.channel.id%1000000000000})
    messages = [message async for message in ctx.channel.history(limit=123)]  #messages = await message.channel.history(limit=td["tslot"]).flatten()


    for fmsg in messages:
        if fmsg.author.id != ctx.author.id:
            for mnt in fmsg.mentions:

                if mnt not in message.mentions:
                    pass

                if mnt in message.mentions:
                    #tk = len(set(ctx.mentions) & set(fmsg.mentions))
                    #mon = len(ctx.mentions) - tk
                    return True







async def tourney(message):
    ctx = message
    guild = message.guild
    td = tourneydbc.find_one({"tid" : message.channel.id%1000000000000})

    if message.author.bot:
        return

    if td is None:
        return
    
    if td["status"] == "paused":
        await message.author.send("Registration Paused")

    if td is not None and message.channel.id  == int(td["rch"]) and td["status"] == "started":
        messages = [message async for message in ctx.channel.history(limit=2000)]     #messages = await message.channel.history(limit=td["tslot"]).flatten()
        crole = discord.utils.get(guild.roles, id=int(td["crole"]))
        cch = discord.utils.get(guild.channels, id = int(td["cch"]))
        rch = discord.utils.get(guild.channels, id = int(td["rch"]))
        ments = td["mentions"]
        rgs = td["reged"]
        tslot = td["tslot"]

            
        if crole in message.author.roles:
            await message.delete()
            return await message.channel.send("Already Registered", delete_after=5)
            

        if rgs > tslot:
            overwrite = rch.overwrites_for(message.guild.default_role)
            overwrite.update(send_messages=False)
            await rch.set_permissions(guild.default_role, overwrite=overwrite)
            await message.delete()
            return await rch.send("**Registration Closed**")
            
        
        elif len(message.mentions) == ments or len(message.mentions) > ments:
            
            for fmsg in messages:
                tk = len(set(ctx.mentions) & set(fmsg.mentions))
                if td["faketag"] == "no":

 
                    if fmsg.author.id == ctx.author.id and len(messages) == 1:
                        print("Same Author")
                        if len(messages) == 1:
                            await message.author.add_roles(crole)
                            await message.add_reaction("✅")
                            reg_update(message)
                            team_name = find_team(message)
                            femb = discord.Embed(color=0xffff00, description=f"**{rgs}) TEAM NAME: [{team_name.upper()}](https://discordapp.com/channels/{message.channel.guild.id}/{message.channel.id}/{message.id})**\n**Players** : {(', '.join(m.mention for m in message.mentions)) if message.mentions else message.author.mention} ")
                            femb.set_author(name=message.guild.name, icon_url=message.guild.icon)
                            femb.timestamp = datetime.datetime.utcnow()
                            return await cch.send(message.author.mention, embed=femb)


                    if fmsg.author.id != ctx.author.id:
                        ftch = await ft_ch(message)
                        if ftch == True:
                            fakeemb = discord.Embed(title=f"The Member You Tagged is Already Registered In A Team. If You Think He Used `Fake Tags`, You can Contact `Management Team`", color=0xffff00)
                            fakeemb.add_field(name="Team", value=f"[Registration Link](https://discordapp.com/channels/{guild.id}/{message.channel.id}/{fmsg.id})")
                            fakeemb.set_author(name=ctx.author, icon_url=ctx.author.avatar)
                            await message.delete()
                            return await ctx.channel.send(embed=fakeemb, delete_after=60)

                            
                                

                        if ftch != True:
                            await message.author.add_roles(crole)
                            await message.add_reaction("✅")
                            reg_update(message)
                            team_name = find_team(message)
                            femb = discord.Embed(color=0xffff00, description=f"**{rgs}) TEAM NAME: [{team_name.upper()}](https://discordapp.com/channels/{message.channel.guild.id}/{message.channel.id}/{message.id})**\n**Players** : {(', '.join(m.mention for m in message.mentions)) if message.mentions else message.author.mention} ")
                            femb.set_author(name=message.guild.name, icon_url=message.guild.icon)
                            femb.timestamp = datetime.datetime.utcnow()
                            return await cch.send(message.author.mention, embed=femb)
                        

                            

                if td["faketag"] == "yes":
                    print("Fake Tag Yes")

                    await message.author.add_roles(crole)
                    await message.add_reaction("✅")
                    reg_update(message)
                    team_name = find_team(message)
                    nfemb = discord.Embed(color=0xffff00, description=f"**{rgs}) TEAM NAME: [{team_name.upper()}](https://discordapp.com/channels/{message.channel.guild.id}/{message.channel.id}/{message.id})**\n**Players** : {(', '.join(m.mention for m in message.mentions)) if message.mentions else message.author.mention} ")
                    nfemb.set_author(name=message.guild.name, icon_url=message.guild.icon)
                    nfemb.timestamp = datetime.datetime.utcnow()
                    return await cch.send(message.author.mention, embed=nfemb)


        elif len(message.mentions) < ments:
            #await bot.process_commands(message)
            meb = discord.Embed(description=f"Minimum {ments} Mentions Required For Successfull Registration", color=0xff0000)
            await message.delete()
            return await message.channel.send(content=message.author.mention, embed=meb, delete_after=5)


