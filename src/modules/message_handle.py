"""
This project is licensed under the GNU GPL v3.0.
Copyright (C) 2022 hunter87.dev@gmail.com
Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.
"""

import re, traceback, functools
from datetime import timedelta
from typing import TYPE_CHECKING
from ext.error import update_error_log
from ext.modals import Tourney
from discord import utils, AllowedMentions, Embed, Message, TextChannel
from ext import Database, helper, color as Color


if TYPE_CHECKING:
    from modules.bot import Spruce
    
db = Database()
dbc = db.dbc

async def get_prize(cch:TextChannel):
    info = cch.category.channels[0]
    messages = [message async for message in info.history(limit=10, oldest_first=True)]

    if len(messages) == 0:
        return "No Data Given"
    
    return helper.parse_prize_pool(messages[0]) or "No Data Given"


def find_team(message:Message):
    content = message.content.lower()
    teamname = re.search(r"team.*", content)
    if teamname is None:return f"{message.author}'s team"
    teamname = re.sub(r"<@*#*!*&*\d+>|team|name|[^\w\s]", "", teamname.group()).strip()
    teamname = f"{teamname.title()}" if teamname else f"{message.author}'s team"
    return teamname


def reg_update(message:Message):
    df = dbc.find_one({"rch" : message.channel.id})
    rgd = df["reged"] 
    dbc.update_one({"rch" : message.channel.id}, {"$set":{"reged": rgd + 1}})


#duplicate Tag Check
async def duplicate_tag(crole, message:Message):
    ctx = message
    messages = [message async for message in ctx.channel.history(limit=100)]  
    for fmsg in messages:

        if fmsg.author.bot:
            return None
        
        if fmsg.author.id != ctx.author.id and crole in fmsg.author.roles:
            for mnt in fmsg.mentions:
                if mnt in message.mentions:return mnt
    return None


@functools.lru_cache(maxsize=400)
def find_by_reg(message:Message) -> dict | None:
    return dbc.find_one({"rch" : message.channel.id})


async def log_event(message:Message, desc:str, color:int=None):
    try:
        if color is None:
            color = Color.random()

        log_channel = utils.get(message.guild.text_channels, name=f"{message.guild.me.name.lower()}-tourney-log")

        if not log_channel:
            return 
        
        _embed = Embed(description=desc, color=color)
        _embed.timestamp = message.created_at

        return await log_channel.send(embed=_embed)
    
    except Exception:
        return print(traceback.format_exc())


#Tourney System
async def tourney(message:Message, bot:'Spruce'):
    if message.author.bot or not message.guild:
        return
    
    if not any([
        message.guild.me.guild_permissions.manage_messages,
        message.guild.me.guild_permissions.manage_roles,
        message.guild.me.guild_permissions.send_messages,
        message.guild.me.guild_permissions.embed_links,
        message.channel.permissions_for(message.guild.me).read_message_history,
        message.guild.me.guild_permissions.manage_channels
    ]):
        return
    
    bot.debug(f"Processing tourney registration in {message.guild.name} for {message.author}.")

    tournament = Tourney.findOne(message.channel.id)

    bot.debug(f"Checking tournament status for {message.guild.name} in channel {message.channel.name}.")

    if not tournament:
        return

    bot.debug("✅ Check 1 passed - Tournament found.")

    if utils.get(message.author.roles, name="tourney-mod"):
        return

    elif tournament.status == "paused":
        try:
            await message.author.send("Registration Paused")
            return
        
        except Exception:
            return print(traceback.format_exc())
        
    bot.debug("✅ Check 2 passed - Tournament is not paused.")
    if message.channel.id  != tournament.rch or tournament.status != "started": return

    crole = message.guild.get_role(tournament.crole)
    cch = message.guild.get_channel(tournament.cch)
    rch = message.guild.get_channel(tournament.rch)

    team_count = tournament.reged
    tslot = tournament.tslot
    valid_member_mentions = [mention for mention in message.mentions if not mention.bot] #filter out bots from the mentions

    if not crole:
        await message.author.send("Registration Paused") if message.author.dm_channel else None
        await message.reply("Confirm Role Not Found")
        tournament.status = "paused"
        tournament.save()

        #  tourney log the event
        await log_event(message, f"{rch.mention} paused\nreason : confirm role not found! seems like someone deleted that..", color=bot.color.red)

    bot.debug("✅ Check 3 passed - Confirm role exists.")

    if crole in message.author.roles:
        await message.delete() if message.guild.me.guild_permissions.manage_messages else None
        await log_event(message, f"{message.author} tried to register again in {rch.mention} but already has the confirm role.", bot.color.red)
        return await message.channel.send("**Seems like you're already registered as you have the confirm role.**", delete_after=5)

    bot.debug("✅ Check 4 passed - User does not have the confirm role.")

    if len(valid_member_mentions) < tournament.mentions:
        await log_event(message, f"{message.author} tried to register in {rch.mention} but failed due to insufficient mentions.", color=bot.color.red)
        meb = Embed(description=f"**Minimum {tournament.mentions} Mentions Required For Successfull Registration**", color=bot.color.red)
        await message.delete() if message.guild.me.guild_permissions.manage_messages else None
        return await message.channel.send(content=message.author.mention, embed=meb, delete_after=5)
    
    bot.debug("✅ Check 5 passed - User has sufficient mentions.")

    if team_count > tslot:
        overwrite = rch.overwrites_for(message.guild.default_role)
        overwrite.update(send_messages=False)
        await rch.set_permissions(message.guild.default_role, overwrite=overwrite)
        await message.delete()
        
        await log_event(message, f"{rch.mention} registration is closed.", bot.color.red)
        embed = Embed(description="**Registration Closed**", color=Color.red)
        embed.set_author(name=message.guild.name, icon_url=message.guild.icon if message.guild.icon else None)
        embed.timestamp = message.created_at
        return await rch.send(embed=embed)

    bot.debug("✅ Check 6 passed - Team count is within limits.")

    if tournament.faketag == "no":
        is_duplicate = await helper.duplicate_tag(crole=crole, message=message, slots=tslot)
        bot.debug(f"✅ check 6.1 - Checking for duplicate tags in {message.guild.name} for {message.author}.")
        if is_duplicate:
            await message.delete() if message.guild.me.guild_permissions.manage_messages else None
            fakeemb = Embed(title=f"The Member {is_duplicate.mention}, You Tagged is Already Registered In A Team. If You Think He Used `Fake Tags`, You can Contact `Management Team`", color=0xffff00)
            fakeemb.add_field(name="Team", value=f"[Registration Link]({is_duplicate.message.jump_url})")
            fakeemb.set_author(name=message.author, icon_url=message.author.display_avatar)
            await message.channel.send(embed=fakeemb, delete_after=60)
            await log_event(message, f"{message.author} tried to register in {rch.mention} but tagged {is_duplicate.mention} who is already registered in a team.", color=bot.color.red)
            return 

    bot.debug("✅ Check 7 passed - No duplicate tags found.")

    await message.author.add_roles(crole)
    await message.add_reaction("✅")
    reg_update(message)
    team_name = find_team(message)
    nfemb = Embed(color=0xffff00, description=f"**{team_count}) TEAM NAME: [{team_name.upper()}]({message.jump_url})**\n**Players** : {(', '.join(str(m) for m in message.mentions)) if message.mentions else message.author.mention} ")
    nfemb.set_author(name=message.guild.name, icon_url=message.guild.icon)
    nfemb.timestamp = message.created_at
    nfemb.set_thumbnail(url=message.author.display_avatar)

    if all([team_count >= 50, tournament.pub == "no", tournament.status == "started", tournament.created_at < timedelta(days=30)]):
        tournament.pub="yes"
        tournament.prize = await get_prize(cch)
        await tournament.save()

    await cch.send(f"{team_name.upper()} {message.author.mention}", embed=nfemb)
    await log_event(message, f"{message.author} registered in {rch.mention} with team name {team_name}.", color=bot.color.green)

 

################# NITRO ######################
async def nitrof(message:Message, bot:'Spruce'):
    if message.author.bot:return
    try:
      gnitro = db.guildbc.find_one({"guild_id" : message.guild.id})
    except Exception:
      return
    if not gnitro  and gnitro["nitro"] != "enabled": return
    try:
      webhook = utils.get(await message.channel.webhooks(), name="Spruce")
    except Exception:
      await message.reply("Nitro Module Enabled But Missing Permissions - `manage_messages` , `manage_webhooks`")
    if not webhook:
        try:
          webhook = await message.channel.create_webhook(name="Spruce")
        except Exception:
          await message.reply("Missing Permissions - `manage_messages` , `manage_webhooks`")
    words = message.content.split()
    for word in words:
        if word[0] == ":" and word[-1] == ":":
            emjn = word.replace(":", "")
            emoji = utils.get(bot.emojis, name=emjn)
            if emoji != None:
                if emoji.name in message.content:
                    msg1 = message.content.replace(":","").replace(f"{emoji.name}" , f"{emoji}")
                    allowed_mentions = AllowedMentions(everyone = False, roles=False, users=True)
                    nick = message.author.nick
                    if message.author.nick == None:
                        nick = message.author.name
                    await message.delete()
                    return await webhook.send(avatar_url=message.author.display_avatar, content=msg1, username=nick, allowed_mentions= allowed_mentions)