from __future__ import annotations

from ext import EmbedBuilder
from discord.mentions import AllowedMentions


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models import TeamModel
    from discord import Message
    from cogs.esports.tourney.esports import Esports


async def handle_tourney_registration(self : Esports, message: Message):
    if message.author.bot or not message.guild:
        return
    
    if not await self.model.is_register_channel(message.channel.id):
        return
    
    # check for permissions
    if not all([
        message.channel.permissions_for(message.guild.me).send_messages,
        message.channel.permissions_for(message.guild.me).embed_links,
        message.channel.permissions_for(message.guild.me).read_message_history,
        message.channel.permissions_for(message.guild.me).add_reactions,
        message.channel.permissions_for(message.guild.me).manage_messages,
        message.channel.permissions_for(message.guild.me).manage_channels,
        message.channel.permissions_for(message.guild.me).manage_roles]):
        await self.utils.log(
            guild=message.guild,
            message="I need the following permissions to manage tournaments:\n"
                "- Send Messages\n"
                "- Embed Links\n"
                "- Read Message History\n"
                "- Add Reactions\n"
                "- Manage Messages\n"
                "- Manage Channels\n"
                "- Manage Roles"
        )
        return

    # Handle the message for the registered tournament channel
    _tourney = await self.model.get(message.channel.id)
    if not _tourney:
        return
    
    if any([
        not _tourney.status,
        _tourney.total_slots <= _tourney.team_count,
    ]):
        return
    
    _slot_channel = message.guild.get_channel(_tourney.slot_channel)
    if not _slot_channel:
        await self.delete_message(message)
        await message.channel.send(
            embed=EmbedBuilder.warning("Slot channel not found. Please check the tournament configuration."),
            allowed_mentions=AllowedMentions.none()
        )
        return
    
    if await _tourney.get_team_by_captain(message.author.id):
        await self.delete_message(message)
        await message.channel.send(
            embed=EmbedBuilder.warning("You are already registered in a team."),
            allowed_mentions=AllowedMentions.none()
        )
        return


    _teamname = self.utils.parse_team_name(message)
    _team: TeamModel = _tourney.create_team(
        tid=_tourney.reg_channel,
        name=_teamname,
        capt= message.author.id,
        members=set([mention.id for mention in message.mentions] or [message.author.id])
    )

    try:
        await _tourney.validate_team(_team)
        await self.add_reaction(message, self.bot.emoji.tick)
        _embed = self.utils.confirm_message_embed(_team, _tourney)
        _embed.set_thumbnail(url=message.author.avatar)
        _confirm_message = await _slot_channel.send(content=f"{_team.name.upper()} {message.author.mention}", embed=_embed)
        _team._id = _confirm_message.id  # Set the message ID for the team
        await _tourney.add_team(_team)

        await self.bot.sleep(0.5)  # Avoid rate limits
        await self.add_reaction(_confirm_message, self.bot.emoji.tick)

    except Exception as e:
        await message.channel.send(
            embed=EmbedBuilder.warning(f"Failed to register team: {str(e)}"),
            delete_after=5,
            allowed_mentions=AllowedMentions.none()
        )
        # self.bot.debug(traceback.format_exc(), True)
        await self.bot.sleep(0.5)
        await self.delete_message(message)

        await self.utils.log(
            guild=message.guild,
            message=f"Failed to register team in tournament **{_tourney.name}**: {str(e)}",
            level="warning"
        )
        return
    
