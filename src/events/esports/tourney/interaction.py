from __future__ import annotations

from ext import EmbedBuilder
from discord import ui as dui
from ext.constants import Messages
from typing import TYPE_CHECKING, Callable
from models import TourneyModel
from discord import ButtonStyle


if TYPE_CHECKING:
    from discord.ui import View
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
    _select = await self.utils.slot_manager_team_select(tourney)
    _view = View()
    _view.add_item(_select)
    

    async def cancellation_confirmation(con_int: Interaction):
        _team = await tourney.get_team_by_id(_select.values[0]) if _select.values else None
        _name = _team.name if _team else ""
        await tourney.remove_team(_team)
        await con_int.response.send_message(
            embed=EmbedBuilder.success(f"Successfully removed Team {_name} from the tournament.")
        )

    _select.callback = cancellation_confirmation
    await interaction.followup.send(view=_view)



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

    await interaction.response.send_message("Coming Soon !!", ephemeral=True)
