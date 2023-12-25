"""
MIT License

Copyright (c) 2022 hunter87ff

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os, discord, re, random, asyncio
import requests as req
import datetime
from asyncio import sleep
from modules import config
from discord.ext import commands
import numpy as np
maindb = config.maindb #MongoClient(os.environ["mongo_url"])
dbc = maindb["tourneydb"]["tourneydbc"]
tourneydbc=dbc
gtamountdbc = maindb["gtamountdb"]["gtamountdbc"]
gtadbc = gtamountdbc
sdb = config.spdb
sdbc = sdb["qna"]["query"]
bws = config.bws

#########################################################
################ CHAT SYSTEM ###########################
#########################################################

say = ["bolo ki", "say", "bolo", "bolie", "kaho"]
name = ["my name", "mera nam kya hai", "what is my name", "do you know my name"]
unfair = [{"q":"me harami", "a":"aap harami ho"}, {"q":"me useless", "a":"me really useful yes i know"}, {"q":"mein harami", "a":"aap harami nehi ho!! kya baat kar rhe ho"}, {"q":"i am a dog", "a":"im a bot!! Spruce Bot 😎"}]
repl_yes = ["ohh", "okey", "hm"]
def lang_model(ctx, query:str, response):
    for i in say:
        if i in query:
            ms = query.replace(i, "")
            for j in unfair:
                if j["q"] in ms:
                    ms = ms.replace(j["q"], j["a"])
            return ms

    if "yes" in query:
        return random.choice(repl_yes)

    for i in name:
        if i in query:
            return ctx.author.name


def check_send(message, bot):
    if message.guild == None:
        return True
    else:
        return None

"""    if message.reference != None:
        if message.reference.cached_message.author.id == bot.user.id:
            return True"""
    

async def ask(message, bot):
    ctx = await bot.get_context(message)
    if message.author.bot:
        return
    if message.author.id != config.owner_id:
        pass
    response = sdbc.find()
    if check_send(message, bot) != None:
        for i in bws:
            if i.lower() in message.content.split().lower():
                return await ctx.reply("message contains blocked word. so i can't reply to this message! sorry buddy.")
        query = message.content.replace(f"<@{bot.user.id}>", "").lower()
        if lang_model(ctx, query, response) != None:
            await ctx.typing()
            await asyncio.sleep(4)
            mallow = discord.AllowedMentions(everyone=False, roles=False)
            return await ctx.reply(lang_model(ctx, query, response), allowed_mentions=mallow)
        matches = []
        if not lang_model(ctx, query, response):
            for a in response:
                a2 = np.array([x.lower() for x in a["q"].split()])
                a1 = np.array([x.lower() for x in query.split()])
                same = len(np.intersect1d(a1, a2))
                if int(same/len(a1)*100) >= 95:
                    await ctx.typing()
                    await asyncio.sleep(4)
                    return await ctx.reply(a["a"])
                if same >= len(query.split())/2:
                    if int(same/len(a1)*100) >= 1:
                        matches.append({"a" : a["a"], "r": int(same/len(a1)*100)})
            if len(matches) > 0:
                mt = max(matches, key=lambda x: x['r'])
                await ctx.typing()
                await asyncio.sleep(4)
                return await ctx.reply(mt["a"])
        if len(matches)==0:
            req.pt(url=config.dml, json={"content":f"{message.author}```\n{query}\n```"})
            return 
        

#########################################################
################ GROUP SYSTEM ###########################
#########################################################



def get_slot(ms):
    for i in range(1, 13):
        if f"{i})" not in ms.content:
            return f"{i})"


async def prc(group,  grpc, bot, msg, tsl):
    messages = [message async for message in grpc.history(limit=tsl)]

    for ms in messages:
        if len(messages) <3:
            if ms.author.id != bot.user.id:
                if f"**__GROUP__ {str(group)} **" not in ms.content:
                    await grpc.send(f"**__GROUP__ {group} ** \n{get_slot(ms)} {msg}")
        if ms.author.id == bot.user.id:
            if f"**__GROUP__ {str(group)} **" in ms.content:
                if "12)" not in ms.content.split():
                    cont = f"{ms.content}\n{get_slot(ms)} {msg}"
                    return await ms.edit(content=cont)
                if "12)" in ms.content.split():
                    pass
            if f"**__GROUP__ {str(group)} **" not in ms.content:
                ms = await grpc.send(f"**__GROUP__ {group} ** \n")
                cont = f"{ms.content}\n{get_slot(ms=ms)} {msg}"
                return await ms.edit(content=cont)
    if len(messages) < 1:
        ms = await grpc.send(f"**__GROUP__ {group} ** \n")
        cont = f"{ms.content}\n{get_slot(ms)} {msg}"
        return await ms.edit(content=cont)

def get_group(reged):
    grp = reged/12
    if grp > int(grp):
        grp = grp + 1
    return str(int(grp))

async def auto_grp(message, bot):
    try:
        td = dbc.find_one({"cch":message.channel.id})
    except:
        return
    if td:
        if td["auto_grp"] == "yes":
            if message.author.id == bot.user.id:
                if not message.embeds:
                    return
                if message.embeds:
                    if "TEAM NAME" not in message.embeds[0].description:
                        return
                reged = td["reged"]-1
                grpch = discord.utils.get(message.guild.channels, id=int(td["gch"]))
                group = get_group(reged=reged)
                return await prc(group=group, grpc=grpch, bot=bot, msg=message.content, tsl=td["tslot"])

##########################################################################
########################### SLOT CONFIRM SYSTEM ##########################
##########################################################################
def gp(info):
    match = ["INR", "inr" , "₹", "Inr", "$"]
    for i in match:
        if i in info:
            nd =  info.split(i)[0]
            ad =  nd.split()[-1]
            print(ad)
            return f"{ad} {i}"
        else:
            return "Not Data"

async def get_prize(cch):
    info = cch.category.channels[0]
    finder = ["Prize", "prize", "PRIZE", "POOL", "Pool", "PrizE"]
    messages = [message async for message in info.history(limit=123)]
    if len(messages) == 0:
        return "No Data"
    for i in messages:
        for p in finder:
            if p in str(i.content).split():
                return gp(info=i.content)
            else:
                return "No Data"

def find_team(message):
    content = message.content.lower()
    teamname = re.search(r"team.*", content)
    if teamname is None:
        return f"{message.author}'s team"
    teamname = re.sub(r"<@*#*!*&*\d+>|team|name|[^\w\s]", "", teamname.group()).strip()
    teamname = f"{teamname.title()}" if teamname else f"{message.author}'s team"
    return teamname

def reg_update(message):
    df = dbc.find_one({"rch" : message.channel.id})
    rgd = df["reged"] 
    dbc.update_one({"rch" : message.channel.id}, {"$set":{"reged": rgd + 1}})


#Fake Tag Check
async def ft_ch(message):
    ctx = message
    #td = tourneydbc.find_one({"tid" : message.channel.id%1000000000000})
    messages = [message async for message in ctx.channel.history(limit=123)]  
    for fmsg in messages:
        if fmsg.author.id != ctx.author.id:
            for mnt in fmsg.mentions:
                if mnt in message.mentions:
                    return mnt
    return None



async def tourney(message):
    if message.author.bot:
        return
    if not message.guild:
        return
    ctx = message
    guild = message.guild
    tmrole = discord.utils.get(ctx.guild.roles, name="tourney-mod")
    if tmrole in ctx.author.roles:
      return
    td = dbc.find_one({"rch" : message.channel.id})
    if td is None:
        return
    if td["status"] == "paused":
        await message.author.send("Registration Paused")
    if td is not None and message.channel.id  == int(td["rch"]) and td["status"] == "started":
        messages = [message async for message in ctx.channel.history(limit=2000)]
        crole = discord.utils.get(guild.roles, id=int(td["crole"]))
        cch = discord.utils.get(guild.channels, id = int(td["cch"]))
        rch = discord.utils.get(guild.channels, id = int(td["rch"]))
        ments = td["mentions"]
        rgs = td["reged"]
        tslot = td["tslot"]
        if not crole:
            try:
                await message.author.send("Registration Paused")
            except:
                pass
            await ctx.reply("Confirm Role Not Found")
            return dbc.update_one({"tid" : td["rch"]}, {"$set" : {"status" : "paused"}})
        if crole in message.author.roles:
            try:
                await message.delete()
            except:
                pass
            return await message.channel.send("**Already Registered**", delete_after=5)
        if rgs > tslot:
            overwrite = rch.overwrites_for(message.guild.default_role)
            overwrite.update(send_messages=False)
            await rch.set_permissions(guild.default_role, overwrite=overwrite)
            await message.delete()
            return await rch.send("**Registration Closed**")
        elif len(message.mentions) >= ments:
            for fmsg in messages:
                
                #IF FAKE TAG NOT ALLOWED
                ########################
                if td["faketag"] == "no":
                    if fmsg.author.id == ctx.author.id and len(messages) == 1:
                        await message.add_reaction("✅")
                        reg_update(message)
                        team_name = find_team(message)
                        femb = discord.Embed(color=0xffff00, description=f"**{rgs}) TEAM NAME: [{team_name.upper()}]({message.jump_url})**\n**Players** : {(', '.join(m.mention for m in message.mentions)) if message.mentions else message.author.mention} ")
                        femb.set_author(name=message.guild.name, icon_url=message.guild.icon)
                        femb.timestamp = datetime.datetime.utcnow()
                        femb.set_thumbnail(url=message.author.display_avatar)
                        await cch.send(f"{team_name.upper()} {message.author.mention}", embed=femb)
                        await message.author.add_roles(crole)
                        if rgs >= tslot*0.1 and td["pub"] == "no":
                            dbc.update_one({"rch" : td["rch"]}, {"$set" : {"pub" : "yes", "prize" : await get_prize(cch)}})
                    if fmsg.author.id != ctx.author.id:
                        ftch = await ft_ch(message)
                        if ftch != None:
                            fakeemb = discord.Embed(title=f"The Member  {ftch}, You Tagged is Already Registered In A Team. If You Think He Used `Fake Tags`, You can Contact `Management Team`", color=0xffff00)
                            fakeemb.add_field(name="Team", value=f"[Registration Link]({fmsg.jump_url})")
                            fakeemb.set_author(name=ctx.author, icon_url=ctx.author.avatar)
                            await message.delete()
                            return await ctx.channel.send(embed=fakeemb, delete_after=60)
                        if ftch == None:
                            try:
                                await message.author.add_roles(crole)
                                await message.add_reaction("✅")
                                reg_update(message)
                                team_name = find_team(message)
                                femb = discord.Embed(color=0xffff00, description=f"**{rgs}) TEAM NAME: [{team_name.upper()}]({message.jump_url})**\n**Players** : {(', '.join(m.mention for m in message.mentions)) if message.mentions else message.author.mention} ")
                                femb.set_author(name=message.guild.name, icon_url=message.guild.icon)
                                femb.timestamp = message.created_at   #datetime.datetime.utcnow()
                                femb.set_thumbnail(url=message.author.display_avatar)
                                if rgs >= tslot*0.1 and td["pub"] == "no":
                                    dbc.update_one({"rch" : td["rch"]}, {"$set" : {"pub" : "yes", "prize" : await get_prize(cch)}})
                                return await cch.send(f"{team_name.upper()} {message.author.mention}", embed=femb)
                            except Exception as e:
                                print(e)
                                
                            
                #IF FAKE TAG ALLOWED
                ####################
                if td["faketag"] == "yes":
                    await message.author.add_roles(crole)
                    await message.add_reaction("✅")
                    reg_update(message)
                    team_name = find_team(message)
                    nfemb = discord.Embed(color=0xffff00, description=f"**{rgs}) TEAM NAME: [{team_name.upper()}]({message.jump_url})**\n**Players** : {(', '.join(m.mention for m in message.mentions)) if message.mentions else message.author.mention} ")
                    nfemb.set_author(name=message.guild.name, icon_url=message.guild.icon)
                    nfemb.timestamp = datetime.datetime.utcnow()
                    nfemb.set_thumbnail(url=message.author.display_avatar)
                    if rgs >= tslot*0.1 and td["pub"] == "no":
                        dbc.update_one({"rch" : td["rch"]}, {"$set" : {"pub" : "yes", "prize" : await get_prize(cch)}})
                    return await cch.send(f"{team_name.upper()} {message.author.mention}", embed=nfemb)
        elif len(message.mentions) < ments:
            #await bot.process_commands(message)
            meb = discord.Embed(description=f"**Minimum {ments} Mentions Required For Successfull Registration**", color=0xff0000)
            try:
                await message.delete()
            except Exception as e:
                print(f"line No 335, error: {e}")
            return await message.channel.send(content=message.author.mention, embed=meb, delete_after=5)



############## ERROR HANDEL ################
############################################
async def error_handle(ctx, error, bot):
    erl = bot.get_channel(config.erl)
    cmdnf = bot.get_channel(config.cmdnf)
    try:
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(embed=discord.Embed(color=0xff0000, description="Missing Required Arguments! You Should Check How To Use This Command.\nTip: use `&help <this_command>` to get Instructions"))
        elif isinstance(error, commands.MissingPermissions):
            return await ctx.send(embed=discord.Embed(color=0xff0000, description="You don't have Permissions To Use This Command"))
        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(embed=discord.Embed(color=0xff0000, description="This Command Is Currently Disabled! You Can Try Again Later"))
        elif isinstance(error, commands.CommandNotFound):
            await cmdnf.send(f"```py\nGuild Name: {ctx.guild}\nGuild Id : {ctx.guild.id}\nUser Tag : {ctx.author}\nUser Id : {ctx.author.id}\nCommand : {ctx.message.content}```")
            return await ctx.send(embed=discord.Embed(color=0xff0000, description="Command Not Found! Please Check Spelling Carefully."))
        elif isinstance(error, (commands.MissingRole, commands.MissingAnyRole)):
            return await ctx.send(embed=discord.Embed(color=0xff0000, description=str(error)))
        elif isinstance(error, commands.UserInputError):
            return await ctx.send(embed=discord.Embed(color=0xff0000, description="Please Enter Valid Arguments"))
        elif isinstance(error, commands.EmojiNotFound):
            return await ctx.send(embed=discord.Embed(color=0xff0000, description="Emoji Not Found"))
        elif isinstance(error, commands.NotOwner):
            return await ctx.send(embed=discord.Embed(color=0xff0000, description="This Is A Owner Only Command You Can't Use It"))
        elif isinstance(error, commands.MessageNotFound):
            return await ctx.send(embed=discord.Embed(color=0xff0000, description="Message Not Found Or Deleted"))
        elif isinstance(error, commands.MemberNotFound):
            return await ctx.send(embed=discord.Embed(color=0xff0000, description="Member Not Found"))
        elif isinstance(error, commands.ChannelNotFound):
            return await ctx.send(embed=discord.Embed(color=0xff0000, description="Channel Not Found"))
        elif isinstance(error, commands.GuildNotFound):
            return await ctx.send("**I'm Not In The Server! which You Want To See**", delete_after=19)
        elif isinstance(error, commands.ChannelNotReadable):
            return await ctx.send(embed=discord.Embed(color=0xff0000, description="Can Not Read Messages Of The Channel"))
        elif isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(embed=discord.Embed(color=0xff0000, description=str(error)))
        elif "Manage Messages" in str(error):
            return await ctx.send(embed=discord.Embed(description="Missing `Manage Messages` Permission", color=0xff0000))
        elif "Unknown file format." in str(error):
            return await ctx.send(embed=discord.Embed(description="Invalid Input", color=0xff0000))
        elif "Send Messages" in str(error):
            return await ctx.author.send(embed=discord.Embed(description=f"I don't have Permissions To Send message in this channel - {ctx.channel.mention}", color=0xff0000))
        elif "This playlist type is unviewable." in str(error):
            return await ctx.send(embed=discord.Embed(description="This playlist type is unsupported!", color=0xff0000))
        elif "Maximum number of channels in category reached (50)" in str(error):
            return await ctx.send(embed=discord.Embed(description="Maximum number of channels in category reached (50)", color=0xff0000), delete_after=30)
        elif isinstance(error, commands.BotMissingPermissions):
            return await ctx.send(embed=discord.Embed(color=0xff0000, description=str(error)))
        elif "error code: 10003" in str(error):
            return await ctx.send(embed=discord.Embed(description="Channel Deleted Or Invalid", color=0xff0000))
        elif "error code: 50013" in str(error):
            return await ctx.send(embed=discord.Embed(description="**Missing Permissions! You Should Check My Permissions**", color=0xff0000), delete_after=30)
        elif "Unknown Role" in str(error):
            return await ctx.send(embed=discord.Embed(description="**Given Role Is Invalid Or Deleted**", color=0xff0000), delete_after=30)
        elif "Cannot delete a channel required for community servers" in str(error):
            return await ctx.send(embed=discord.Embed(description="**I Cannot delete a channel required for community servers**", color=0xff0000), delete_after=30)
        elif "error code: 50001" in str(error):
            return await ctx.send(embed=discord.Embed(description="**I don't have access to do this**", color=0xff0000), delete_after=30)
        elif "error code: 30005" in str(error):
            return await ctx.send(embed=discord.Embed(description="Maximum number of guild roles reached (250)", color=0xff0000))
        elif "error code: 30007" in str(error):
            return await ctx.send(embed=discord.Embed(description="Maximum number of webhooks reached (15)", color=0xff0000))
        elif "error code: 30008" in str(error):
            return await ctx.send(embed=discord.Embed(description="Maximum number of emojis reached", color=0xff0000))
        elif "error code: 30010" in str(error):
            return await ctx.send(embed=discord.Embed(description="Maximum number of reactions reached (20)", color=0xff0000))
        elif "error code: 30013" in str(error):
            return await ctx.send(embed=discord.Embed(description="Maximum number of guild channels reached (500)", color=0xff0000))

    except:
        e = str(error)
        await erl.send(f"<@885193210455011369>\n```py\nGuild Name: {ctx.guild}\nGuild Id : {ctx.guild.id}\nUser Tag : {ctx.author}\nUser Id : {ctx.author.id}\nCommand : {ctx.message.content}\n\n\n{e}```")
        await ctx.reply("Something Went Wrong. Don't worry! I've Reported To Developers. You'll Get Reply Soon.\nThanks For Playing With Me ❤️", delete_after=30)
