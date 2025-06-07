"""
This project is licensed under the GNU GPL v3.0.
Copyright (C) 2022 hunter87.dev@gmail.com
Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.
"""

import discord
import functools
from enum import Enum
from typing import TYPE_CHECKING
from ext import constants, checks
from discord.ext import commands, tasks
from ext.models.scrim import ScrimModel, Team
from modules.config import IS_DEV_ENV
from discord import Embed, TextChannel,  Interaction,   app_commands as app


if TYPE_CHECKING:
    from modules.bot import Spruce    

_resolved_scrims: dict[str, bool] = {}

class ScrimCog(commands.GroupCog, name="scrim", group_name="scrim", command_attrs={"help":"Manage scrims for the server."}):
    """Currently in development mode!!"""
    def __init__(self, bot:"Spruce") -> None:
        self.bot = bot
        self.time = bot.time
        self.monitor_scrims.start()
        self.DEFAULT_START_TIME = "10:00 AM"
        self.DEFAULT_END_TIME = "4:00 PM"
        self.DEFAULT_TIMEZONE = constants.TimeZone.Asia_Kolkata.value
        self.DEFAULT_END_MESSAGE = "Scrim has ended! Thank you for participating."
        self.DEFAULT_NO_SCRIM_MSG = "No scrim found for the provided registration channel."
        self.DEFAULT_NO_IDP_ROLE = "No IDP role found for the scrim. Please set it using `/scrim set idp_role` command."
        self.TAG_IGNORE_ROLE = "scrim-tag-ignore"
        self.SCRIM_MOD_ROLE = "scrim-mod"
        self.SCRIM_LIMIT = 4
        self.scrim_interval = 86400 # seconds in 24 hours



    set_app = app.Group(name="set",  description="Set scrim configurations.")
    setup_app = app.Group(name="setup", description="Setup scrim configurations.")
    add_app = app.Group(name="add", description="Add scrim configurations.")
    remove_app = app.Group(name="remove", description="Remove scrim configurations.")


    async def log(self, guild:discord.Guild, message:str, color=None, **kwargs):
        """Log scrim related messages to the scrim log channel."""
        if not guild:
            return
        mention = kwargs.get("mention", None)
        scrim_log_channel = discord.utils.get(guild.text_channels, name=f"{self.bot.user.name.lower()}-scrim-log")
        if scrim_log_channel:
            await scrim_log_channel.send(
                content="@scrim-mod" if mention else None,
                embed=self.log_embed(message=message, color=color or self.bot.color.green)
            )



    def debug(self, message: str):
        """Debug function to print messages if DEBUG is True."""
        self.bot.debug(message=message, is_debug=False)


    def log_embed(self, message:str, color=None):
        embed = Embed(description=message, color=color or self.bot.color.green)
        return embed
    

    async def setup_group(self, scrim:ScrimModel, slot_per_group:int = None):
        """Setup the scrim group with the provided scrim model."""

        if not scrim._id:
            return None
        
        if not slot_per_group:
            slot_per_group = scrim.total_slots
        
        reg_channel = self.bot.get_channel(scrim.reg_channel)

        if not reg_channel:
            raise ValueError("Registration channel not found in the scrim. Please update it.")
        
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
        scrim.teams.extend(scrim.reserved)

        def format_slot(number:int, team_name:str):
            """Format the slot number and team name."""
            return f"Slot {number:02d} -> Team {team_name.upper()}"
        
        time_taken = int(discord.utils.utcnow().timestamp()) - (scrim.open_time - self.scrim_interval)  # Interval is now configurable
        group_embed = discord.Embed(
            title=f"**{self.bot.emoji.cup} | {scrim.name.upper()} SLOT LIST | {self.bot.emoji.cup}**",
            color=self.bot.color.random()
        )
        group_embed.set_footer(text=f"Registration Took : {self.time.by_seconds(time_taken)}")
        _description = "```" + "\n".join([format_slot(i, team.name) for i, team in enumerate(scrim.teams, start=1)]) + "```"

        if len(scrim.teams) == 0:
            _description = "No teams registered yet."

        group_embed.description = _description
        await slot_channel.send(embed=group_embed)

        
        await self.log(
            guild=reg_channel.guild,
            message=f"Scrim group setup completed for `{scrim.name}` in {reg_channel.mention}.",
        )


    @staticmethod
    def scrim_info_embed(scrim:ScrimModel):
        embed = Embed(
            title=f"{scrim.name}",
            color=discord.Color.green()
        )
        status = "Open" if scrim.status==True else "Closed" if scrim.status==False else "Disabled"
        available_slots = scrim.total_slots - (len(scrim.reserved) + len(scrim.teams))
        embed.add_field(name="Open Time", value=f"<t:{scrim.open_time}:t>(<t:{scrim.open_time}:R>)")
        embed.add_field(name="Close Time", value=f"<t:{scrim.close_time}:t>(<t:{scrim.close_time}:R>)")
        embed.add_field(name="Status", value=f"`{status}`")
        embed.add_field(name="Time Zone", value=f"`{scrim.time_zone}`")
        embed.add_field(name="Registration Channel", value=f"<#{scrim.reg_channel}>")
        embed.add_field(name="Slotlist Channel", value=f"<#{scrim.slot_channel}>")
        embed.add_field(name="Team Compulsion", value=f"`{'Yes' if scrim.team_compulsion else 'No'}`")
        embed.add_field(name="Multi Register", value=f"`{'Allowed' if scrim.multi_register else 'Not Allowed'}`")
        embed.add_field(name="Duplicate Tags", value=f"`{'Allowed' if scrim.duplicate_tag else 'Not Allowed'}`")
        embed.add_field(name="Mentions", value=f"`{scrim.mentions:02d}`")
        embed.add_field(name="Success Role", value=f"<@&{scrim.idp_role}>")
        embed.add_field(name="Ping Role", value=f"<@&{scrim.ping_role}>" if scrim.ping_role else "None")
        embed.add_field(name="Slots", value=f"`{available_slots}`/`{scrim.total_slots}`")
        embed.add_field(name="Reserved Slots", value=f"`{len(scrim.reserved)}`")
        embed.add_field(name="Open Days", value="`" + "`, `".join(scrim.open_days) + "`")
        embed.set_footer(text=f"Scrim ID: {scrim.reg_channel}")
        embed.timestamp = discord.utils.utcnow()
        return embed


    @app.command(name="create", description="Create a scrim for the server. (currently in testing mode. Use with caution!)")
    @app.guild_only()
    @app.describe(
        scrim_name="Name of the scrim",
        mentions="Number of mentions required to register a team (default: 4)",
        total_slots="Total number of slots for the scrim (default: 12)",
        open_time="examples: 10am, 10:00, 22:00, 7:00 PM (default: 10:00 AM)",
        close_time="examples: 10am, 10:00, 22:00, 7:00 PM (default: 4:00 PM)",
        timezone="Timezone of the scrim (default: Asia/Kolkata)",
        reg_channel="Registration channel for the scrim (default: create's new channel)",
        ping_role="Role to ping when the scrim starts (optional)",
    )
    @commands.cooldown(1, 15, commands.BucketType.guild)
    @checks.scrim_mod(interaction=True)
    async def create_scrim(
        self,
        ctx: Interaction,
        open_time: str = "10:00 AM",
        close_time: str = "4:00 PM",
        scrim_name: str = "Scrim",
        total_slots: app.Range[int, 1, 30] = 12,
        timezone: constants.TimeZone = constants.TimeZone.Asia_Kolkata,
        mentions: app.Range[int, 1, 5] = 4,
        idp_role: discord.Role | None = None,
        ping_role: discord.Role | None = None,
        reg_channel: TextChannel | None = None,
    ):
        """Create a new scrim
        """

        await ctx.response.defer(ephemeral=True)
        
        try:
            _parsed_open_time = int(self.time.parse_datetime(time_str=open_time, tz=timezone.value).timestamp())
            _parsed_close_time = int(self.time.parse_datetime(time_str=close_time, tz=timezone.value).timestamp())

        except ValueError as e:
            return await ctx.followup.send(f"{str(e)}. Please use HH:MM AM/PM format.", ephemeral=True)

        _existing_scrims = ScrimModel.find(guild_id=ctx.guild.id)
        if len(_existing_scrims) >= self.SCRIM_LIMIT:
            await self.log(ctx.guild, f"Scrim limit reached in {ctx.guild.name}. Cannot create new scrim.", color=self.bot.color.red)
            return await ctx.followup.send(embed=Embed(
                description=f"You can only have a maximum of {self.SCRIM_LIMIT} scrims in a server. Please delete some scrims before creating a new one.",
                color=self.bot.color.red
            ), ephemeral=True)

        _event_prefix = self.bot.helper.get_event_prefix(scrim_name)
        _scrim_category: discord.CategoryChannel
        _registration_channel: TextChannel
        
        # if registration channel is provided, use it, otherwise create a new one
        # 
        if reg_channel:
            if ScrimModel.find_by_reg_channel(reg_channel.id):
                return await ctx.followup.send("A scrim with this registration channel already exists.", ephemeral=True)
            

            _registration_channel = reg_channel
            if _registration_channel.category is not None:
                _scrim_category = _registration_channel.category

        else:
            _scrim_category = await ctx.guild.create_category(name=str(scrim_name))
            _registration_channel = await _scrim_category.create_text_channel(name=f"{_event_prefix}register-here")

        await _scrim_category.set_permissions(ctx.guild.default_role, send_messages=False, add_reactions=False)

        _self_override = _scrim_category.overwrites_for(ctx.guild.me)
        _self_override.update(
            send_messages=True, 
            manage_messages=True, 
            read_message_history=True, 
            add_reactions=True, 
            manage_channels=True, 
            external_emojis=True, 
            view_channel=True
        )
        await _scrim_category.set_permissions(ctx.guild.me, overwrite=_self_override)
        idp_role = idp_role or await ctx.guild.create_role(name=f"{_event_prefix}IDP", mentionable=True, color=self.bot.color.random())

        try:
            _scrim = ScrimModel(
                name=scrim_name,
                mentions=mentions,
                reg_channel=_registration_channel.id,
                idp_role=idp_role.id,
                guild_id=ctx.guild.id,
                scrim_name=scrim_name,
                open_time=_parsed_open_time,
                close_time=_parsed_close_time,
                total_slots=total_slots,
                time_zone=timezone.value,
                ping_role=ping_role.id if ping_role else None,
            )
            await _scrim.save()

            await ctx.followup.send(embed=self.scrim_info_embed(scrim=_scrim), ephemeral=True)

            await _registration_channel.send(embed=Embed(
                description=f"Scrim will start at <t:{_parsed_open_time}:t>(<t:{_parsed_open_time}:R>)",
                color=self.bot.color.random()
            ))
            await self.log( ctx.guild, f"{self.bot.emoji.tick} Scrim created by {ctx.user.mention} in {ctx.guild.name} with name: {scrim_name}", color=self.bot.color.green,)

        except ValueError as e:
            return await ctx.followup.send(f"Unable to create scrim: {str(e)}", ephemeral=True)
        

    class ScrimStatus(Enum):
        OPEN = "open"
        CLOSED = "closed"
        DISABLED = "disabled"



    @app.command(name="status", description="Update the status of a scrim by it's ID.")
    @app.guild_only()
    @checks.scrim_mod(interaction=True)
    @app.describe(
        reg_channel="ID of the scrim to update (required)",
        status="New status for the scrim (required)"
    )
    async def update_scrim_status(self, ctx:discord.Interaction, reg_channel:discord.TextChannel, status: ScrimStatus):
        """Update the status of a scrim by its ID."""
        await ctx.response.defer(ephemeral=True)

        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)

        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)

        _status = False
        if status == self.ScrimStatus.OPEN:
            _status = True

        elif status == self.ScrimStatus.CLOSED:
            _status = False

        elif status == self.ScrimStatus.DISABLED:
            _status = None

        _scrim.status = _status
        await _scrim.save()

        await ctx.followup.send(embed=discord.Embed(description=f"{self.bot.emoji.tick} | Scrim {reg_channel.mention} status updated to: {status.value}", color=self.bot.color.cyan), ephemeral=True)


    @app.command(name="start", description="Start a scrim by its ID.")
    @app.guild_only()
    @checks.scrim_mod(interaction=True)
    @app.describe(  reg_channel="ID of the scrim to start (required)")
    async def start_scrim(self, ctx:discord.Interaction, reg_channel:discord.TextChannel):
        """Start a scrim by its ID."""
        await ctx.response.defer(ephemeral=True)
        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)

        # Start the scrim
        _scrim.status = True
        ping_role =  f"<@&{_scrim.ping_role}>" if _scrim.ping_role else None
        await _scrim.save()
        await reg_channel.send(content=ping_role, embed=discord.Embed(
            description="**Scrim has started!**\n",
            color=self.bot.color.green
        ))
        await self.log(ctx.guild, f"Scrim `{_scrim.name}` has been started by {ctx.user.mention} in {reg_channel.mention}.")
        await ctx.followup.send(embed=discord.Embed(description=f"Scrim {reg_channel.mention} has been started.", color=self.bot.color.green), ephemeral=True)


    
    @app.command(name="idp", description="send the IDP for a scrim by it's channel ID")
    @app.guild_only()
    @checks.scrim_mod(interaction=True)
    @app.describe(
        room_id = "room id for the match",
        password = "password for the match",
        map= "map for the match",
        ping_role = "Ping role to notify IDP (optional)",
        reg_channel = "Registration channel of the scrim to send IDP (optional)",
        thumbnail = "Thumbnail image url for the embed (optional)",
        image = "Image url for the embed (optional)"
    )
    async def send_idp(self, ctx:discord.Interaction, room_id: str, password: str, map: str, ping_role: discord.Role = None, reg_channel: discord.TextChannel = None, thumbnail: str = None, image: str = None):
        await ctx.response.defer(ephemeral=True)
        channel = reg_channel or ctx.channel
        embed = discord.Embed(
            description=f"```\nRoom ID: {room_id}\nPassword: {password}\nMap: {map}\n```",
            color=self.bot.color.random()
        )
        embed.set_author(name=ctx.user.name, icon_url=ctx.user.display_avatar.url if ctx.user.display_avatar else None)
        embed.set_footer(text="Please Join within time.")
        embed.timestamp = discord.utils.utcnow()

        if thumbnail and self.bot.validator.is_valid_url(thumbnail):
            embed.set_thumbnail(url=thumbnail)

        if image and self.bot.validator.is_valid_url(image):
            embed.set_image(url=image)

        await channel.send(content=ping_role.mention if ping_role else None, embed=embed)
        await ctx.followup.send(content=f"IDP sent to {channel.mention}", embed=embed, ephemeral=True)



    @app.command(name="audit", description="Audit a scrim by its ID.")
    @app.guild_only()
    @checks.scrim_mod(interaction=True)
    @app.describe( reg_channel="Registration channel of the scrim to audit (required)")
    async def audit_scrim(self, ctx:discord.Interaction, reg_channel:discord.TextChannel):
        """Audit a scrim by its registration channel."""
        await ctx.response.defer(ephemeral=True)

        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)

        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)
        
        reg_channel: TextChannel = self.bot.get_channel(_scrim.reg_channel)
        idp_role = ctx.guild.get_role(_scrim.idp_role)
        slot_channel = self.bot.get_channel(_scrim.slot_channel)

        if not reg_channel:
            return await ctx.followup.send("Registration channel not found in the scrim. Please update it.", ephemeral=True)

        if not idp_role:
            return await ctx.followup.send("IDP role not found in the scrim. Please update it.", ephemeral=True)

        if not slot_channel:
            return await ctx.followup.send("Slot channel not found in the scrim. Please update it.", ephemeral=True)

        reg_read_perms = reg_channel.permissions_for(ctx.guild.me).read_messages
        reg_send_perms = reg_channel.permissions_for(ctx.guild.me).send_messages
        reg_manage_message_perms = reg_channel.permissions_for(ctx.guild.me).manage_messages
        reg_add_reactions_perms = reg_channel.permissions_for(ctx.guild.me).add_reactions

        slot_read_perms = slot_channel.permissions_for(ctx.guild.me).read_messages
        slot_send_perms = slot_channel.permissions_for(ctx.guild.me).send_messages
        slot_manage_message_perms = slot_channel.permissions_for(ctx.guild.me).manage_messages
        slot_add_reactions_perms = slot_channel.permissions_for(ctx.guild.me).add_reactions

        manage_role_perms = ctx.guild.me.guild_permissions.manage_roles
        manage_channel_perms = ctx.guild.me.guild_permissions.manage_channels
        read_history_perms = reg_channel.permissions_for(ctx.guild.me).read_message_history

        having_perm = all([
            reg_read_perms,
            reg_send_perms,
            reg_manage_message_perms,
            reg_add_reactions_perms,
            slot_read_perms,
            slot_send_perms,
            slot_manage_message_perms,
            slot_add_reactions_perms,
            manage_role_perms,
            manage_channel_perms,
            read_history_perms
        ])
        if having_perm:
            await ctx.followup.send(embed=discord.Embed(description="You have all the required permissions to manage the scrim."), ephemeral=True)
            return

        missing_perms = []

        if not reg_read_perms:
            missing_perms.append("read_messages")
        elif not reg_send_perms:
            missing_perms.append("send_messages")
        elif not reg_manage_message_perms:
            missing_perms.append("manage_messages")
        elif not reg_add_reactions_perms:
            missing_perms.append("add_reactions")
        elif not manage_role_perms:
            missing_perms.append("manage_roles")
        elif not manage_channel_perms:
            missing_perms.append("manage_channels")
        elif not read_history_perms:
            missing_perms.append("read_message_history")

        return await ctx.followup.send(
            f"Missing permissions to manage the scrim: `{'`, '.join(missing_perms)}. Please update the permissions and try again.",
            ephemeral=True
        )


    @app.command(name="info", description="Get information about a scrim by its ID.")
    @checks.scrim_mod(interaction=True)
    @app.guild_only()
    @app.describe(
        reg_channel="Registration channel of the scrim to get information about (required)",
    )
    async def scrim_info(self, ctx:discord.Interaction, reg_channel:discord.TextChannel):
        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        """Get information about a scrim by its registration channel."""
        await ctx.response.defer(ephemeral=True)
        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)

        await ctx.followup.send(
            embed=self.scrim_info_embed(scrim=_scrim),
            ephemeral=True
        )



    async def _cancel_slot(self, ctx:discord.Interaction, reg_channel:discord.TextChannel, captain:discord.Member):
        await ctx.response.defer(ephemeral=True)

        scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)
        
        # Find the team of the captain
        teams = [(team, slot) for  slot, team in enumerate(scrim.teams, start=1) if team.captain == captain.id]
        if any([
            captain.guild_permissions.manage_guild,
            captain.guild_permissions.administrator,
            discord.utils.get(captain.roles, name=self.SCRIM_MOD_ROLE)
        ]):
            teams = [(team, slot) for  slot, team in enumerate(scrim.teams, start=1)]

        if not teams:
            return await ctx.followup.send(embed=discord.Embed(description=f"No team found for captain {captain.mention} in scrim <#{scrim.reg_channel}>.", color=discord.Color.red()), ephemeral=True)

        idp_role = ctx.guild.get_role(scrim.idp_role)

        options = [
            discord.SelectOption(
                label=f"{slot}) TEAM {team.name.upper()}",
                value=str(slot-1)
            )
            for team, slot in teams
        ]

        # Create a select menu for the user to choose which slot to cancel
        select = discord.ui.Select(
            placeholder="Select a team to cancel the slot for...",
            options=options
        )

        async def select_callback(interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)

            # Get the selected option
            selected_option = select.values[0]
            team = scrim.teams[int(selected_option)]

            # Cancel the slot for the selected team
            scrim.teams.remove(team)
            await captain.remove_roles(idp_role, reason="Cancelled slot in scrim")
            await scrim.save()

            await ctx.followup.send(f"Cancelled slot for team {team.name.upper()}", ephemeral=True)

        select.callback = select_callback

        # Send the initial response with the select menu
        await ctx.followup.send("Please select a team to cancel the slot for:", ephemeral=True, view=discord.ui.View().add_item(select))



    # cancel slots
    @app.command(name="cancel_slot", description="Cancel slots for a scrim by its scrim and captain")
    @app.guild_only()
    @checks.scrim_mod(interaction=True)
    @app.describe(
        reg_channel="Registration channel of the scrim to cancel slots (required)",
        captain="ID of the captain whose slots to cancel (required)",
    )
    async def cancel_slot(self, ctx:discord.Interaction, reg_channel:discord.TextChannel, captain:discord.Member):
        await self._cancel_slot(ctx, reg_channel, captain)



    @app.command(name="delete", description="Delete a scrim by its ID.")
    @app.guild_only()
    @checks.scrim_mod(interaction=True)
    @app.describe(
        reg_channel="Registration channel of the scrim to delete (required)",
    )
    async def delete_scrim(self, ctx:discord.Interaction, reg_channel:discord.TextChannel):
        """Delete a scrim by its registration channel."""
        await ctx.response.defer(ephemeral=True)

        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)

        #  delete the scrim from the database
        await _scrim.delete()

        await ctx.followup.send(embed=discord.Embed(description=f"Scrim `{_scrim.name}` has been deleted successfully.", color=self.bot.color.red), ephemeral=True)


    @app.command(name="toggle", description="Toggle the status of a scrim by its ID.")
    @app.guild_only()
    @checks.scrim_mod(interaction=True)
    @app.describe(reg_channel="Registration channel of the scrim to toggle (required)",)
    async def toggle_scrim(self, ctx:discord.Interaction, reg_channel:discord.TextChannel):
        await ctx.response.defer(ephemeral=True)
        """Toggle the status of a scrim by its registration channel."""
        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)
        
        # Toggle the scrim status
        _scrim.status = not _scrim.status
        await _scrim.save()
        status = "opened" if _scrim.status else "closed"
        await reg_channel.send(embed=discord.Embed(description=f"The scrim has been {status}!", color=self.bot.color.green))
        await ctx.followup.send(embed=discord.Embed(description=f"Scrim {reg_channel.mention} has been {status}.", color=self.bot.color.green), ephemeral=True)



    @app.command(name="list", description="List all scrims in the server.")
    @app.guild_only()
    @checks.dev_only(interaction=True)
    async def list_scrims(self, ctx:discord.Interaction):
        """List all scrims in the server."""
        await ctx.response.defer()

        scrims = ScrimModel.find(guild_id=ctx.guild.id)
        if not scrims:
            return await ctx.followup.send("No scrims found in this server.")

        class InfoView(discord.ui.View):
            def __init__(self, scrims : list[ScrimModel]):
                super().__init__(timeout=None)
                self.scrims = scrims
                self.current_index = 0
                self.update_button_states()

            def update_button_states(self):
                # Update previous button
                self.previous_button.disabled = (self.current_index == 0)
                # Update next button
                self.next_button.disabled = (self.current_index >= len(self.scrims) - 1)


            @discord.ui.button(emoji="◀️", label="Previous", style=discord.ButtonStyle.primary, disabled=True)
            async def previous_button(self, interaction:discord.Interaction, button:discord.ui.Button):
                if self.current_index > 0:
                    self.current_index -= 1
                    embed = ScrimCog.scrim_info_embed(self.scrims[self.current_index])
                    # Update button states
                    self.update_button_states()
                    await interaction.response.edit_message(embed=embed, view=self)

            @discord.ui.button(emoji="✅", label="Done", style=discord.ButtonStyle.success)
            async def done_button(self, interaction:discord.Interaction, button:discord.ui.Button):
                # delete all the views
                await interaction.message.delete()
                self.stop()

            @discord.ui.button(emoji="🗑️", label="Delete", style=discord.ButtonStyle.danger)
            async def delete_button(self, interaction:discord.Interaction, button:discord.ui.Button):
                scrim = self.scrims[self.current_index]
                await scrim.delete()
                self.scrims.pop(self.current_index)
                self.current_index = 0  # Adjust index after deletion
                self.update_button_states()
                if len(self.scrims) == 0:
                    embed = discord.Embed(title="No Scrims", description="No scrims available.", color=discord.Color.red())
                    await interaction.message.edit(embed=embed, view=None)
                    return

                embed = ScrimCog.scrim_info_embed(self.scrims[self.current_index])
                embed.set_footer(text=f"Scrim ID: {self.scrims[self.current_index].id} | Page {self.current_index + 1}/{len(self.scrims)}")
                await interaction.message.edit(embed=embed, view=self)


            @discord.ui.button(emoji="▶️", label="Next", style=discord.ButtonStyle.primary)
            async def next_button(self, interaction:discord.Interaction, button:discord.ui.Button):
                if self.current_index < len(self.scrims) - 1:
                    self.current_index += 1
                    embed = ScrimCog.scrim_info_embed(self.scrims[self.current_index])
                    # Update button states
                    self.update_button_states()
                    await interaction.response.edit_message(embed=embed, view=self)


        embed = self.scrim_info_embed(scrims[0])
        view = InfoView(scrims)
        await ctx.followup.send(embed=embed, view=view, ephemeral=True)



    @set_app.command(name="log", description="Setup or update the scrim log channel.")
    @app.guild_only()
    @checks.scrim_mod(interaction=True)
    async def scrim_log(self, ctx:discord.Interaction):
        await ctx.response.defer(ephemeral=True)

        log_channel = self.bot.helper.get_scrim_log(ctx.guild)
        if log_channel:
            if log_channel.permissions_for(ctx.guild.me).send_messages:
                return await ctx.followup.send(
                    f"Scrim log channel is already set to <#{log_channel.id}>.",
                    ephemeral=True
                )
            else:
                return await ctx.followup.send(
                    f"Scrim log channel is set to <#{log_channel.id}>, but I don't have permission to send messages there. Please update the permissions and try again.",
                    ephemeral=True
                )
        else:
            log_channel = await ctx.guild.create_text_channel(name=f"{self.bot.user.name}-scrim-log")

        await log_channel.set_permissions(ctx.guild.default_role, read_messages=False)
        await log_channel.set_permissions(ctx.guild.me,
                                            read_messages=True,
                                            send_messages=True,
                                            attach_files=True,
                                            manage_channels=True,
                                            manage_messages=True,
                                            add_reactions=True,
                                            external_emojis=True
        )
        await ctx.followup.send(
            f"Scrim log channel has been set to <#{log_channel.id}>. All scrim related logs will be sent there.",
            ephemeral=True
        )



    @set_app.command(name="idp_channel", description="Set or update the IDP channel for a scrim.")
    @app.guild_only()
    @app.describe(
        reg_channel="Registration channel of the scrim to set IDP channel (required)",
        idp_channel="IDP channel to set for the scrim (required)",
    )
    @checks.scrim_mod(interaction=True)
    async def set_idp_channel(self, ctx:discord.Interaction, reg_channel:discord.TextChannel, idp_channel:discord.TextChannel):
        """Set or update the IDP channel for a scrim."""
        await ctx.response.defer(ephemeral=True)

        scrim  = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)
        
        # Update the IDP channel in the scrim
        idp_role = ctx.guild.get_role(scrim.idp_role)
        if not idp_role:
            await self.log(ctx.guild, self.DEFAULT_NO_IDP_ROLE, color=self.bot.color.red)
            return await ctx.followup.send(self.DEFAULT_NO_IDP_ROLE, ephemeral=True)

        event_prefix = self.bot.helper.get_event_prefix(scrim.name)
        idp_channel = idp_channel or await ctx.guild.create_text_channel(
            name=f"{event_prefix}-idp",
            category=reg_channel.category,
        )
        idp_channel.set_permissions(
            ctx.guild.default_role,
            send_messages=False,
            read_messages=True
        )
        override = idp_channel.overwrites_for(idp_role)
        override.update(send_messages=False, read_messages=True, add_reactions=True)
        await idp_channel.set_permissions(idp_role, overwrite=override)

        my_override = idp_channel.overwrites_for(ctx.guild.me)
        my_override.update(send_messages=True, read_messages=True, add_reactions=True, manage_messages=True, embed_links=True)
        await idp_channel.set_permissions(ctx.guild.me, overwrite=my_override)

        await self.log(ctx.guild, f"IDP channel for scrim `{scrim.name}` has been set to {idp_channel.mention}.", color=self.bot.color.green)
        await ctx.followup.send(
            embed=Embed(
                description=f"IDP channel for scrim `{scrim.name}` has been set to {idp_channel.mention}.",
                color=self.bot.color.green
        ))

    class DuplicateTagCheck(Enum):
        ALLOW = 1
        DISALLOW = 0


    @set_app.command(name="fake_tag", description="Enable or disable fake tag filter for a scrim.")
    @app.guild_only()
    @app.describe(
        reg_channel="Registration channel of the scrim to set fake tag filter (required)",
        fake_tag="Enable or disable fake tag filter (required)",
    )
    @checks.scrim_mod(interaction=True)
    async def set_fake_tag(self, ctx:discord.Interaction, reg_channel:discord.TextChannel, fake_tag:DuplicateTagCheck):
        """Enable or disable fake tag filter for a scrim."""
        await ctx.response.defer(ephemeral=True)

        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)

        # Update the fake tag filter in the scrim
        _scrim.duplicate_tag = bool(fake_tag.value)
        await _scrim.save()

        await ctx.followup.send(f"Fake tag filter for scrim `{_scrim.name}` has been {fake_tag.value}.", ephemeral=True)



    @set_app.command(name="idp_role", description="Set or update the IDP role for a scrim.")
    @app.guild_only()
    @app.describe(
        reg_channel="Registration channel of the scrim to set IDP role (required)",
        idp_role="IDP role to set for the scrim (required)",
    )
    @checks.scrim_mod(interaction=True)
    async def set_idp_role(self, ctx:discord.Interaction, reg_channel:discord.TextChannel, idp_role:discord.Role):
        """Set or update the IDP role for a scrim."""
        await ctx.response.defer(ephemeral=True)

        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)

        #  update the idp role in the scrim
        _scrim.idp_role = idp_role.id
        await _scrim.save()

        await ctx.followup.send(f"IDP role for scrim `{_scrim.name}` has been set to {idp_role.mention}.", ephemeral=True)



    @set_app.command(name="ping_role", description="Set or update the ping role for a scrim.")
    @app.guild_only()
    @app.describe(
        reg_channel="Registration channel of the scrim to set ping role (required)",
        ping_role="Ping role to set for the scrim (required)",
    )
    @checks.scrim_mod(interaction=True)
    async def set_ping_role(self, ctx:discord.Interaction, reg_channel:discord.TextChannel, ping_role:discord.Role):
        """Set or update the ping role for a scrim."""
        await ctx.response.defer(ephemeral=True)

        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)

        #  update the ping role in the scrim
        _scrim.ping_role = ping_role.id
        await _scrim.save()

        await ctx.followup.send(f"Ping role for scrim `{_scrim.name}` has been set to {ping_role.mention}.", ephemeral=True)


    @set_app.command(name="mentions", description="Set or update the number of mentions required to register a team for a scrim.")
    @app.guild_only()
    @app.describe(
        reg_channel="Registration channel of the scrim to update mentions (required)",
        mentions="Number of mentions required to register a team (required)",
    )
    @checks.scrim_mod(interaction=True)
    async def set_mentions(self, ctx:discord.Interaction, reg_channel:discord.TextChannel, mentions:int):
        """Set or update the number of mentions required to register a team for a scrim."""
        await ctx.response.defer(ephemeral=True)

        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)

        #  update the mentions in the scrim
        _scrim.mentions = mentions
        await _scrim.save()

        await ctx.followup.send(f"Mentions required for scrim `{_scrim.name}` have been set to {mentions}.", ephemeral=True)


    
    @set_app.command(name="total_slots", description="Set or update the total number of slots for a scrim.")
    @app.guild_only()
    @app.describe(
        reg_channel="Registration channel of the scrim to update total slots (required)",
        total_slots="Total number of slots for the scrim (required)",
    )
    @checks.scrim_mod(interaction=True)
    async def set_total_slots(self, ctx:discord.Interaction, reg_channel:discord.TextChannel, total_slots:int):
        """Set or update the total number of slots for a scrim."""
        await ctx.response.defer(ephemeral=True)

        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)

        #  update the total slots in the scrim
        _scrim.total_slots = total_slots
        await _scrim.save()

        await ctx.followup.send(f"Total slots for scrim `{_scrim.name}` have been set to {total_slots}.", ephemeral=True)



    @set_app.command(name="open_time", description="Set or update the open time for a scrim.")
    @app.guild_only()
    @checks.scrim_mod(interaction=True)
    @app.describe(
        reg_channel="Registration channel of the scrim to update open time (required)",
        open_time="Open time for the scrim (required)",
    )
    async def set_open_time(self, ctx:discord.Interaction, reg_channel:discord.TextChannel, open_time:str):
        """Set or update the open time for a scrim."""
        await ctx.response.defer(ephemeral=True)

        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)

        parsed_open_time = int(self.time.parse_datetime(time_str=open_time, tz=_scrim.time_zone).timestamp())
        
        #  update the open time in the scrim
        _scrim.open_time = parsed_open_time
        await _scrim.save()

        

        await ctx.followup.send(f"Open time for scrim <#{reg_channel.id}> has been set to <t:{parsed_open_time}:t>.", ephemeral=True)


    @set_app.command(name="close_time", description="Set or update the close time for a scrim.")
    @app.guild_only()
    @checks.scrim_mod(interaction=True)
    @app.describe(reg_channel="Registration channel of the scrim to update close time (required)",
                  close_time="Close time for the scrim (required)")
    async def set_close_time(self, ctx:discord.Interaction, reg_channel:discord.TextChannel, close_time:str):
        """Set or update the close time for a scrim."""
        await ctx.response.defer(ephemeral=True)

        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)

        try:
            parsed_close_time = int(self.time.parse_datetime(time_str=close_time, tz=_scrim.time_zone).timestamp())
            
        except ValueError:
            return await ctx.followup.send(f"Invalid close time format. Please use HH:MM AM/PM format.", ephemeral=True)

        #  update the close time in the scrim
        _scrim.close_time = parsed_close_time
        await _scrim.save()

        await ctx.followup.send(f"Close time for scrim <#{reg_channel.id}> has been set to <t:{parsed_close_time}:t>.", ephemeral=True)


    @set_app.command(name="time_zone", description="Set or update the time zone for a scrim.")
    @app.guild_only()
    @checks.scrim_mod(interaction=True)
    @app.describe(
        reg_channel="Registration channel of the scrim to update time zone (required)",
        time_zone="Time zone for the scrim",
        custom_zone="If your time zone is not listed, you can provide a custom time zone (optional<priority>, e.g., 'Asia/Tokyo')",
    )
    @app.checks.bot_has_permissions(manage_roles=True, manage_channels=True, send_messages=True, embed_links=True)
    async def set_time_zone(self, ctx:discord.Interaction, reg_channel:discord.TextChannel, time_zone:constants.TimeZone=constants.TimeZone.Asia_Kolkata, custom_zone:str=None):
        """Set or update the time zone for a scrim."""
        await ctx.response.defer(ephemeral=True)

        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)
        
        if all([time_zone, custom_zone]):
            return await ctx.followup.send("please select a time zone or provide a custom one if not listed", ephemeral=True)

        if custom_zone and self.time.is_valid_tz(custom_zone):
            _scrim.time_zone = custom_zone

        elif not custom_zone and time_zone:
            _scrim.time_zone = time_zone.value

        await _scrim.save()

        await ctx.followup.send(f"Time zone for scrim <#{reg_channel.id}> has been set to {time_zone.value}.", ephemeral=True)



    @set_app.command(name="reg_channel", description="Set or update the registration channel for a scrim.")
    @app.guild_only()
    @checks.scrim_mod(interaction=True)
    @app.describe( reg_channel="Registration channel of the scrim to update (required)")
    @app.checks.bot_has_permissions(manage_roles=True, manage_channels=True, send_messages=True, embed_links=True)
    async def set_reg_channel(self, ctx:discord.Interaction, reg_channel:discord.TextChannel):
        """Set or update the registration channel for a scrim."""
        await ctx.response.defer(ephemeral=True)

        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)

        #  update the registration channel in the scrim
        _scrim.reg_channel = reg_channel.id
        await _scrim.save()

        await ctx.followup.send(f"Registration channel for scrim `{_scrim.name}` has been set to <#{reg_channel.id}>.", ephemeral=True)


    @set_app.command(name="slot_channel", description="Set or update the slot channel for a scrim.")
    @app.guild_only()
    @checks.scrim_mod(interaction=True)
    @app.describe(
        reg_channel="Registration channel of the scrim to update slot channel (required)",
        slot_channel="Slot channel for the scrim (required)",
    )
    @app.checks.bot_has_permissions(manage_roles=True, manage_channels=True, send_messages=True, embed_links=True)
    async def set_slot_channel(self, ctx:discord.Interaction, reg_channel:discord.TextChannel, slot_channel:discord.TextChannel):
        """Set or update the slot channel for a scrim."""
        await ctx.response.defer(ephemeral=True)

        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)

        #  update the slot channel in the scrim
        _scrim.slot_channel = slot_channel.id
        await _scrim.save()

        await ctx.followup.send(f"Slot channel for scrim `{_scrim.name}` has been set to <#{slot_channel.id}>.", ephemeral=True)


    @setup_app.command(name="group", description="setup scrim group.")
    @app.guild_only()
    @app.describe(reg_channel="Registration channel of the scrim to setup group (required)",)
    @checks.scrim_mod(interaction=True)
    async def scrim_group_setup(self, ctx:Interaction, reg_channel:TextChannel):
        """Setup the scrim group with the provided registration channel."""
        await ctx.response.defer(ephemeral=True)
         # remove this before release
        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)

        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)

        try:
            await self.setup_group(scrim=_scrim)
            await ctx.followup.send("Scrim group setup successfully.", ephemeral=True)

        except Exception as e:
            return await ctx.followup.send(f"Error occurred while setting up scrim group: {str(e)}", ephemeral=True)


    @app.command(name="reserved_slots", description="View the reserved slots for a scrim.")
    @app.guild_only()
    @checks.scrim_mod(interaction=True)
    @app.describe(reg_channel="Registration channel of the scrim to view or update reserved slots (required)")
    async def view_reserved_slots(self, ctx:discord.Interaction, reg_channel:discord.TextChannel):
        await ctx.response.defer(ephemeral=True)
        """View or update the reserved slots for a scrim."""
        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)
        
        if not _scrim.reserved:
            return await ctx.followup.send("No reserved slots found for this scrim.", ephemeral=True)

        reserved_slots = "**" + str("\n".join([f"{index}) {team.name.upper()} <@{team.captain}>" for index, team in enumerate(_scrim.reserved, start=1)])) + "**"
        embed = Embed(
            title=f"Reserved Slots for Scrim: {_scrim.name}",
            description=reserved_slots,
            color=self.bot.color.random()
        )
        await ctx.followup.send(embed=embed, ephemeral=True)


    @add_app.command(name="reserved_slots", description="View or update the reserved slots for a scrim.")
    @app.guild_only()
    @checks.scrim_mod(interaction=True)
    @app.describe(
        reg_channel="Registration channel of the scrim to view or update reserved slots (required)",
        team_name="Name of the team to reserve a slot (required)",
        captain="ID of the captain of the team (required)",
    )
    @checks.scrim_mod(interaction=True)
    async def add_reserved_slots(self, ctx:discord.Interaction, reg_channel:discord.TextChannel, team_name:str, captain:discord.Member):
        """View or update the reserved slots for a scrim."""
        await ctx.response.defer(ephemeral=True)
        

        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)
        
        if(len(_scrim.reserved) >= _scrim.total_slots):
            return await ctx.followup.send("All slots are already reserved for this scrim.", ephemeral=True)

        try:
            _scrim.add_reserved(captain=captain.id, name=team_name)
            await _scrim.save()
            await ctx.followup.send(f"Reserved slot for team `{team_name}` has been added successfully.", ephemeral=True)

        except ValueError as e:
            await ctx.followup.send(f"{str(e)}", ephemeral=True)


    @add_app.command(name="slot", description="Add a slot for a team in a scrim.")
    @app.guild_only()
    @checks.scrim_mod(interaction=True)
    @app.describe(
        reg_channel="Registration channel of the scrim to add a slot (required)",
        captain="ID of the captain of the team to add a slot for (required)",
        team_name="Name of the team to add a slot for (required)",
    )
    async def add_slot(self, ctx:discord.Interaction, reg_channel:discord.TextChannel, captain:discord.Member, team_name:str):
        """Add a slot for a team in a scrim."""
        await ctx.response.defer(ephemeral=True)

        scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)

        try:
            scrim.add_team(captain=captain.id, name=team_name)

        except Exception as e:
            return await ctx.followup.send(str(e), ephemeral=True)

        await scrim.save()
        await ctx.followup.send(f"Slot for team `{team_name}` has been added successfully.", ephemeral=True)


    @remove_app.command(name="reserved_slots", description="View or remove a reserved slot for a scrim.")
    @app.guild_only()
    @checks.scrim_mod(interaction=True)
    @app.describe(
        reg_channel="Registration channel of the scrim to view or remove reserved slots (required)",
        captain="ID of the captain of the team whose reserved slot you want to remove (required)",
    )
    async def remove_reserved_slots(self, ctx:discord.Interaction, reg_channel:discord.TextChannel, captain:discord.Member):
        """View or remove a reserved slot for a scrim."""
        await ctx.response.defer(ephemeral=True)

        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)

        #  find the reserved slot by captain id
        if captain.id not in _scrim.reserved:
            return await ctx.followup.send(f"No reserved slot found for captain {captain.mention} in this scrim.", ephemeral=True)
        
        #  remove the reserved slot
        _scrim.reserved.remove(captain.id)
        await _scrim.save()

        await ctx.followup.send(f"Reserved slot for captain {captain.mention} has been removed successfully.", ephemeral=True)


    @commands.Cog.listener()
    async def on_scrim_open_time_hit(self, scrim:ScrimModel):
        """Listener for when a scrim start time is hit."""
        self.debug(f"Scrim open time hit for {scrim.name} in {scrim.guild_id} at {self.time.now()}")

        #  check for open days
        week_day = self.time.now(scrim.time_zone).strftime("%a").lower()[0:2]
        if week_day not in scrim.open_days:
            self.debug(f"Scrim {scrim.name} is not open today ({week_day}). Skipping opening.")
            return

        
        _channel = self.bot.get_channel(scrim.reg_channel)


        if not _channel:
            guild = self.bot.get_guild(scrim.guild_id)

            # identify if the open time is 30 days ago or more
            if scrim.open_time < (self.time.now(scrim.time_zone).timestamp() - int(self.scrim_interval * 30)):  # 30 days in seconds
                await self.log(
                    guild,
                    f"Scrim {scrim.name} registration channel not found, and the scrim is older than 30 days. Deleting the scrim.",
                    self.bot.color.red
                )
                await scrim.delete()
                
            self.debug(f"Scrim {scrim.name} registration channel not found. Skipping opening.")
            return
        
        _idp_role = _channel.guild.get_role(scrim.idp_role)

        if not _channel.guild.me.guild_permissions.manage_roles:
            return await self.log( _channel.guild, f"Scrim {_channel.mention} could not be started as I don't have permission to manage roles." )
        
        for member in _idp_role.members:
            await member.remove_roles(_idp_role, reason="Scrim registration started, removing IDP role.")

        # upda the scrim status and open time
        scrim.status = True
        scrim.open_time += self.scrim_interval 
        scrim.clear_teams()
        await scrim.save()

        ping_role_mention  = f"<@&{scrim.ping_role}>" if (scrim.ping_role != "@everyone" and scrim.ping_role) else None
        available_slots = scrim.total_slots - (len(scrim.reserved) + len(scrim.teams))
        start_message = await _channel.send(
            content=ping_role_mention,
            embed = discord.Embed(
                title=f"**{self.bot.emoji.cup} | REGISTRATION STARTED | {self.bot.emoji.cup}**",
                description=f"**{self.bot.emoji.tick} | AVAILABLE SLOTS : {available_slots}/{scrim.total_slots}\n{self.bot.emoji.tick} | RESERVED SLOTS : {len(scrim.reserved)}\n{self.bot.emoji.tick} | REQUIRED MENTIONS : {scrim.mentions}\n{self.bot.emoji.tick} | CLOSE TIME : <t:{int(scrim.close_time)}:t>(<t:{int(scrim.close_time)}:R>)**",
                color=self.bot.color.green
            )
        )


        await self.bot.helper.unlock_channel(_channel)

        if _channel.permissions_for(_channel.guild.me).add_reactions:
            await start_message.add_reaction(self.bot.emoji.tick)


        def purge_filter(message: discord.Message):

            if message.id == start_message.id:
                return False

            if self.bot.is_ws_ratelimited():
                return False

            return True

        if scrim.clear_messages and _channel.permissions_for(_channel.guild.me).manage_messages:
            await _channel.purge(limit=scrim.total_slots+10, check=purge_filter, before=start_message)

        await self.log(
            _channel.guild,
            f"Scrim <#{_channel.id}> has been opened for registration. Available slots: {available_slots}/{scrim.total_slots}.",
            self.bot.color.green
        )




    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        """Listener for when a message is sent in a scrim registration channel."""
        if not message.guild:
            return 
        
        if not all([
            not message.author.bot,
            isinstance(message.channel, discord.TextChannel),
            message.guild,
            message.guild.me.guild_permissions.manage_messages,
            message.guild.me.guild_permissions.add_reactions,
            message.guild.me.guild_permissions.manage_roles,
        ]):
            return
        self.debug("✅ Check 1 passed for scrim registration. bot having all the permsissions.")

        if discord.utils.get(message.author.roles, name=self.TAG_IGNORE_ROLE):
            return  # Ignore messages from users with the scrim-ignore-tag role

        _scrim = ScrimModel.find_by_reg_channel(message.channel.id)

        #  if no scrim is found or not active, return
        if not _scrim or not _scrim.status:
            return
        
        self.debug(f"✅ Check 1.1 passed for scrim registration. Scrim found: {_scrim.name} with status: {_scrim.status}")

        

        #  Check if the member is already registered for the scrim (having idp role)
        if not _scrim.multi_register and message.author.id in _scrim.teams:
            await message.delete(delay=1)
            await message.channel.send( f"**{message.author.mention}**: You are already registered. Please wait for the next one.",  delete_after=10 )
            await self.log(message.guild, f"{message.author.mention} tried to register a team but is already registered.", self.bot.color.red)
            return
        
        self.debug("✅ Check 1.6 passed for scrim registration. Member is not already registered.")

        available_slots = _scrim.total_slots - (len(_scrim.reserved) + len(_scrim.teams))
        confirm_role = message.guild.get_role(_scrim.idp_role)
        self.debug(f"✅ Check 2 passed for scrim registration. Available slots: {available_slots}, IDP Role: {confirm_role}")

        #  check if there is any available slot for registration
        if available_slots <= 0:
            await message.channel.send( f"**{message.author.mention}**: All slots are full for this scrim. Please wait for the next one.", delete_after=10 )
            
            #  log action info
            await self.log(message.guild, f"All slots are full for scrim <#{_scrim.reg_channel}>. {message.author.mention} tried to register a team.", self.bot.color.red)
            return
        
        self.debug("✅ Check 3 passed for scrim registration.")

        # check if idp role exists or not, if  not, then close the scrim and inform the scrim mod role if exists
        if not confirm_role:
            await self.log(message.guild, self.DEFAULT_NO_IDP_ROLE, color=self.bot.color.red)
            return

        #  check if the idp role is higher than the bot's top role
        if confirm_role.position >= message.guild.me.top_role.position:
            await message.channel.send(
                f"**{message.author.mention}**: I cannot add the IDP role `{confirm_role.name}` to you because it is higher than my top role. Please contact a server admin to resolve this issue.",
                delete_after=10
            )
            await self.log(message.guild, f"{message.author.mention} tried to register a team but I cannot add the IDP role `{confirm_role.name}` because it is higher than my top role.", color=self.bot.color.red)
            return

        #  Check if the team name is valid
        _team_name = self.bot.helper.parse_team_name(message, _scrim.team_compulsion)
        if not _team_name:
            await message.channel.send( f"**{message.author.mention}**: You must provide a team name. something like `TEAM NAME : XPERIENCED`", delete_after=10 )
            return
        

        #  check if the required mentions are met
        if len(message.mentions) < _scrim.mentions:
            await message.channel.send( f"**{message.author.mention}**: You must mention at least {_scrim.mentions} members to register a team.", delete_after=10 )
            await message.delete()
            await self.log(message.guild, f"{message.author.mention} tried to register a team but did not mention enough members. Required: {_scrim.mentions}, Mentioned: {len(message.mentions)}", color=self.bot.color.red)
            return

        #  checking for duplicate tag invalidation if duplicate tag is enabled
        if not _scrim.duplicate_tag: #if duplicate tag is not allowed
            is_duplicate_tag = await self.bot.helper.duplicate_tag(confirm_role, message)
                
            if is_duplicate_tag:
                await message.delete(delay=1)
                await message.channel.send(
                    embed=discord.Embed(
                        title="Duplicate Tag Detected",
                        description=f"{is_duplicate_tag.mention} you've mentioned is registered to a different [team]({is_duplicate_tag.message.jump_url}). Please check your mentions and try again.", color=self.bot.color.red
                    ), delete_after=10
                )
                await self.log(message.guild, f"{message.author.mention} tried to register a team with a duplicate tag: {is_duplicate_tag.mention}.", color=self.bot.color.red)
                return
            
        self.debug("✅ Check 4 passed for scrim registration. Team name and mentions are valid.")
        await message.add_reaction(self.bot.emoji.tick)
        await message.author.add_roles(confirm_role, reason="Scrim registration")
        self.debug("✅ Check 5 passed for scrim registration. IDP role added to the author.")

        #  add the team to the scrim
        _scrim.add_team(captain=message.author.id, name=_team_name)
        await _scrim.save()
        self.debug("✅ Check 6 passed for scrim registration. Team added to the scrim.")

        team_count = len(_scrim.teams) + len(_scrim.reserved)

        if team_count >= _scrim.total_slots:
            self.bot.dispatch("scrim_close_time_hit", _scrim)

        await self.log(message.guild, f"{message.author.mention} has registered for scrim {_scrim.name}.", color=self.bot.color.green)



    @commands.Cog.listener()
    async def on_scrim_close_time_hit(self, scrim:ScrimModel):
        """Listener for when a scrim end time is hit."""

        scrim.close_time += self.scrim_interval
        self.debug(f"Scrim close time hit for {scrim.name} in {scrim.guild_id} at {self.time.now()}")

        scrim.status = False
        await scrim.save()

        _channel = self.bot.get_channel(scrim.reg_channel)
        team_count = len(scrim.teams) + len(scrim.reserved)

        await self.log(_channel.guild, f"Scrim {_channel.mention} has ended. Team registered : {team_count}.", color=self.bot.color.green)
        self.debug(f"Setting up scrim group for {scrim.name} in {_channel.guild.name}.")
        await self.setup_group(scrim)
        self.debug(f"Scrim group setup completed for {scrim.name} in {_channel.guild.name}. locking registration channel.")
        await self.bot.helper.lock_channel(_channel)


    @functools.lru_cache(maxsize=60)
    def current_scrims(self, is_open:bool,  time:str):
        _time=self.time.now().timestamp()

        _resolved_scrims.clear()
        _resolved_scrims[time] = True

        if is_open:
            return ScrimModel.find(
                open_time={"$lte": int(_time)},
                status=False
            )

        return ScrimModel.find(
            close_time={"$lte": int(_time)},
            status=True
        )


    @tasks.loop(seconds=2)
    async def monitor_scrims(self):
        time = self.time.now().strftime("%H%M")

        if time in _resolved_scrims:
            return

        scrims_by_open_time = self.current_scrims(is_open=True, time=time)
        scrims_by_close_time = self.current_scrims(is_open=False, time=time)

        if len(scrims_by_open_time) > 0:
            for scrim in scrims_by_open_time:
                scrim.status = True
                self.bot.dispatch("scrim_open_time_hit", scrim)

        if len(scrims_by_close_time) > 0:
            for scrim in scrims_by_close_time:
                scrim.status = False
                self.bot.dispatch("scrim_close_time_hit", scrim)


    @monitor_scrims.before_loop
    async def before_monitor_scrims(self):
        """Wait for the bot to be ready before starting the monitor loop."""
        await self.bot.wait_until_ready()



    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel:discord.abc.GuildChannel):
        """Listener for when a scrim registration channel is deleted."""
        if not isinstance(channel, discord.TextChannel):
            return

        _scrim = ScrimModel.find_by_reg_channel(channel.id)
        if not _scrim:
            return

        #  delete the scrim from the database
        await _scrim.delete()
        await self.log(
            channel.guild,
            f"Scrim `{_scrim.name}` has been deleted as its registration channel <#{channel.id}> was deleted.",
            self.bot.color.red
        )




    @set_app.command(name="manager", description="Set the manager for the tournament")
    @commands.guild_only()
    @checks.scrim_mod()
    @app.describe(reg_channel="The channel where the scrim is registered")
    async def set_manager(self, ctx:discord.Interaction, reg_channel:discord.TextChannel):
        await ctx.response.defer(ephemeral=True)

        scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not scrim:
            return await ctx.followup.send(embed=discord.Embed(description=self.DEFAULT_NO_SCRIM_MSG, color=self.bot.color.red))
        
        manage_channel = await reg_channel.category.create_text_channel(name="manage-slot")
        emb = discord.Embed(
            title=reg_channel.category.name,
            description=f"{self.bot.emoji.arow} **Cancel Slot** : To Cancel Your Slot\n{self.bot.emoji.arow} **My Slot** : To Get Details Of Your Slot\n{self.bot.emoji.arow} **Team Name** : To Change Your Team Name\n{self.bot.emoji.arow} **Transfer Slot** : To Transfer Your Slot To Another User",
            color=self.bot.color.cyan
        )
        buttons = [
            discord.ui.Button(label='Cancel Slot', style=discord.ButtonStyle.red, custom_id=f"{scrim.reg_channel}-{ctx.guild.id}-scrim-cancel-slot"),
            discord.ui.Button(label='My Slot', style=discord.ButtonStyle.blurple, custom_id=f"{scrim.reg_channel}-{ctx.guild.id}-scrim-my-slot"),
            discord.ui.Button(label='Team Name', style=discord.ButtonStyle.green, custom_id=f"{scrim.reg_channel}-{ctx.guild.id}-scrim-team-name"),
            discord.ui.Button(label="Transfer Slot", style=discord.ButtonStyle.grey, custom_id=f"{scrim.reg_channel}-{ctx.guild.id}-scrim-transfer-slot"),
        ]

        view = discord.ui.View()
        for i in buttons:
            view.add_item(i)

        await manage_channel.send(embed=emb, view=view)
        await self.bot.helper.lock_channel(channel=manage_channel)

        await ctx.followup.send(f"{self.bot.emoji.tick} | {manage_channel.mention} created")




    async def handle_my_slot_callback(self, interaction:discord.Interaction, scrim:ScrimModel, teams:list[Team]):
            if not teams:
                return await interaction.response.send_message(
                    embed=Embed(
                        description="You are not registered for this scrim.", 
                        color=self.bot.color.red
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
                placeholder="Select your team...",
                options=options
            )

            async def select_callback(select_interaction:discord.Interaction):
                selected_slot = int(select.values[0])
                team = teams[selected_slot]

                embed = Embed(
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
        


    async def handle_teamname_change_callback(self, interaction:discord.Interaction, scrim:ScrimModel, teams:list[Team]):
            if not teams:
                return await interaction.response.send_message(embed=Embed(description="You are not registered for this scrim.", color=self.bot.color.red), ephemeral=True)

            options = [
                discord.SelectOption(
                    label=f"{slot}) TEAM {team.name.upper()}",
                    value=str(slot-1)
                ) for slot, team in enumerate(teams, start=1)
            ]

            # Create a select menu for the user to choose which slot to change the team name
            select = discord.ui.Select(
                placeholder="Select your team...",
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
                        return await modal_interaction.response.send_message(embed=Embed(description="Team name cannot be empty.", color=self.bot.color.red), ephemeral=True)

                    try:
                        team.name = new_team_name
                        await scrim.save()

                        await modal_interaction.response.send_message(embed=Embed(description=f"Your team name has been changed to `{new_team_name}`.", color=self.bot.color.green), ephemeral=True)

                    except Exception as e:
                        await modal_interaction.response.send_message(embed=Embed(description=str(e), color=self.bot.color.red), ephemeral=True)

                modal.on_submit = modal_callback
                await select_interaction.response.send_modal(modal)

            select.callback = select_callback
            view = discord.ui.View()
            view.add_item(select)
            return await interaction.response.send_message(view=view, ephemeral=True)
    

    async def handle_transfer_slot_callback(self, interaction:discord.Interaction, scrim:ScrimModel, teams:list[Team]):
        """Handle the transfer slot callback for scrim interactions."""
        if not teams:
            return await interaction.response.send_message(embed=Embed(description="You are not registered for this scrim.", color=self.bot.color.red), ephemeral=True)

        options = [
            discord.SelectOption(
                label=f"{slot}) TEAM {team.name.upper()}",
                value=str(slot-1)
            ) for slot, team in enumerate(teams, start=1)
        ]

        # Create a select menu for the user to choose which slot to transfer
        select = discord.ui.Select(
            placeholder="Select your team...",
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
                    return await member_interaction.response.send_message(embed=Embed(description="Invalid member.", color=self.bot.color.red), ephemeral=True)

                try:
                    team.captain = new_member.id
                    await scrim.save()

                    await member_interaction.response.send_message(embed=Embed(description=f"Your slot has been transferred to {new_member.mention}.", color=self.bot.color.green), ephemeral=True)

                except Exception as e:
                    await member_interaction.response.send_message(embed=Embed(description=str(e), color=self.bot.color.red), ephemeral=True)

            member_input.callback = member_selection_callback
            await select_interaction.response.send_message(
                embed=Embed(
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



    async def handle_scrim_interaction(self, interaction:discord.Interaction):
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

        scrim = ScrimModel.find_by_reg_channel(reg_channel.id)

        if not scrim:
            return await interaction.response.send_message(embed=Embed(description=self.DEFAULT_NO_SCRIM_MSG, color=self.bot.color.red), ephemeral=True)
            
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
            await self.handle_my_slot_callback(interaction=interaction, scrim=scrim, teams=teams)


        if custom_id.endswith("scrim-team-name"):
            await self.handle_teamname_change_callback(interaction= interaction, scrim=scrim, teams=teams)


        if custom_id.endswith("scrim-transfer-slot"):
            await self.handle_transfer_slot_callback(interaction=interaction, scrim=scrim, teams=teams)


    @commands.Cog.listener()
    async def on_interaction(self, interaction:discord.Interaction):
        """Listener for when an interaction is received."""
        if not interaction.guild:
            return
        custom_id = interaction.data.get("custom_id", "")
        

        if f"-{interaction.guild.id}-scrim" in custom_id:
                await self.handle_scrim_interaction(interaction)

