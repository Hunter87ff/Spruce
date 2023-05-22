import os 
import time
import random
import discord
import asyncio
#import requests
import wavelink
from asyncio import sleep
from wavelink.ext import spotify
from discord.ext import commands
#from discord.ui import Button, View
from modules import (message_handel, channel_handel, config)
#from discord.ext.commands.converter import (MemberConverter, RoleConverter, TextChannelConverter)



 
onm = message_handel
ochd = channel_handel
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True
intents.voice_states = True
intents.guilds = True



#Configuring db
pref = config.prefix
maindb = config.maindb






bot = commands.Bot(command_prefix= commands.when_mentioned_or(pref), intents=intents ) 
#bot = commands.Bot(command_prefix= pref, intents=intents ) 
#allowed_mentions = discord.AllowedMentions(roles=True, users=True, everyone=True),
bot.remove_command("help")


async def load_extensions():
    for filename in os.listdir(config.cogs_path):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
asyncio.run(load_extensions())




@bot.event
async def on_ready():
    #await node_connect()
    st_log = bot.get_channel(config.stl)
    await bot.tree.sync()
    status = ['&help', "You", "dsc.gg/spruce", "250k+ Members", "Tournaments", "Feedbacks", "Text2Speech", "Music"]
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


@bot.event
async def on_message(message):
    if message.webhook_id:
        return
    await bot.process_commands(message)
    #await nitrof(message)
    await onm.tourney(message)
    await onm.auto_grp(message)
    #await onm.ask(message, bot)
	


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
    support_server = bot.get_guild(config.support_server_id)
    orole = discord.utils.get(support_server.roles, id=1043134410029019176)
    #link = await guild.channels[0].create_invite(reason=None, max_age=0, max_uses=0, temporary=False, unique=True, target_type=None, target_user=None, target_application_id=None)
    msg= f"```py\nGuild Name : {guild.name}\nGuild Id : {guild.id}\nGuild Owner : {guild.owner}\nOwner_id : {guild.owner.id}\n Members : {guild.member_count}```"
    for i in support_server.members:
        if i.id == guild.owner.id:
            if orole in i.roles:
                await i.remove_roles(orole, reason="Kicked Spruce")

    return await ch.send(msg)


@bot.event
async def error_handle(ctx, error, bot):
    erl = bot.get_channel(config.erl)
    cmdnf = bot.get_channel(config.cmdnf)
    try:
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(embed=discord.Embed(color=0xff0000, description=error))
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
        await brp.edit(content="Something Went Wrong. Don't worry! I've Reported To Developers. You'll Get Reply Soon.\nThanks For Playing With Me ❤️", delete_after=30)


#async def on_command_error(ctx, error):
#    await onm.error_handle(ctx, error, bot)

##########################################################################################
#                                          TEXT COMMANDS
############################################################################################



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


@bot.hybrid_command(with_app_command = True, hidden=True)
@commands.is_owner()
async def edm(ctx, channel:discord.TextChannel, msg_id, *, msg):
  if ctx.author.bot:
    return
  await ctx.defer(ephemeral=True)
  if ctx.author.id != config.owner_id:
    return await ctx.send('This is a owner only command.')
  try:
    ms = await channel.fetch_message(int(msg_id))
    print(type(ms))
    if ms.author.id == bot.user.id:
      await ms.edit(content=msg)
      await ctx.send('done')
  except:
    return await ctx.send('Something went wrong...')
  

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




############################################################################################
#                                       INFO
############################################################################################

@bot.hybrid_command(with_app_command=True)
@commands.is_owner()
async def get_guild(ctx, id):
    if ctx.author.bot:
        return
    id = int(id)
    if ctx.author.id != config.owner_id:
        return await ctx.send(embed=discord.Embed(description="This Is A Owner Only Command", color=0xff0000))
    guild = bot.get_guild(id)
    if  guild:
        inv = await random.choice(guild.channels).create_invite(reason=None, max_age=0, max_uses=0, temporary=False, unique=True, target_type=None, target_user=None, target_application_id=None)
        return await ctx.reply(inv)
    if not guild:
        return await ctx.reply("Im Not In This Guild")



def mmbrs(ctx=None):
    i = 0
    for guild in bot.guilds:
        i = i + guild.member_count
    return i

def gp():
    plst = [23, 19, 21, 22, 21, 32, 43, 20, 21, 23, 19, 18, 24,28]
    ping = random.choice(plst)
    return ping

@bot.command()
@commands.cooldown(2, 20, commands.BucketType.user)
@commands.bot_has_permissions(send_messages=True)
@commands.cooldown(2, 60, commands.BucketType.user)
async def ping(ctx):
    if ctx.author.id == config.owner_id:
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
    emb.add_field(name=f"{config.servers}__Servers Info__", value=f"Total server : {len(bot.guilds)}\nTotal Members : {mmbs}", inline=False)
    emb.add_field(name=f"{config.dev} __Developer__", value="[Hunter#6967](https://discord.com/users/885193210455011369)", inline=False)
    emb.add_field(name=f"{config.ping} __Current Ping__", value=gp(), inline=False)
    emb.add_field(name=f"{config.setting} __Command Prefix__", value=f"command: {pref}help, prefix: {pref}  ", inline=False)
    emb.set_footer(text=f"Made with ❤️ | By hunter#6967")
    return await ctx.send(embed=emb)



@bot.command()
@commands.guild_only()
@commands.cooldown(2, 20, commands.BucketType.user)
async def owners(ctx):
    if ctx.guild.id != config.support_server_id:
        return
    ms = await ctx.send(f"{config.loading} Processing...")
    ofcg = bot.get_guild(config.support_server_id)
    owner_role = ofcg.get_role(1043134410029019176)
    for i in bot.guilds:
        if i.owner in ofcg.members:
            if i.member_count > 100:
                onr = ofcg.get_member(i.owner.id)
                await onr.add_roles(owner_role)
    return ms.edit(content="Done")



@bot.hybrid_command(with_app_command=True)
@commands.guild_only()
async def dlm(ctx, channel:discord.TextChannel, msg_id):
    await ctx.defer(ephemeral=True)
    if ctx.author.bot:
        return
    if ctx.author.id != config.owner_id:
        return
    try:
        ms = await channel.fetch_message(msg_id)
        if ms.author.id == bot.user.id:
            await ms.delete()
        else:
            return await ctx.send("I didn't sent the mesage")
    except:
        return await ctx.send("Not Possible")


@bot.command(hidden=True)
@commands.guild_only()
@commands.cooldown(2, 20, commands.BucketType.user)
async def sdm(ctx, member: discord.User, *, message):
    if ctx.author.id == config.owner_id:
        try:
            await member.send(message)
            return await ctx.reply("Done")
        except:
            return

    if ctx.author.id != config.owner_id:
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


bot.run(config.token)
