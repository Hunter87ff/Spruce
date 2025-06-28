"""
This project is licensed under the GNU GPL v3.0.
Copyright (C) 2022 hunter87.dev@gmail.com
Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.
"""

import re, traceback
from typing import TYPE_CHECKING
from ext.modals import Tourney
from discord import utils, Embed, Message, TextChannel
from ext import helper, color as Color


if TYPE_CHECKING:
    from modules.bot import Spruce

IS_DEBUG = False

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
async def tourney(message: Message, bot: 'Spruce'):
    if message.author.bot or not message.guild:
        return
    
    # Cache permissions check result
    guild_me = message.guild.me
    channel_perms = message.channel.permissions_for(guild_me)
    
    required_perms = (
        guild_me.guild_permissions.manage_messages and
        guild_me.guild_permissions.manage_roles and
        guild_me.guild_permissions.send_messages and
        guild_me.guild_permissions.embed_links and
        channel_perms.read_message_history and
        guild_me.guild_permissions.manage_channels
    )
    
    if not required_perms:
        return
    

    if utils.get(message.author.roles, name=bot.config.TAG_IGNORE_ROLE):
        return

    tournament = Tourney.findOne(message.channel.id)
    bot.debug(f"Checking tournament status for {message.guild.name} in channel {message.channel.name}.", is_debug=IS_DEBUG)
    if not tournament:
        return

    bot.debug("✅ Check 1 passed - Tournament found.", is_debug=IS_DEBUG)


    if tournament.status == "paused":
        await message.channel.send(embed=Embed(description=f"{bot.emoji.cross} | Registration Paused", color=bot.color.red))
        bot.debug("❌ Check 2 failed - Tournament is paused.", is_debug=IS_DEBUG)
        await log_event(message, f"{message.author} tried to register in {message.channel.mention} but the tournament is paused.", color=bot.color.red)
        return
        

    bot.debug("✅ Check 2 passed - Tournament is not paused.", is_debug=IS_DEBUG)
    crole = message.guild.get_role(tournament.crole)
    cch = message.guild.get_channel(tournament.cch)
    rch = message.guild.get_channel(tournament.rch)

    if not cch:
        await message.author.send(embed=Embed(description=f"{bot.emoji.cross} | Registration Paused", color=bot.color.red)) if message.author.dm_channel else None
        await message.reply("Confirm Channel Not Found")
        tournament.status = "paused"
        tournament.save()

    team_count = tournament.reged
    tslot = tournament.tslot
    valid_member_mentions = [mention for mention in message.mentions if not mention.bot] #filter out bots from the mentions

    if not crole:
        await message.author.send(embed=Embed(description=f"{bot.emoji.cross} | Registration Paused", color=bot.color.red)) if message.author.dm_channel else None
        await message.reply("Confirm Role Not Found")
        tournament.status = "paused"
        tournament.save()

        #  tourney log the event
        await log_event(message, f"{rch.mention} paused\nreason : confirm role not found! seems like someone deleted that..", color=bot.color.red)
        bot.debug("❌ Check 3 failed - Confirm role does not exist.", is_debug=IS_DEBUG)
        return
    
    bot.debug("✅ Check 3 passed - Confirm role exists.", is_debug=IS_DEBUG)


    if crole.position >= guild_me.top_role.position:
        await message.author.send(embed=Embed(description=f"{bot.emoji.cross} | Registration Paused", color=bot.color.red)) if message.author.dm_channel else None
        await message.reply("Confirm Role Position Is Higher Than Bot's Top Role")
        tournament.status = "paused"
        tournament.save()

        #  tourney log the event
        await log_event(message, f"{rch.mention} paused\nreason : confirm role position is higher than bot's top role!", color=bot.color.red)
        bot.debug("❌ Check 3.1 failed - Confirm role position is higher than bot's top role.", is_debug=IS_DEBUG)
        return

    if crole in message.author.roles:
        await message.delete() if message else None
        await log_event(message, f"{message.author} tried to register again in {rch.mention} but already has the confirm role.", bot.color.red)
        return await message.channel.send(embed=Embed(description="**Seems like you're already registered as you have the confirm role.**", color=bot.color.red), delete_after=5)

    bot.debug("✅ Check 4 passed - User does not have the confirm role.", is_debug=IS_DEBUG)

    if len(valid_member_mentions) < tournament.mentions:
        await log_event(message, f"{message.author} tried to register in {rch.mention} but failed due to insufficient mentions.", color=bot.color.red)
        meb = Embed(description=f"**Minimum {tournament.mentions} Mentions Required For Successfull Registration**", color=bot.color.red)
        await message.delete()
        return await message.channel.send(content=message.author.mention, embed=meb, delete_after=5)
    

    bot.debug("✅ Check 5 passed - User has sufficient mentions.", is_debug=IS_DEBUG)

    if team_count > tslot:
        await bot.helper.lock_channel(message.channel)
        await message.delete()
         
        await log_event(message, f"{rch.mention} registration is closed.", bot.color.red)
        embed = Embed(description="**Registration Closed**", color=bot.color.red)
        embed.set_author(name=message.guild.name, icon_url=message.guild.icon if message.guild.icon else None)
        embed.timestamp = message.created_at
        return await message.channel.send(embed=embed)

    bot.debug("✅ Check 6 passed - Team count is within limits.", is_debug=IS_DEBUG)


    if tournament.faketag == "no":
        is_duplicate = await helper.duplicate_tag(crole=crole, message=message, slots=tournament.reged + 10)
        bot.debug(f"✅ check 6.1 - Checking for duplicate tags in {message.guild.name} for {message.author}.", is_debug=IS_DEBUG)

        if is_duplicate:
            await message.delete()
            fakeemb = Embed(
                description=f"The Member {is_duplicate.mention}, You Tagged is Already Registered In A Team. If You Think He Used `Fake Tags`, You can Contact `Management Team`", color=bot.color.red
            )
            fakeemb.add_field(name="Team", value=f"[Registration Link]({is_duplicate.message.jump_url})")
            fakeemb.set_author(name=message.author, icon_url=message.author.display_avatar)
            await message.channel.send(embed=fakeemb, delete_after=60)
            await log_event(message, f"{message.author} tried to register in {rch.mention} but tagged {is_duplicate.mention} who is already registered in a team.", color=bot.color.red)
            return 

    bot.debug("✅ Check 7 passed - No duplicate tags found.", is_debug=IS_DEBUG)

    await message.author.add_roles(crole)
    await message.add_reaction("✅")
    tournament.reged += 1

    bot.debug(f"✅ Check 8 passed - User {message.author} successfully registered in {rch.mention}.", is_debug=IS_DEBUG)
    team_name = bot.helper.parse_team_name(message)
    embed = Embed(color=bot.color.cyan, description=f"**{team_count}) TEAM NAME: [{team_name.upper()}]({message.jump_url})**\n**Players** : {(', '.join(str(m) for m in message.mentions)) if message.mentions else message.author.mention} ")
    embed.set_author(name=message.guild.name, icon_url=message.guild.icon if message.guild.icon else None)
    embed.timestamp = message.created_at
    embed.set_thumbnail(url=message.author.display_avatar or message.guild.icon or bot.user.display_avatar)

  
    bot.db.dbc.update_one(
        {"rch": rch.id},
        {"$set": {"reged" : tournament.reged}}
    )
    await cch.send(f"{team_name.upper()} {message.author.mention}", embed=embed)

    await log_event(message, f"{message.author} registered in {rch.mention} with team name {team_name}.", color=bot.color.green)