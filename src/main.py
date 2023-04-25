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
    #await node_connect()
    st_log = bot.get_channel(config.stl)
    await bot.tree.sync()
    status = ['&help', "You", "Sprucebot.ml/invite", "241k+ Members", "Tournaments", "Feedbacks", "Text2Speech"]
    stmsg = f'{bot.user} is ready with {len(bot.commands)} commands'
    await st_log.send("<@885193210455011369>", embed=discord.Embed(title="Status", description=stmsg, color=0x00ff00))
    print(stmsg)
    while True:
        for st in status:
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=st))
            await sleep(120)




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
    ch = bot.get_channel(config.gjoin)
    link = await random.choice(guild.channels).create_invite(reason=None, max_age=0, max_uses=0, temporary=False, unique=False, target_type=None, target_user=None, target_application_id=None)
    msg= f"```py\nGuild Name : {guild.name}\nGuild Id : {guild.id}\nGuild Owner : {guild.owner}\nOwner_id : {guild.owner.id}\nMembers : {guild.member_count}```\nInvite Link : {link}"
    return await ch.send(msg)


@bot.event
async def on_guild_remove(guild):
    ch = bot.get_channel(config.gleave)
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


@bot.hybrid_command(with_app_command = True, hidden=True)
@commands.is_owner()
@commands.dm_only()
@commands.cooldown(2, 20, commands.BucketType.user)
async def cdm(ctx,amount:int):
    await ctx.defer(ephemeral=True)
    dmchannel = await ctx.author.create_dm()
    async for message in dmchannel.history(limit=amount):
        if message.author == bot.user:
            await message.delete()




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

@bot.hybrid_command(with_app_command = True)
@commands.cooldown(2, 20, commands.BucketType.user)
async def tourneys(ctx):
    await ctx.defer(ephemeral=True)
    dbc = maindb["tourneydb"]["tourneydbc"]
    dta = dbc.find()
    emb = discord.Embed(title="Tournaments", color=0x00ff00)
    for i in dta:
        rch = bot.get_channel(i["rch"])
        if i["pub"] == "yes":
            invite = await il(id=i["rch"])
            emb.add_field(name=rch.category.name.upper(), value=f'Server : {rch.guild.name}\nPrize : {i["prize"]}\n[Register]({invite})\n----------------')

    try:
        msg = await ctx.send("Sending You! Via DM")
        await ctx.author.send(embed=emb)
        await msg.edit(content="Please Check Your DM")
    except:
        await msg.edit(content="I Think You've Disabled Your DM")




@bot.hybrid_command(with_app_command = True, aliases=["pub"])
@commands.bot_has_permissions(create_instant_invite=True)
@commands.has_permissions(manage_messages=True, manage_channels=True, manage_roles=True)
@commands.has_role("tourney-mod")
@commands.cooldown(2, 20, commands.BucketType.user)
@commands.guild_only()
async def publish(ctx, rch: discord.TextChannel, *, prize: str):
    await ctx.defer(ephemeral=True)
    dbc = maindb["tourneydb"]["tourneydbc"]
    if len(prize) > 30:
        return await ctx.reply("Only 30 Letters Allowed ")
    try:
        dbcd = dbc.find_one({"rch" : rch.id})
        if dbcd["reged"] < dbcd["tslot"]*0.1:
            return await ctx.send("You've To Fill 10% Slot. To Publish This Tournament")
    except:
        return await ctx.send("Tournament Not Found")


    dbc.update_one({"rch" : rch.id}, {"$set" : {"pub" : "yes", "prize" : prize}})
    await ctx.send(f"**{rch.category.name} is now public**")



############################################################################################
#                                       INFO
############################################################################################
  
@bot.command()
async def get_guild(ctx, id:int):
    if ctx.author.id != 885193210455011369:
        return await ctx.send(embed=discord.Embed(description="Command not found! please check the spelling carefully", color=0xff0000))
    guild = bot.get_guild(id)
    if not guild:
        return await ctx.reply("Im Not In This Guild")
    inv = await random.choice(guild.channels).create_invite(reason=None, max_age=0, max_uses=0, temporary=False, unique=True, target_type=None, target_user=None, target_application_id=None)
    await ctx.reply(inv)



def mmbrs(ctx=None):
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
@commands.bot_has_permissions(send_messages=True)
@commands.cooldown(2, 60, commands.BucketType.user)
async def ping(ctx):
    if ctx.author.id == 885193210455011369:
        await ctx.reply(f'**Current ping is `{round(bot.latency*1000)} ms`**')
    else:
        await ctx.reply(f'**Current ping is `{gp()} ms`**')


@bot.hybrid_command(with_app_command = True, aliases=["bi", "about", "info"])
@commands.cooldown(2, 20, commands.BucketType.user)
@commands.bot_has_permissions(send_messages=True, embed_links=True)
async def botinfo(ctx):
    await ctx.defer(ephemeral=True)
    emb = discord.Embed(title="Spruce Bot", description="Welcome To Spruce", color=discord.Color.blurple())
    mmbs = mmbrs()
    emb.add_field(name="<:servers:1018845797556703262> __Servers Info__", value=f"Total server : {len(bot.guilds)}\nTotal Members : {mmbs}", inline=False)
    emb.add_field(name="<:dev:1020696239689433139> __Developer__", value="[Hunter#6967](https://discord.com/users/885193210455011369)", inline=False)
    emb.add_field(name="<:g_latency:968371843335610408> __Current Ping__", value=gp(), inline=False)
    emb.add_field(name="<:setting:968374105961300008> __Command Prefix__", value="prefix: & , command: &help", inline=False)
    emb.set_footer(text=f"Made with ❤️ | By hunter#6967")
    return await ctx.send(embed=emb)



@bot.command()
@commands.guild_only()
@commands.cooldown(2, 20, commands.BucketType.user)
async def owners(ctx):
    if ctx.guild.id != 947443790053015623:
        return
    ms = await ctx.send("Processing...")
    ofcg = bot.get_guild(947443790053015623)
    owner_role = ofcg.get_role(1043134410029019176)
    for i in bot.guilds:
        if i.owner in ofcg.members:
            if i.member_count > 100:
                onr = ofcg.get_member(i.owner.id)
                await onr.add_roles(owner_role)
    return ms.delete()





@bot.command(hidden=True)
@commands.guild_only()
@commands.cooldown(2, 20, commands.BucketType.user)
async def sdm(ctx, member: discord.User, *, message):
    if ctx.author.id == 885193210455011369:
        try:
            await member.send(message)
            return await ctx.reply("Done")
        except:
            return

    if ctx.author.id != 885193210455011369:
        return await ctx.send(embed=discord.Embed(description="Command not found! please check the spelling carefully", color=0xff0000))




@bot.command(hidden=True)
@commands.guild_only()
@commands.cooldown(2, 20, commands.BucketType.user)
async def leaveg(ctx, member:int, guild_id:int=None):
    if ctx.author.bot:
        return

    if ctx.author.id != config.owner_id:
        return

    if not guild_id:
        for guild in bot.guilds:
            if guild.member_count < member:
                gname = guild.name
                await guild.leave()
                await ctx.send(f"Leaved From {gname}, Members: {guild.member_count}")
    if guild_id:
        try:
            gld = bot.get_guild(guild_id)
        except:
            return
        if gld:
            await gld.leave()
            await ctx.send(f"Leaved From {gld.name}, Members: {gld.member_count}")


bot.run(os.environ['TOKEN'])
