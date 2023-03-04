import os 
import json
import time
import random
import typing
import pymongo
import discord
import asyncio
import datetime
import requests
import wavelink
import gtts
from gtts import gTTS
from asyncio import sleep
from pymongo import MongoClient
from wavelink.ext import spotify
from discord.ext import commands
from discord.ui import Button, View
from datetime import datetime, timedelta
from modules import (message_handel, channel_handel, checker, config, color)
from discord.ext.commands.converter import (MemberConverter, RoleConverter, TextChannelConverter)




 
onm = message_handel
ochd = channel_handel
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True
intents.voice_states = True
intents.guilds = True
pref = os.environ["prefix"]


#Configuring db
dburl = os.environ["mongo_url"]
maindb = MongoClient(dburl)
startTime = time.time()





bot = commands.Bot(command_prefix= commands.when_mentioned_or("&"), intents=intents ) 
#allowed_mentions = discord.AllowedMentions(roles=True, users=True, everyone=True),
bot.remove_command("help")

async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
asyncio.run(load_extensions())




@bot.event
async def on_ready():
    await node_connect()
    st_log = bot.get_channel(1020027121231462400)
    status = ['&help', f"{len(bot.guilds) } Servers", "You", "Sprucebot.ml/invite", "189k+ Members"]
    stmsg = f'{bot.user} is ready with {len(bot.commands)} commands'
    await st_log.send(embed=discord.Embed(title="Status", description=stmsg, color=0x00ff00))
    print(stmsg)
    while True:
        for st in status:
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=st))
            await sleep(180)




@bot.event
async def on_wavelink_node_ready(node: wavelink.Node):
    print(f"Node {node.identifier} is ready")

async def node_connect():
    await bot.wait_until_ready()
    await wavelink.NodePool.create_node(bot = bot, host=config.m_host, port=443, password=config.m_host_psw, https=True, spotify_client=spotify.SpotifyClient(client_id=config.spot_id, client_secret=config.spot_secret))



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
            await message.reply("Nitro Module Enabled But Missing Permissions - `manage_messages` , `manage_webhooks`")

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
                        msg1 = message.content.replace(":","").replace(f"{emoji.name}" , f"{emoji}")
                        allowed_mentions = discord.AllowedMentions(everyone = False, roles=False, users=True)
                        nick = message.author.nick
                        if message.author.nick == None:
                            nick = message.author.name
                        await message.delete()
                        return await webhook.send(avatar_url=message.author.display_avatar, content=msg1, username=nick, allowed_mentions= allowed_mentions)
    else:
        return
                        



    

@bot.event
async def on_message(message):
    if message.webhook_id != None:
        return
    await bot.process_commands(message)
    #await nitrof(message)
    await onm.tourney(message)
    await onm.auto_grp(message)
    
    
   
	
@bot.event
async def on_guild_channel_delete(channel):
    await ochd.ch_handel(channel)
	

@bot.event
async def on_guild_join(guild):
    ch = bot.get_channel(1028673206850179152)
    link = await random.choice(guild.channels).create_invite(reason=None, max_age=0, max_uses=0, temporary=False, unique=True, target_type=None, target_user=None, target_application_id=None)
    msg= f"```py\nGuild Name : {guild.name}\nGuild Id : {guild.id}\nGuild Owner : {guild.owner}\nOwner_id : {guild.owner.id}\nMembers : {guild.member_count}```\nInvite Link : {link}"
    return await ch.send(msg)


@bot.event
async def on_guild_remove(guild):
    ch = bot.get_channel(1028673254606508072)
    #link = await guild.channels[0].create_invite(reason=None, max_age=0, max_uses=0, temporary=False, unique=True, target_type=None, target_user=None, target_application_id=None)
    msg= f"```py\nGuild Name : {guild.name}\nGuild Id : {guild.id}\nGuild Owner : {guild.owner}\nOwner_id : {guild.owner.id}\n Members : {guild.member_count}```"
    return await ch.send(msg)

	
##########################################################################################
#                                          TEXT COMMANDS
############################################################################################
"""
class Nhelp(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            emby = discord.Embed(description=page, color = discord.Color.blurple())
            emby.add_field(name="Links", value="[Support Server](https://discord.gg/vMnhpAyFZm) | [Invite Link](https://discord.com/api/oauth2/authorize?client_id=931202912888164474&permissions=8&redirect_uri=https%3A%2F%2Fdiscord.gg%2FvMnhpAyFZm&response_type=code&scope=bot%20identify)")
#           emby.add_field(name='Support Server', value='[join](https://discord.gg/FXbRZHz3cG)', inline = False)
            await destination.send(embed=emby)
bot.help_command = Nhelp(no_category = 'Commands')

"""


@bot.event
async def on_command_error(ctx, error):
    erl = bot.get_channel(1015166083050766366)
    cmdnf = bot.get_channel(1020698810625826846)

    if isinstance(error, commands.MissingRequiredArgument):
        err = discord.Embed(color=0xff0000, description="Missing Required Arguments")
        return await ctx.send(embed=err)

    elif isinstance(error, commands.MissingPermissions):
        err = discord.Embed(color=0xff0000, description="You don't have Permissions To Use This Command")
        return await ctx.send(embed=err)

    elif isinstance(error, commands.DisabledCommand):
        err = discord.Embed(color=0xff0000, description="This Command Is Currently Disabled! You Can Try Again Later")
        return await ctx.send(embed=err)

    elif isinstance(error, commands.CommandNotFound):
        err = discord.Embed(color=0xff0000, description="Command Not Found! Please Check Spelling Carefully.")
        await cmdnf.send(f"```py\nGuild Name: {ctx.guild}\nGuild Id : {ctx.guild.id}\nUser Tag : {ctx.author}\nUser Id : {ctx.author.id}\nCommand : {ctx.message.content}```")
        return await ctx.send(embed=err)


    elif isinstance(error, (commands.MissingRole, commands.MissingAnyRole)):
        er = str(error)
        if "'" in er:
            er = er.replace("'", "`")
        err = discord.Embed(color=0xff0000, description=er)
        return await ctx.send(embed=err)

    elif isinstance(error, commands.UserInputError):
        err = discord.Embed(color=0xff0000, description="Please Enter Valid Arguments")
        return await ctx.send(embed=err)

    elif isinstance(error, commands.EmojiNotFound):
        err = discord.Embed(color=0xff0000, description="Emoji Not Found")
        return await ctx.send(embed=err)

    elif isinstance(error, commands.NotOwner):
        err = discord.Embed(color=0xff0000, description="This Is A Owner Only Command You Can't Use It")
        return await ctx.send(embed=err)

    elif isinstance(error, commands.MessageNotFound):
        err = discord.Embed(color=0xff0000, description="Message Not Found Or Deleted")
        return await ctx.send(embed=err)

    elif isinstance(error, commands.MemberNotFound):
        err = discord.Embed(color=0xff0000, description="Member Not Found")
        return await ctx.send(embed=err)

    elif isinstance(error, commands.ChannelNotFound):
        err = discord.Embed(color=0xff0000, description="Channel Not Found")
        return await ctx.send(embed=err)
    elif isinstance(error, commands.GuildNotFound):
        return await ctx.send("**I'm Not In The Server! which You Want To See**", delete_after=19)

    elif isinstance(error, commands.ChannelNotReadable):
        err = discord.Embed(color=0xff0000, description="Can Not Read Messages Of The Channel")
        return await ctx.send(embed=err)

    elif isinstance(error, commands.CommandOnCooldown):
        e = str(error)
        err = discord.Embed(color=0xff0000, description=e)
        return await ctx.send(embed=err)

    elif "Manage Messages" in str(error):
        return await ctx.send(embed=discord.Embed(description="Missing `Manage Messages` Permission", color=0xff0000))

    elif "Unknown file format." in str(error):
        return await ctx.send(embed=discord.Embed(description="Invalid Input", color=0xff0000))

    elif "Send Messages" in str(error):
        try:
            return await ctx.author.send(embed=discord.Embed(description=f"I don't have Permissions To Send message in this channel - {ctx.channel.mention}", color=0xff0000))
        except:
            return

    elif "This playlist type is unviewable." in str(error):
        return await ctx.send(embed=discord.Embed(description="This playlist type is unsupported!", color=0xff0000))

    elif "Maximum number of channels in category reached (50)" in str(error):
        return await ctx.send(embed=discord.Embed(description="Maximum number of channels in category reached (50)", color=0xff0000), delete_after=30)

    elif isinstance(error, commands.BotMissingPermissions):
        er = str(error)
        if "(s)" in er:
            er = er.replace("(s)", " ")
        err = discord.Embed(color=0xff0000, description=er)
        return await ctx.send(embed=err)


    elif "NotFound: 404 Not Found (error code: 10003): Unknown Channel" in str(error):
        try:
            return await ctx.send(embed=discord.Embed(description="Channel Deleted Or Invalid", color=0xff0000))
        except:
            return

    elif "403 Forbidden (error code: 50013): Missing Permissions" in str(error):
        return await ctx.send(embed=discord.Embed(description="**Missing Permissions! You Should Check My Permissions**", color=0xff0000), delete_after=30)

    elif "Unknown Role" in str(error):
        return await ctx.send(embed=discord.Embed(description="**Given Role Is Invalid Or Deleted**", color=0xff0000), delete_after=30)

    elif "Cannot delete a channel required for community servers" in str(error):
        return await ctx.send(embed=discord.Embed(description="**Cannot delete a channel required for community servers**", color=0xff0000), delete_after=30)

    elif "403 Forbidden (error code: 50001): Missing Access" in str(error):
        return await ctx.send(embed=discord.Embed(description="**Missing Access! You Should Check My Permissions**", color=0xff0000), delete_after=30)

    else:
        e = str(error)
        await erl.send(f"<@885193210455011369>\n```py\nGuild Name: {ctx.guild}\nGuild Id : {ctx.guild.id}\nUser Tag : {ctx.author}\nUser Id : {ctx.author.id}\nCommand : {ctx.message.content}\n\n\n{e}```")
        brp = await ctx.reply(f"Suddenly You Got a Bug!")
        await brp.edit(content=f"Error Ditected. Don't worry! I've Reported To Developers. You'll Get Reply Soon.\nThanks For Playing With Me ❤️", delete_after=30)


#

@bot.command()
@commands.dm_only()
async def cdm(ctx,amount:int):
  dmchannel = await ctx.author.create_dm()
  async for message in dmchannel.history(limit=amount):
    if message.author == bot.user:
      await message.delete()



block = ["ass", "asses", "asshole", "bc", "behenchod", "betichod", "bhenchod", "bhos", "bitch", "boob", "bsdk", "bsdke", "carding", "chumt", "chut", "chutia", "chutiya", "comdon", "condom", "faggot", "fuck", "fucker", "gamd", "gamdu", "gand", "hentai", "idiot", "khanki", "kutta", "lauda", "lawde", "lund", "maderchod", "motherchod", "nigg"," p0rn", "penis", "pepe", "porn", "pornhub", "pussy", "ramdi", "randi", "sex", "sexy", "titt", "vagina", "xhamster", "xnxx", "xvideos", "खनकी", "गांडू", "चुटिया", "छूट", "छोड़", "छोड़ू", "बेटीछोद", "भोसडीके", "मदरचोड", "मादरचोद", "लुंड"]
good = ["good", "awesome", "smart", "la la la", "achha", "bohot achha"]
@bot.command()
async def tts(ctx, *, message):
    if len(message.split()) > 100:
        return await ctx.send("Maximum 100 words allowed")
    for i in block:
        if i in message.split():
            message = message.replace(i,random.choice(good))
    output = gTTS(text=message, lang="en", tld="co.in")
    output.save(f"tts.mp3")
    #fl = open("tts.mp3", r).read()
    await ctx.send(ctx.author.mention, file=discord.File("tts.mp3"))
    os.remove("tts.mp3")





async def il(id):
    try:
        channel = bot.get_channel(id)
    except:
        return "Not Available"
    try:
        link = await channel.create_invite(reason=None, max_age=360000, max_uses=0, temporary=False, unique=False, target_type=None, target_user=None, target_application_id=None)
    except:
        return "Not Available"

    return link



#dbc.update_many({"status" : "started"},{"$set":{"pub" : "no", "prize" : "Nothing"}})

@bot.command()
async def tourneys(ctx):
    dbc = maindb["tourneydb"]["tourneydbc"]
    dta = dbc.find()
    emb = discord.Embed(title="Tournaments", color=0x00ff00)
    msg = await ctx.send("Sending You! Via DM")
    for i in dta:
        rch = bot.get_channel(i["rch"])
        if i["reged"] >= i["tslot"]/10:
            if i["reged"]/i["tslot"]*100 < 90:
                if i["pub"] == "yes":
                    invite = await il(id=i["rch"])
                    emb.add_field(name=rch.category.name.upper(), value=f'Prize : {i["prize"]}\n[Register]({invite})\n----------------')

    try:
        await ctx.author.send(embed=emb)
        await msg.edit(content="Please Check Your DM")
    except:
        await msg.edit(content="I Think You've Disabled Your DM")




@bot.command()
@commands.bot_has_permissions(create_instant_invite=True)
@commands.has_permissions(manage_messages=True, manage_channels=True, manage_roles=True)
@commands.has_role("tourney-mod")
async def publish(ctx, rch: discord.TextChannel, *, prize: str):
    dbc = maindb["tourneydb"]["tourneydbc"]
    if len(prize) > 30:
        return await ctx.reply("Only 30 Letters Allowed ")
    try:
        dbcd = dbc.find_one({"rch" : rch.id})
    except:
        return await ctx.send("Tournament Not Found")

    dbc.update_one({"rch" : rch.id}, {"$set" : {"pub" : "yes", "prize" : prize}})
    await ctx.send(f"{rch.category.name} is now public")



############################################################################################
#                                       INFO
############################################################################################
  

@bot.command(hidden=True)
@commands.bot_has_permissions(manage_messages=True, send_messages=True)
async def rping(ctx):
    if ctx.author.id == 885193210455011369:
        await ctx.reply(f'**Current ping is `{round(bot.latency*1000)} ms`**')


async def mmbrs(ctx):
    i = 0
    for guild in bot.guilds:
        i = i + guild.member_count
    return i


def gp():
    plst = [23, 19, 21, 22, 21, 20, 21, 23, 19, 18, 24,28]
    ping = random.choice(plst)
    return ping



@bot.command()
@commands.cooldown(2, 20, commands.BucketType.user)
@commands.bot_has_permissions(manage_messages=True, send_messages=True)
async def ping(ctx):
    await ctx.reply(f'**Current ping is `{gp()} ms`**')


async def mmbrs(ctx):
    i = 0
    for guild in bot.guilds:
        i = i + guild.member_count
    return i


@bot.command(aliases=["bi"])
@commands.bot_has_permissions(send_messages=True, embed_links=True)
async def botinfo(ctx): 
  emb = discord.Embed(title="Spruce Bot", description="Welcome To Spruce", color=discord.Color.blurple())
  mmbs = await mmbrs(ctx)
  emb.add_field(name="<:servers:1018845797556703262> __Servers Info__", value=f"Total server : {len(bot.guilds)}\nTotal Members : {mmbs}", inline=False)
  emb.add_field(name="<:dev:1020696239689433139> __Developer__", value="[Hunter#6967](https://discord.com/users/885193210455011369)", inline=False)
  emb.add_field(name="<:g_latency:968371843335610408> __Current Ping__", value=gp(), inline=False)
  emb.add_field(name="<:setting:968374105961300008> __Command Prefix__", value="prefix: & , command: &help", inline=False)
  emb.set_footer(text=f"Made with ❤️ | By hunter#6967")
  return await ctx.send(embed=emb)






@bot.command()
@commands.guild_only()
@commands.bot_has_permissions(manage_emojis=True)
@commands.has_permissions(manage_emojis=True)
async def addemoji(ctx, emoji: discord.PartialEmoji):
    emoji_bytes = await emoji.read()
    new = await ctx.guild.create_custom_emoji(name=emoji.name, image=emoji_bytes, reason=f'Emoji Added By {ctx.author}')
    return await ctx.send(f"{new} added", delete_after=10)




@bot.command(hidden=True)
async def sdm(ctx, member: discord.User, *, message):
    if ctx.author.id == 885193210455011369:
        try:
            await member.send(message)
            return ctx.reply("Done")
        except:
            return

    if ctx.author.id != 885193210455011369:
        return await ctx.send(embed=discord.Embed(description="Command not found! please check the spelling carefully", color=0xff0000))




@bot.command(hidden=True)
async def leaveg(ctx, member:int):
    if ctx.author.bot:
        return

    if ctx.author.id != config.owner_id:
        return

    for guild in bot.guilds:
        if guild.member_count < member:
            gname = guild.name
            await guild.leave()
            await ctx.send(f"Leaved From {gname}")



bot.run(os.environ['TOKEN'])
