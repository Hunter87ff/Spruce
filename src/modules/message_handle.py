"""
This project is licensed under the GNU GPL v3.0.
Copyright (C) 2022 hunter87.dev@gmail.com
Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.
"""

import re, traceback, functools
from typing import TYPE_CHECKING
from ext.error import update_error_log
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


#Tourney System
async def tourney(message:Message):
    if message.author.bot or not message.guild:
        return
    
    log_channel = helper.get_tourney_log(message.guild)

    async def log_event(desc:str, color:int=None):
        if color is None:
            color = Color.random()
        if log_channel:

            _embed = Embed(description=desc, color=color)
            _embed.set_author(name=message.author, icon_url=message.author.display_avatar if message.author.display_avatar else None)
            _embed.timestamp = message.created_at

            return await log_channel.send(embed=_embed)


    td: dict[str] = find_by_reg(message)
    if not td :
        return
    
    elif utils.get(message.author.roles, name="tourney-mod") :
        return

    elif td["status"] == "paused":
        try:
            await message.author.send("Registration Paused")
            return
        except Exception:
            return print(traceback.format_exc())
        

    elif message.channel.id  != int(td["rch"]) or td["status"] != "started": return

    crole = message.guild.get_role(td.get("crole"))
    cch = message.guild.get_channel(td.get("cch"))
    rch = message.guild.get_channel(td.get("rch"))

    
    ments = td.get("mentions")
    team_count = td["reged"]
    tslot = td["tslot"]
    valid_member_mentions = [mention for mention in message.mentions if not mention.bot] #filter out bots from the mentions

    if not crole:
        await message.author.send("Registration Paused") if message.author.dm_channel else None
        await message.reply("Confirm Role Not Found")
        dbc.update_one({"rch" : message.channel.id}, {"$set" : {"status" : "paused"}})

        #  tourney log the event
        await log_event(f"{rch.mention} paused\nreason : confirm role not found! seems like someone deleted that..", color=Color.red)

    elif crole in message.author.roles:
        await message.delete() if message.guild.me.guild_permissions.manage_messages else None
        await log_event(f"{message.author} tried to register again in {rch.mention} but already has the confirm role.")
        return await message.channel.send("**Already Registered**", delete_after=5)
    
    elif team_count > tslot:
        overwrite = rch.overwrites_for(message.guild.default_role)
        overwrite.update(send_messages=False)
        await rch.set_permissions(message.guild.default_role, overwrite=overwrite)
        await message.delete()
        
        await log_event(f"{rch.mention} registration is closed.")
        return await rch.send("**Registration Closed**")
    
    messages = [message async for message in message.channel.history(limit=1100)]
    
    if len(valid_member_mentions) >= ments:
        for fmsg in messages:

            #IF DUPLICATE TAG ALLOWED
            ####################
            if td["faketag"] == "yes":
                await message.author.add_roles(crole)
                await message.add_reaction("✅")
                reg_update(message)
                team_name = find_team(message)
                nfemb = Embed(color=0xffff00, description=f"**{team_count}) TEAM NAME: [{team_name.upper()}]({message.jump_url})**\n**Players** : {(', '.join(str(m) for m in message.mentions)) if message.mentions else message.author.mention} ")
                nfemb.set_author(name=message.guild.name, icon_url=message.guild.icon)
                nfemb.timestamp = message.created_at
                nfemb.set_thumbnail(url=message.author.display_avatar)
                if team_count >= tslot*0.1 and td["pub"] == "no":
                    dbc.update_one({"rch" : td["rch"]}, {"$set" : {"pub" : "yes", "prize" : await get_prize(cch)}})
                return await cch.send(f"{team_name.upper()} {message.author.mention}", embed=nfemb)
            
            
            #IF DUPLICATE TAG NOT ALLOWED
            ########################

            if fmsg.author.id == message.author.id and len(messages) == 1:
                await message.add_reaction("✅")
                reg_update(message)
                team_name = find_team(message)
                femb = Embed(color=0xffff00, description=f"**{team_count}) TEAM NAME: [{team_name.upper()}]({message.jump_url})**\n**Players** : {(', '.join(str(m) for m in message.mentions)) if message.mentions else message.author.mention} ")
                femb.set_author(name=message.guild.name, icon_url=message.guild.icon.url if message.guild.icon else message.guild.me.avatar.url)
                femb.timestamp = message.created_at
                femb.set_thumbnail(url=message.author.display_avatar or message.author.default_avatar or message.guild.icon or message.guild.me.avatar.url)
                await cch.send(f"{team_name.upper()} {message.author.mention}", embed=femb)
                await message.author.add_roles(crole)
                if team_count >= tslot*0.1 and td["pub"] == "no":
                    dbc.update_one({"rch" : td["rch"]}, {"$set" : {"pub" : "yes", "prize" : await get_prize(cch)}})
                return await log_event(f"{message.author} registered in {rch.mention} with team name {team_name.upper()}", color=Color.green)

            if fmsg.author.id != message.author.id:
                ftch = await duplicate_tag(crole, message)
                if ftch != None:
                    fakeemb = Embed(title=f"The Member  {ftch}, You Tagged is Already Registered In A Team. If You Think He Used `Fake Tags`, You can Contact `Management Team`", color=0xffff00)
                    fakeemb.add_field(name="Team", value=f"[Registration Link]({fmsg.jump_url})")
                    fakeemb.set_author(name=message.author, icon_url=message.author.avatar)
                    if message: await message.delete()
                    await log_event(f"{message.author} tried to register in {rch.mention} but tagged {ftch} who is already registered in a team.", color=Color.red)
                    return await message.channel.send(embed=fakeemb, delete_after=60)
                try:
                    await message.author.add_roles(crole)
                    await message.add_reaction("✅")
                    reg_update(message)
                    team_name = find_team(message)
                    femb = Embed(color=0xffff00, description=f"**{team_count}) TEAM NAME: [{team_name.upper()}]({message.jump_url})**\n**Players** : {(', '.join(str(m) for m in message.mentions)) if message.mentions else message.author.mention} ")
                    femb.set_author(name=message.guild.name, icon_url=message.guild.icon)
                    femb.timestamp = message.created_at   
                    femb.set_thumbnail(url=message.author.display_avatar)
                    if team_count >= tslot*0.1 and td["pub"] == "no":
                        dbc.update_one({"rch" : td["rch"]}, {"$set" : {"pub" : "yes", "prize" : await get_prize(cch)}})
                    await log_event(f"{message.author} registered in {rch.mention} with team name {team_name.upper()}", color=Color.green)
                    return await cch.send(f"{team_name.upper()} {message.author.mention}", embed=femb)
                
                except Exception as e: 
                    update_error_log(traceback.format_exc())
                    await log_event(f"{message.author} failed to register in {rch.mention} with team name {team_name.upper()}\Issue raised : `{e}`", color=Color.red)


    elif len(valid_member_mentions) < ments:
        await log_event(f"{message.author} tried to register in {rch.mention} but failed due to insufficient mentions.", color=Color.red)

        meb = Embed(description=f"**Minimum {ments} Mentions Required For Successfull Registration**", color=0xff0000)
        await message.delete() if message.guild.me.guild_permissions.manage_messages else None

        return await message.channel.send(content=message.author.mention, embed=meb, delete_after=5)



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