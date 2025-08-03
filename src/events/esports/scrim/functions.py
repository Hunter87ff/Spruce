from __future__ import annotations
import discord
from models.scrim import ScrimModel, Team
from typing import TYPE_CHECKING
from ext import EmbedBuilder

if TYPE_CHECKING:
    from cogs.esports import ScrimCog


async def handle_my_slot_callback(self : ScrimCog, interaction:discord.Interaction, scrim:ScrimModel, teams:list[Team]):
        if not teams:
            return await interaction.response.send_message(
                embed=EmbedBuilder.warning(self.YOU_ARE_NOT_REGISTERED
                ), ephemeral=True
            )

        options = [
            discord.SelectOption(
                label=f"{slot}) TEAM {team.name.upper()}",
                value=str(slot-1)
            ) for slot, team in enumerate(teams, start=1)
        ]

        # Create a select menu for the user to choose which slot to cancel
        select = discord.ui.Select(
            placeholder=self.SELECT_TEAM_PLACEHOLDER,
            options=options
        )

        async def select_callback(select_interaction:discord.Interaction):
            selected_slot = int(select.values[0])
            team = teams[selected_slot]

            embed = EmbedBuilder(
                title=f"Your Slot Details for Scrim: {scrim.name}",
                color=self.bot.color.blue
            )
            embed.add_field(name="Slot Number", value=str(selected_slot + 1), inline=False)
            embed.add_field(name="Team Name", value=team.name.upper(), inline=False)
            embed.add_field(name="Captain", value=f"<@{team.captain}>", inline=False)
            embed.add_field(name="Status", value="Registered", inline=False)
            embed.set_footer(text=f"Scrim ID: {scrim.reg_channel}")
            embed.timestamp = discord.utils.utcnow()
            await select_interaction.response.send_message(embed=embed, ephemeral=True)

        select.callback = select_callback
        view = discord.ui.View()
        view.add_item(select)
        return await interaction.response.send_message(view=view, ephemeral=True)
    

async def handle_teamname_change_callback(self : ScrimCog, interaction:discord.Interaction, scrim:ScrimModel, teams:list[Team]):
        if not teams:
            return await interaction.response.send_message(embed=EmbedBuilder.warning(self.YOU_ARE_NOT_REGISTERED), ephemeral=True)

        options = [
            discord.SelectOption(
                label=f"{slot}) TEAM {team.name.upper()}",
                value=str(slot-1)
            ) for slot, team in enumerate(teams, start=1)
        ]

        # Create a select menu for the user to choose which slot to change the team name
        select = discord.ui.Select(
            placeholder=self.SELECT_TEAM_PLACEHOLDER,
            options=options
        )

        # Callback for the select menu 
        async def select_callback(select_interaction:discord.Interaction):
            selected_slot = int(select.values[0])
            team = teams[selected_slot]

            modal = discord.ui.Modal(title="Change Team Name")
            team_name_input = discord.ui.TextInput(
                label="New Team Name",
                placeholder="Enter your new team name",
                required=True,
                max_length=30
            )
            modal.add_item(team_name_input)

            # Callback for the modal submission
            async def modal_callback(modal_interaction:discord.Interaction):
                new_team_name = team_name_input.value.strip()

                if not new_team_name:
                    return await modal_interaction.response.send_message(embed=EmbedBuilder.warning("Team name cannot be empty."), ephemeral=True)

                try:
                    team.name = new_team_name
                    await scrim.save()

                    await modal_interaction.response.send_message(embed=EmbedBuilder.success(f"Your team name has been changed to `{new_team_name}`."), ephemeral=True)

                except Exception as e:
                    await modal_interaction.response.send_message(embed=EmbedBuilder.warning(description=str(e)), ephemeral=True)

            modal.on_submit = modal_callback
            await select_interaction.response.send_modal(modal)

        select.callback = select_callback
        view = discord.ui.View()
        view.add_item(select)
        return await interaction.response.send_message(view=view, ephemeral=True)


async def handle_transfer_slot_callback(self : ScrimCog, interaction:discord.Interaction, scrim:ScrimModel, teams:list[Team]):
    """Handle the transfer slot callback for scrim interactions."""
    if not teams:
        return await interaction.response.send_message(embed=EmbedBuilder.warning(self.YOU_ARE_NOT_REGISTERED), ephemeral=True)

    options = [
        discord.SelectOption(
            label=f"{slot}) TEAM {team.name.upper()}",
            value=str(slot-1)
        ) for slot, team in enumerate(teams, start=1)
    ]

    # Create a select menu for the user to choose which slot to transfer
    select = discord.ui.Select(
        placeholder=self.SELECT_TEAM_PLACEHOLDER,
        options=options
    )

    async def select_callback(select_interaction:discord.Interaction):
        selected_slot = int(select.values[0])
        team = teams[selected_slot]

        view = discord.ui.View()
        member_input = discord.ui.UserSelect( placeholder="Select the member to transfer the slot to", min_values=1, max_values=1 )
        view.add_item(member_input)

        async def member_selection_callback(member_interaction:discord.Interaction):
            new_member = member_input.values[0]

            if not new_member or new_member.bot:
                return await member_interaction.response.send_message(embed=EmbedBuilder.warning("Invalid member."), ephemeral=True)

            try:
                team.captain = new_member.id
                await scrim.save()

                await member_interaction.response.send_message(embed=EmbedBuilder.success(f"Your slot has been transferred to {new_member.mention}."), ephemeral=True)

            except Exception as e:
                await member_interaction.response.send_message(embed=EmbedBuilder.warning(description=str(e)), ephemeral=True)

        member_input.callback = member_selection_callback
        await select_interaction.response.send_message(
            embed=EmbedBuilder(
                title=f"Transfer Slot for Scrim: {scrim.name}",
                description=f"Select a member to transfer your slot to. Current team: {team.name.upper()}",
                color=self.bot.color.blue
            ),
            view=view,
            ephemeral=True
        )

    select.callback = select_callback
    view = discord.ui.View()
    view.add_item(select)
    return await interaction.response.send_message(view=view, ephemeral=True)


async def handle_scrim_slot_manager_interaction(self : ScrimCog, interaction:discord.Interaction):
    """Handle scrim interactions."""

    custom_id = interaction.data.get("custom_id", "")
    reg_channel = self.bot.get_channel(int(custom_id.split("-")[0]))

    if not reg_channel or not isinstance(reg_channel, discord.TextChannel):
        await self.log(
            interaction.guild,
            f"Invalid registration channel for scrim interaction: {custom_id}. Channel not found or not a text channel.",
            self.bot.color.red
        )
        return await interaction.response.send_message(
            embed=discord.Embed(
                description="Invalid registration channel. Please contact management or try again later." , 
                color=self.bot.color.red
            ), ephemeral=True
        )

    scrim = await ScrimModel.find_by_reg_channel(reg_channel.id)

    if not scrim:
        return await interaction.response.send_message(embed=EmbedBuilder.warning(self.DEFAULT_NO_SCRIM_MSG), ephemeral=True)

    teams = [team for team in scrim.teams if team.captain == interaction.user.id]
    if any([
        interaction.user.guild_permissions.manage_guild,
        discord.utils.get(interaction.user.roles, name=self.SCRIM_MOD_ROLE),
    ]):
        teams = scrim.teams

    if custom_id.endswith("scrim-cancel-slot"):
        await self._cancel_slot(interaction, reg_channel, interaction.user)

    #  get the team details for the user
    if custom_id.endswith("scrim-my-slot"):
        await handle_my_slot_callback(self, interaction=interaction, scrim=scrim, teams=teams)


    if custom_id.endswith("scrim-team-name"):
        await handle_teamname_change_callback(self, interaction=interaction, scrim=scrim, teams=teams)


    if custom_id.endswith("scrim-transfer-slot"):
        await handle_transfer_slot_callback(self, interaction=interaction, scrim=scrim, teams=teams)
