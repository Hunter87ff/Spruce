import os
import discord
import re
import random
import requests as req
import asyncio
import datetime
import openai
from asyncio import sleep
from modules import config
from discord.ext import commands



maindb = config.maindb #MongoClient(os.environ["mongo_url"])
dbc = maindb["tourneydb"]["tourneydbc"]
tourneydbc=dbc

gtamountdbc = maindb["gtamountdb"]["gtamountdbc"]
gtadbc = gtamountdbc

sdb = config.spdb
sdbc = sdb["qna"]["query"]

openai.api_key = config.openai_key



bws = ['xvideos', ' bsdke', 'भोसडीके', 'randi', "https://", 'लुंड', "लन्ड", "Lund","lunD", 'behnchod', 'chut', 'fuck', 'गांडू', 'fuddi', 'chutia', 'chumt', 'madrchod', 'bhos', 'carding', 'kutta', 'lauda', 'asshole', 'छोड़', 'xhamster', 'sex', 'penis', 'bitch', 'betichod', 'nude', 'Pornhub', 'gand', 'faggot', 'Porn', 'lundura', 'xnxx', 'maderchod', '18+ content', 'vagina', 'Mother Fucker', 'bhnchod', 'asses', 'chutiya', 'lodi', 'behenchod', 'bhn ki lodi', 'gamd', 'खनकी', 'मदरचोड', 'fucker', 'छोड़ू', 'lund', 'adult content', 'hentai', 'motherchod', 'ramdi', 'छूट', 'RedTube', 'p0rn', 'pussy', 'chod', 'sexy', 'bhenchod', 'condom', 'YouPorn.', 'चुटिया', 'comdon', 'khanki', 'nigg', 'porn', 'boob', 'titt', 'btichod', 'pepe', 'pornhub', 'lowda','redwap', 'मादरचोद', 'idiot', 'gamdu', ' bsdk', 'bc', 'बेटीछोद', 'wtf', 'lawde', 'fuk', 'Fucker']



#########################################################
################ CHAT SYSTEM ###########################
#########################################################

cod = [
  {"q":"function","a":"js"},
  {"q":"def","a":"py"},
  {"q":"print","a":"py"},
  {"q":"console","a":"js"},
  {"q":"python","a":"py"},
  {"q":"py","a":"py"},
  {"q":"js","a":"js"},
  {"q":"<script>","a":"js"},
]
dmm = ["send me", "dm me", "mujhe bhejo", "pm me", "amake send koro", " mujhe dm karo"]
tim = ["what is the date","abhi tarikh kya hai?", "aj kosa tarikh hai", "abhi kitna baja hai", "what is the time", "abhi kitna baja hai"]



async def ask(message, bot):
    ctx = await bot.get_context(message)
    if message.author.bot:
        return
    #dmc = bot.get_channel(config.dml)
    opt = ""
    try:
		
        if message.guild and  bot.user.mention in message.content or message.guild==None:
            await ctx.typing()
            req.post(url=config.dml, json={'content':f"sent by : {message.author}\nmessage: ```\n{message.content[0:1980]}\n```"})
            for i in bws:
                if i in message.content:
                    ms = await message.channel.send("Sorry can't reply to a message which contains restricted words")
                    await asyncio.sleep(5)
                    return await ms.delete()
                    
            query = message.content.replace(f"<@{bot.user.id}>", "")
            #print(query)
            for i in cod:
                if i["q"] in query:
                    query = query + f"quote the code with ```{i['a']}"
            response = openai.Completion.create(model="text-davinci-003",prompt=query,temperature=0.7,max_tokens=998,top_p=1,frequency_penalty=0,presence_penalty=0)
            #print(response["choices"][0]["text"])
            liss = []
            rsp = sdbc.find_one({"q" : query})
            if rsp is not None:
                if int(rsp["rating"]) >= 5:
                    opt = rsp["a"]
                if int(rsp["rating"]) <5:
                    liss.append(rsp['a'])
                    liss.append(response["choices"][0]["text"])
                    opt = random.choice(liss)
            if rsp is None:
                opt = str(response["choices"][0]["text"])
        
            for i in bws:
                if i in opt.split(" "):
                    ms = await message.channel.send("Sorry can't reply to a message which contains restricted words")
                    await asyncio.sleep(5)
                    return await ms.delete()
        
    
            for i in dmm:
                if i in query:
                    try:
                        await message.author.send(opt)
                        return await message.reply("check dm")
                    except:
                        return await message.reply("please check your dm configuration.")
            for i in tim:
                if i in query:
                    #print(message.created_at)
                    date = str(message.created_at).split(' ')[0]  
                    return await message.reply(f'Current Date : {"-".join(date.split("-")[::-1])}')
    
            await message.reply(opt)
    except Exception as e:
        return print(f"error ask feature: {e}")
    

#########################################################
################ GROUP SYSTEM ###########################
#########################################################



def get_slot(ms):
    for i in range(1, 13):
        if f"{i})" not in ms.content:
            return f"{i})"


async def prc(group,  grpc , msg, tsl):
    messages = [message async for message in grpc.history(limit=tsl)]

    for ms in messages:
        if len(messages) <3:
            if ms.author.id != config.bot_id:
                if f"**__GROUP__ {str(group)} **" not in ms.content:
                    await grpc.send(f"**__GROUP__ {group} ** \n{get_slot(ms)} {msg}")


        if ms.author.id == config.bot_id:
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


async def auto_grp(message):
    try:
        td = dbc.find_one({"cch":message.channel.id})
    except:
        return

    if td:
        if td["auto_grp"] == "yes":
            if message.author.id == config.bot_id:
                if not message.embeds:
                    return
                if message.embeds:
                    if "TEAM NAME" not in message.embeds[0].description:
                        return
                reged = td["reged"]-1
                grpch = discord.utils.get(message.guild.channels, id=int(td["gch"]))
                group = get_group(reged=reged)
                return await prc(group=group, grpc=grpch, msg=message.content, tsl=td["tslot"])




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
                    return True



async def tourney(message):
    if not message.guild:
        return
    ctx = message
    guild = message.guild
    td = tourneydbc.find_one({"tid" : message.channel.id%1000000000000})
    tmrole = discord.utils.get(ctx.guild.roles, name="tourney-mod")
    if message.author.bot:
        return
      
    if tmrole in ctx.author.roles:
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

        if not crole:
            try:
                await message.author.send("Registration Paused")
            except:
                pass
            await ctx.reply("Confirm Role Not Found")
            return dbc.update_one({"tid" : td["rch"]}, {"$set" : {"status" : "paused"}})


            
        if crole in message.author.roles:
            await message.delete()
            return await message.channel.send("**Already Registered**", delete_after=5)
            

        if rgs > tslot:
            overwrite = rch.overwrites_for(message.guild.default_role)
            overwrite.update(send_messages=False)
            await rch.set_permissions(guild.default_role, overwrite=overwrite)
            await message.delete()
            return await rch.send("**Registration Closed**")
        
        elif len(message.mentions) == ments or len(message.mentions) > ments:
            
            for fmsg in messages:
                tk = len(set(ctx.mentions) & set(fmsg.mentions))


#IF FAKE TAG NOT ALLOWED
########################

                if td["faketag"] == "no":

 
                    if fmsg.author.id == ctx.author.id and len(messages) == 1:

                        if len(messages) == 1:
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
                                dbc.update_one({"rch" : rch.id}, {"$set" : {"pub" : "yes", "prize" : await get_prize(cch)}})
                                


                    if fmsg.author.id != ctx.author.id:
                        ftch = await ft_ch(message)
                        if ftch == True:
                            fakeemb = discord.Embed(title=f"The Member You Tagged is Already Registered In A Team. If You Think He Used `Fake Tags`, You can Contact `Management Team`", color=0xffff00)
                            fakeemb.add_field(name="Team", value=f"[Registration Link]({fmsg.jump_url})")
                            fakeemb.set_author(name=ctx.author, icon_url=ctx.author.avatar)
                            await message.delete()
                            return await ctx.channel.send(embed=fakeemb, delete_after=60)
                                

                        if ftch != True:
                            await message.author.add_roles(crole)
                            await message.add_reaction("✅")
                            reg_update(message)
                            team_name = find_team(message)
                            femb = discord.Embed(color=0xffff00, description=f"**{rgs}) TEAM NAME: [{team_name.upper()}]({message.jump_url})**\n**Players** : {(', '.join(m.mention for m in message.mentions)) if message.mentions else message.author.mention} ")
                            femb.set_author(name=message.guild.name, icon_url=message.guild.icon)
                            femb.timestamp = datetime.datetime.utcnow()
                            femb.set_thumbnail(url=message.author.display_avatar)
                            if rgs >= tslot*0.1 and td["pub"] == "no":
                                dbc.update_one({"rch" : rch.id}, {"$set" : {"pub" : "yes", "prize" : await get_prize(cch)}})
                            return await cch.send(f"{team_name.upper()} {message.author.mention}", embed=femb)
                            
                        
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
                        dbc.update_one({"rch" : rch.id}, {"$set" : {"pub" : "yes", "prize" : await get_prize(cch)}})
                    return await cch.send(f"{team_name.upper()} {message.author.mention}", embed=nfemb)
                    


        elif len(message.mentions) < ments:
            #await bot.process_commands(message)
            meb = discord.Embed(description=f"**Minimum {ments} Mentions Required For Successfull Registration**", color=0xff0000)
            await message.delete()
            return await message.channel.send(content=message.author.mention, embed=meb, delete_after=5)

        


############## ERROR HANDEL ################


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
        brp = await ctx.reply(f"Processing...")
        await brp.edit(content=f"Something Went Wrong. Don't worry! I've Reported To Developers. You'll Get Reply Soon.\nThanks For Playing With Me ❤️", delete_after=30)

