"""
This project is licensed under the GNU GPL v3.0.
Copyright (C) 2022-present hunter87.dev@gmail.com
Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.
"""


from typing import TYPE_CHECKING
from ext import EmbedBuilder
from ext.modals import Tourney
from discord import utils, Embed, Message
from ext import Logger


if TYPE_CHECKING:
    from cogs.esports.tourney import TourneyCog

IS_DEBUG = False


async def add_reaction(message : Message, emoji : str):
    try:
        await message.add_reaction(emoji)

    except Exception as e:
        Logger.debug(f"Error adding reaction: {e}")



#Legacy Tourney Registration System
async def tourney_registration(self : "TourneyCog", message: Message):
    if not message.guild:
        return
    
    # Cache permissions check result
    guild_me = message.guild.me # type: ignore
    channel_perms = message.channel.permissions_for(guild_me)
    
    if not all([
        not message.author.bot,
        not message.is_system(),
        guild_me.guild_permissions.manage_messages,
        guild_me.guild_permissions.manage_roles,
        guild_me.guild_permissions.send_messages,
        guild_me.guild_permissions.embed_links,
        channel_perms.read_message_history,
        guild_me.guild_permissions.manage_channels
    ]):
        return
    

    if utils.get(message.author.roles, name=self.bot.config.TAG_IGNORE_ROLE): # type: ignore
        return

    tournament = Tourney.findOne(message.channel.id)
    if not tournament:
        return


    if tournament.status == "paused":
        await message.channel.send(embed=Embed(description=f"{self.bot.emoji.cross} | Registration Paused", color=self.bot.color.red))
        await self.log(message.guild, f"{message.author} tried to register in {message.channel.mention} but the tournament is paused.", color=self.bot.color.red)
        return
        
    crole = message.guild.get_role(tournament.crole)
    cch = message.guild.get_channel(tournament.cch)
    rch = message.guild.get_channel(tournament.rch)

    if not cch:
        await self.log(message.guild, f"{self.bot.emoji.cross} | Slot  Channel Not Found", color=self.bot.color.red)
        tournament.status = "paused"
        tournament.save()

    team_count = tournament.reged
    tslot = tournament.tslot
    valid_member_mentions = [mention for mention in message.mentions if not mention.bot] #filter out bots from the mentions

    if not crole:
        await self.log(message.guild, f"{self.bot.emoji.cross} | Confirm Role Not Found", color=self.bot.color.red)
        tournament.status = "paused"
        tournament.save()

        #  tourney log the event
        await self.log(message.guild, f"{rch.mention} paused\nreason : confirm role not found! seems like someone deleted that..", color=self.bot.color.red)
        return



    if crole.position >= guild_me.top_role.position:
        await self.log(message.guild, f"{self.bot.emoji.cross} | Confirm Role Position Is Higher Than Bot's Top Role", color=self.bot.color.red)
        tournament.status = "paused"
        tournament.save()
        return


    if crole in message.author.roles:
        await message.delete() if message else None
        await self.log(message.guild, f"{message.author} tried to register again in {rch.mention} but already has the confirm role.", color=self.bot.color.red)
        await message.channel.send(embed=Embed(description="**Seems like you're already registered as you have the confirm role.**", color=self.bot.color.red), delete_after=5)
        return 
    


    if len(valid_member_mentions) < tournament.mentions:
        await self.log(message.guild, f"{message.author} tried to register in {rch.mention} but failed due to insufficient mentions.", color=self.bot.color.red)
        meb = EmbedBuilder.warning(f"**Minimum {tournament.mentions} Mentions Required For Successfull Registration**")
        await message.delete()
        await message.channel.send(content=message.author.mention, embed=meb, delete_after=5)
        return


    if team_count > tslot:
        await self.bot.helper.lock_channel(message.channel)
        await message.delete()

        await self.log(message.guild, f"{rch.mention} registration is closed.", color=self.bot.color.red)
        embed = EmbedBuilder(title=None, description=f"{self.bot.emoji.reddot} **Registration Closed**", color=self.bot.base_color)
        embed.set_author(name=message.guild.name, icon_url=message.guild.icon if message.guild.icon else None)
        await message.channel.send(embed=embed)
        return



    if tournament.faketag == "no":
        is_duplicate = await self.bot.helper.duplicate_tag(self.bot, crole=crole, message=message, slots=tournament.reged + 10)

        if is_duplicate:
            await message.delete()
            fakeemb = Embed(
                description=f"The Member {is_duplicate.mention}, You Tagged is Already Registered In A Team. If You Think He Used `Fake Tags`, You can Contact `Management Team`", color=self.bot.color.red
            )
            fakeemb.add_field(name="Team", value=f"[Registration Link]({is_duplicate.message.jump_url})")
            fakeemb.set_author(name=message.author, icon_url=message.author.display_avatar)
            await message.channel.send(embed=fakeemb, delete_after=60)
            await self.log(message.guild, f"{message.author} tried to register in {rch.mention} but tagged {is_duplicate.mention} who is already registered in a team.", color=self.bot.color.red)
            return


    self.bot.cache.tourney_confirm.insert(rch, message)
    self.bot.cache.tourney_reged.insert(rch, message)

    await message.author.add_roles(crole)
    await add_reaction(message, emoji=self.bot.emoji.tick)
    tournament.reged += 1

    team_name = self.bot.helper.parse_team_name(message)
    embed = Embed(color=self.bot.color.cyan, description=f"**{team_count}) TEAM NAME: [{team_name.upper()}]({message.jump_url})**\n**Players** : {(', '.join(m.mention for m in message.mentions)) if message.mentions else message.author.mention} ")
    embed.set_author(name=message.guild.name, icon_url=message.guild.icon if message.guild.icon else None)
    embed.timestamp = message.created_at
    embed.set_thumbnail(url=message.author.display_avatar or message.guild.icon or self.bot.user.display_avatar)

    tournament.save()
    await cch.send(f"{team_name.upper()} {message.author.mention}", embed=embed)

    await self.log(message.guild, f"{message.author} registered in {rch.mention} with team name {team_name}.", color=self.bot.base_color)