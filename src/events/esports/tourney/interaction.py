from __future__ import annotations


import discord
from ext import EmbedBuilder
from discord import ui as dui
from ext.constants import Messages
from typing import TYPE_CHECKING, Callable
from models import TourneyModel
from discord import ButtonStyle


if TYPE_CHECKING:
    from discord import Interaction
    from cogs.esports.tourney.esports import Esports



class ConfirmView(dui.View):
    def __init__(self, callback: Callable[[ConfirmView, bool], None], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.callback = callback

    async def on_timeout(self):
        await self.callback(self, timed_out=True)

    @dui.button(label="Confirm", style=ButtonStyle.red)
    async def confirm_button(self, interaction: Interaction, button: dui.Button):
        await self.callback(self, confirmed=True)

    @dui.button(label="Cancel", style=ButtonStyle.green)
    async def cancel_button(self, interaction: Interaction, button: dui.Button):
        await self.callback(self, confirmed=False)


async def cancel_slot_handler(self : Esports, tourney : TourneyModel, interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    _select = await self.utils.slot_manager_team_select(interaction.user.id, tourney)

    if not _select:
        await interaction.followup.send(
            embed=EmbedBuilder.warning("No team found."),
            ephemeral=True
        )
        return
    
    _view = dui.View()
    _view.add_item(_select)
    

    async def cancellation_confirmation(con_int: Interaction):
        _team_id = int(_select.values[0]) if _select.values else None
        _team = await tourney.get_team_by_id(_team_id) if _team_id else None
        if not _team:
            await con_int.response.send_message(
                embed=EmbedBuilder.warning("Team not found."),
                ephemeral=True
            )
            return
        slot_channel = interaction.guild.get_channel(tourney.slot_channel)
        _name = _team.name if _team else ""
        await tourney.remove_team(_team)
        _confirm_message = await slot_channel.fetch_message(_team_id or 8787)
        if _confirm_message:
            await self.bot.sleep()
            await _confirm_message.delete()

        await con_int.response.send_message(
            embed=EmbedBuilder.success(f"Successfully removed Team {_name} from the tournament."),
            ephemeral=True
        )

    _select.callback = cancellation_confirmation
    await interaction.followup.send(view=_view, ephemeral=True)



async def check_slot_handler(self: Esports, tourney: TourneyModel, interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    _select = await self.utils.slot_manager_team_select(interaction.user.id, tourney)

    if not _select:
        await interaction.followup.send(
            embed=EmbedBuilder.warning("No team found."),
            ephemeral=True
        )
        return

    _view = dui.View()
    _view.add_item(_select)

    async def check_confirmation(con_int: Interaction):
        _team_id = int(_select.values[0]) if _select.values else None
        _team = await tourney.get_team_by_id(_team_id) if _team_id else None
        if not _team:
            await con_int.response.send_message(
                embed=EmbedBuilder.warning("Team not found."),
                ephemeral=True
            )
            return

        _embed = EmbedBuilder(
            title=f"{tourney.name}".upper(),
            description=f"**Team Name : {_team.name}**\n"
            f'Players : {", ".join(f"<@{id}>" for id in _team.members)}'
        )
        await con_int.response.send_message(
            embed=_embed,
            ephemeral=True
        )

    _select.callback = check_confirmation
    await interaction.followup.send(view=_view, ephemeral=True)


async def rename_slot_handler(self : Esports, tourney : TourneyModel, interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    _select = await self.utils.slot_manager_team_select(interaction.user.id, tourney)

    if not _select:
        await interaction.followup.send(
            embed=EmbedBuilder.warning("No team found."),
            ephemeral=True
        )
        return
    
    _view = dui.View()
    _view.add_item(_select)

    async def rename_confirmation(con_int: Interaction):
        _team_id = int(_select.values[0]) if _select.values else None
        _team = await tourney.get_team_by_id(_team_id) if _team_id else None
        if not _team:
            await con_int.response.send_message(
                embed=EmbedBuilder.warning("Team not found."),
                ephemeral=True
            )
            return
        _team_name = await self.bot.helper.get_input(con_int, "Enter new team name:", placeholder="New Team Name", max_length=200)
        _team.name = _team_name
        await _team.save()

        await con_int.followup.send(
            embed=EmbedBuilder.success(f"Successfully renamed Team {_team.name} to {_team_name} in the tournament."),
            ephemeral=True
        )

    _select.callback = rename_confirmation
    await interaction.followup.send(view=_view, ephemeral=True)



async def transfer_slot_handler(self: Esports, tourney: TourneyModel, interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    _select = await self.utils.slot_manager_team_select(interaction.user.id, tourney)

    if not _select:
        await interaction.followup.send(
            embed=EmbedBuilder.warning("No team found."),
            ephemeral=True
        )
        return
    
    _view = dui.View()
    _view.add_item(_select)

    async def transfer_confirmation(con_int: Interaction):
        _team_id = int(_select.values[0]) if _select.values else None
        _team = await tourney.get_team_by_id(_team_id) if _team_id else None
        if not _team:
            await con_int.response.send_message(
                embed=EmbedBuilder.warning("Team not found."),
                ephemeral=True
            )
            return
        
        view = discord.ui.View()
        member_input = discord.ui.UserSelect( placeholder="Select the member to transfer the slot to", min_values=1, max_values=1 )
        view.add_item(member_input)

        async def member_mention_callback(mem_int : Interaction):
            new_captain = member_input.values[0]

            if await tourney.get_teams_by_player_id(new_captain.id):
                await mem_int.response.send_message(
                    embed=EmbedBuilder.warning("Member is already in a team."), ephemeral=True
                )
                return

            _team.captain = new_captain.id
            await _team.save()
            await mem_int.response.send_message(embed=EmbedBuilder.success(f"Successfully transferred the slot to {new_captain.mention}."), ephemeral=True)


        member_input.callback = member_mention_callback
        await con_int.response.send_message(
            view=view,
            ephemeral=True
        )
    
    _select.callback = transfer_confirmation
    await interaction.followup.send(view=_view, ephemeral=True)


async def slot_manager_interaction(self: Esports, interaction: Interaction):

    _custom_id = interaction.data.get("custom_id")

    if _custom_id in self.MANAGER_PREFIXES:
        await self.migrate_slot_manager(interaction)

    if _custom_id not in self.INTERACTION_IDS.ALL:
        return
    
    _event = await self.model.get_by_slot_manager(interaction.channel_id)
    if not _event:
        await interaction.followup.send(
            embed=EmbedBuilder.warning(Messages.NO_ACTIVE_TOURNAMENT),
            ephemeral=True
        )
        return
    
    if _custom_id == self.INTERACTION_IDS.CANCEL_SLOT:
        await cancel_slot_handler(self, _event, interaction)
        return
    
    if _custom_id == self.INTERACTION_IDS.CHECK_SLOT:
        await check_slot_handler(self, _event, interaction)
        return

    if _custom_id == self.INTERACTION_IDS.RENAME_SLOT:
        await rename_slot_handler(self, _event, interaction)
        return

    if _custom_id == self.INTERACTION_IDS.TRANSFER_SLOT:
        await transfer_slot_handler(self, _event, interaction)
        return

    await interaction.response.send_message("Coming Soon !!", ephemeral=True)
