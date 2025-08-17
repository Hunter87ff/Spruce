from __future__ import annotations

import discord
from discord.ext import commands
from models import ScrimModel

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from cogs.esports.scrim import ScrimCog








async def setup_group(self : ScrimCog, scrim:ScrimModel, slot_per_group:int = None, end_time:int=None, message:discord.Message = None):
    """Setup the scrim group with the provided scrim model."""

    if not scrim._id:
        return None
    
    if not slot_per_group:
        slot_per_group = scrim.total_slots
    
    reg_channel = self.bot.get_channel(scrim.reg_channel)

    if not reg_channel:
        raise ValueError("Registration channel not found in the scrim. Please update it.")

    end_time = int(end_time or discord.utils.utcnow().timestamp())

    if not reg_channel.permissions_for(reg_channel.guild.me).send_messages:
        raise commands.BotMissingPermissions(
            missing_permissions= [
                "send_messages",
                "manage_messages",
            ]
        )
    
    if not reg_channel.permissions_for(reg_channel.guild.me).read_message_history:
        raise commands.BotMissingPermissions(
            missing_permissions= [
                "read_message_history",
            ]
        )

    slot_channel = self.bot.get_channel(scrim.slot_channel)

    def format_slot(number:int, team_name:str):
        """Format the slot number and team name."""
        return f"Slot {number:02d} -> Team {team_name.upper()}"
    
    time_taken = end_time - (scrim.open_time - self.scrim_interval)  # Interval is now configurable
    group_embed = discord.Embed(
        title=f"**{self.bot.emoji.cup} | {scrim.name.upper()} SLOT LIST | {self.bot.emoji.cup}**",
        color=self.bot.color.random()
    )
    group_embed.set_footer(text=f"Registration Took : {self.time.by_seconds(time_taken)}")
    _description = "```\n"

    for i, team in enumerate(scrim.get_teams(), start=1):
        _description += format_slot(i, team.name) + "\n"
    _description += "```"

    if len(scrim.get_teams()) == 0:
        _description = "No teams registered yet."

    group_embed.description = _description

    _view = discord.ui.View(timeout=None)
    _buttons = [
        discord.ui.Button(emoji=self.bot.emoji.refresh, label="Refresh", style=discord.ButtonStyle.green, custom_id=f"{scrim.reg_channel}-{scrim.guild_id}-scrim-slot-refresh"),
    ]
    for _button in _buttons:
        _view.add_item(_button)

    if not message:
        await slot_channel.send(embed=group_embed, view=_view)

    if message:
        await message.edit(embed=group_embed, view=_view)

    await self.log(
        guild=reg_channel.guild,
        message=f"Scrim group setup completed for `{scrim.name}` in {reg_channel.mention}.\nGroup of {slot_per_group} slots",
    )

