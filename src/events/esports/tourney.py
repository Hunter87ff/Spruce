from __future__ import annotations


import traceback

from discord import Interaction
from ext import EmbedBuilder
from ext.constants import Messages
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
        await message.delete()
        await message.channel.send(
            embed=EmbedBuilder.warning("Slot channel not found. Please check the tournament configuration."),
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
        await message.add_reaction(self.bot.emoji.tick)
        _embed = self.utils.confirm_message_embed(_team, _tourney)
        _embed.set_thumbnail(url=message.author.avatar)
        _confirm_message = await _slot_channel.send(content=f"{_team.name.upper()} {message.author.mention}", embed=_embed)
        _team._id = _confirm_message.id  # Set the message ID for the team
        await _tourney.add_team(_team)

        await _confirm_message.add_reaction(self.bot.emoji.tick)
        await self.bot.sleep(0.5)  # Avoid rate limits
        await _confirm_message.add_reaction(self.bot.emoji.tick)

    except Exception as e:
        await message.channel.send(
            embed=EmbedBuilder.warning(f"Failed to register team: {str(e)}"),
            allowed_mentions=AllowedMentions.none()
        )
        # self.bot.debug(traceback.format_exc(), True)
        await self.bot.sleep(0.5)
        await message.delete()

        await self.utils.log(
            guild=message.guild,
            message=f"Failed to register team in tournament **{_tourney.name}**: {str(e)}",
            level="warning"
        )
        return
    


async def slot_manager_interaction(self: Esports, interaction: Interaction):
    _custom_ids = set([
        f"{self.bot.user.id}_tourney_slot_remove",
        f"{self.bot.user.id}_tourney_slot_check",
        f"{self.bot.user.id}_tourney_slot_rename",
        f"{self.bot.user.id}_tourney_slot_transfer",
    ])
    if interaction.data.get("custom_id") not in _custom_ids:
        return
    
    await interaction.response.defer(ephemeral=True)
    _event = await self.model.get_by_slot_manager(interaction.channel_id)
    if not _event:
        await interaction.followup.send(
            embed=EmbedBuilder.warning(Messages.NO_ACTIVE_TOURNAMENT),
            ephemeral=True
        )
        return
    

    
