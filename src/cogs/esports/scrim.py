"""
A module for managing scrims in a Discord server.
    :author: hunter87
    :copyright: (c) 2022-present hunter87.dev@gmail.com
    :license: GPL-3, see LICENSE for more details.
"""

import discord
from enum import Enum
from typing import TYPE_CHECKING
from ext import EmbedBuilder, constants, checks
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from models.scrim import ScrimModel, Team
from core.abstract import GroupCog
from events.esports import scrim as scrim_events
from discord import Embed, TextChannel,  Interaction,   app_commands as app


if TYPE_CHECKING:
    from core.bot import Spruce    

_resolved_scrims: dict[str, bool] = {}

class ScrimCog(GroupCog, name="scrim", group_name="scrim", command_attrs={"help":"Manage scrims for the server."}):
    """Cog for managing scrims in the server."""

    CUSTOM_ID_SLOT_REFRESH = "scrim-slot-refresh"
    CUSTOM_ID_MY_SLOT = "scrim-my-slot"
    CUSTOM_ID_TEAM_NAME = "scrim-team-name"
    CUSTOM_ID_CANCEL_SLOT = "scrim-cancel-slot"
    CUSTOM_ID_TRANSFER_SLOT = "scrim-transfer-slot"

    def __init__(self, bot:"Spruce") -> None:
        self.bot = bot
        self.SCRIM_LIMIT = 4
        self.time = bot.time
        self.monitor_scrims.start()
        self.DEFAULT_START_TIME = "10:00 AM"
        self.DEFAULT_END_TIME = "4:00 PM"
        self.TAG_IGNORE_ROLE = "scrim-tag-ignore"
        self.SCRIM_MOD_ROLE = "scrim-mod"
        self.scrim_interval = 86400 # seconds in 24 hours
        self.DEFAULT_TIMEZONE = constants.TimeZone.Asia_Kolkata.value
        self.SELECT_TEAM_PLACEHOLDER = "Select your team..."
        self.YOU_ARE_NOT_REGISTERED = "Seems like you are not registered for this scrim."
        self.DEFAULT_END_MESSAGE = "Scrim has ended! Thank you for participating."
        self.DEFAULT_NO_SCRIM_MSG = "No scrim found for the provided registration channel."
        self.HIGHER_ROLE_POSITION = "{role.mention} has a higher role position than me. Please move it below my role and try again."
        self.DEFAULT_NO_IDP_ROLE = "No IDP role found for the scrim. Please set it using `/scrim set idp_role` command."



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
    

    async def setup_group(self, scrim:ScrimModel, slot_per_group:int = None, end_time:int=None, message:discord.Message = None):
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
            discord.ui.Button(emoji=self.bot.emoji.refresh, style=discord.ButtonStyle.secondary, custom_id=f"{scrim.reg_channel}-{scrim.guild_id}-scrim-slot-refresh"),
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


    @staticmethod
    def scrim_info_embed(scrim:ScrimModel):
        embed = Embed(
            title=f"{scrim.name}",
            color=discord.Color.green()
        )
        if scrim.status is True:
            status = "Open"
        elif scrim.status is False:
            status = "Closed"
        else:
            status = "Disabled"
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
        embed.add_field(name="Ping Role", value=f"<@&{scrim.ping_role}>" if scrim.ping_role else "`not-set`")
        embed.add_field(name="Open Role", value=f"<@&{scrim.open_role}>" if scrim.open_role else "`not-set`")
        embed.add_field(name="Slots Left", value=f"`{available_slots}`/`{scrim.total_slots}`")
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

        _existing_scrims = await ScrimModel.find(guild_id=ctx.guild.id)
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
            if await ScrimModel.find_by_reg_channel(reg_channel.id):
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

        _scrim = await ScrimModel.find_by_reg_channel(reg_channel.id)

        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)

        next_open_timestamp = self.time.parse_datetime(
            time_str=_scrim.open_time_str(), 
            tz=_scrim.time_zone).timestamp()

        next_close_timestamp = self.time.parse_datetime(
            time_str=_scrim.close_time_str(), 
            tz=_scrim.time_zone).timestamp()

        _scrim.open_time = int(next_open_timestamp)
        _scrim.close_time = int(next_close_timestamp)

        _status = False
        if status == self.ScrimStatus.OPEN:
            _status = True

        elif status == self.ScrimStatus.CLOSED:
            _status = False

        elif status == self.ScrimStatus.DISABLED:
            _status = None

        _scrim.status = _status
        await _scrim.save()

        await ctx.followup.send(embed=EmbedBuilder.success(f"Scrim {reg_channel.mention} status updated to: {status.value}"), ephemeral=True)


    @app.command(name="start", description="Start a scrim by its ID.")
    @app.guild_only()
    @checks.scrim_mod(interaction=True)
    @app.describe(  reg_channel="ID of the scrim to start (required)")
    async def start_scrim(self, ctx:discord.Interaction, reg_channel:discord.TextChannel):
        """Start a scrim by its ID."""
        await ctx.response.defer(ephemeral=True)
        _scrim = await ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)


        if _scrim.status == True:
            return await ctx.followup.send(embed=discord.Embed(description=f"Scrim {reg_channel.mention} is already open.", color=self.bot.color.red), ephemeral=True)
        

        self.bot.dispatch("scrim_open_time_hit", scrim=_scrim)
        await ctx.followup.send(embed=discord.Embed(description=f"Scrim {reg_channel.mention} has been started.", color=self.bot.color.green), ephemeral=True)



    @app.command(name="close", description="End a scrim by its ID.")
    @app.guild_only()
    @checks.scrim_mod(interaction=True)
    @app.describe(reg_channel="ID of the scrim to end (required)")
    async def end_scrim(self, ctx:discord.Interaction, reg_channel:discord.TextChannel):
        await ctx.response.defer(ephemeral=True)

        scrim = await ScrimModel.find_by_reg_channel(reg_channel.id)
        if not scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)
        
        if scrim.status == False:
            return await ctx.followup.send(embed=discord.Embed(description=f"Scrim {reg_channel.mention} is already closed.", color=self.bot.color.red), ephemeral=True)
        
        if scrim.status is None:
            return await ctx.followup.send(embed=discord.Embed(description=f"Scrim {reg_channel.mention} is disabled.", color=self.bot.color.red), ephemeral=True)

        # End the scrim
        self.bot.dispatch("scrim_close_time_hit", scrim=scrim)
        await ctx.followup.send(embed=discord.Embed(description=f"Scrim {reg_channel.mention} has been ended.", color=self.bot.color.red), ephemeral=True)



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

        _scrim = await ScrimModel.find_by_reg_channel(reg_channel.id)

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
        _scrim = await ScrimModel.find_by_reg_channel(reg_channel.id)
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

        scrim = await ScrimModel.find_by_reg_channel(reg_channel.id)
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

        _scrim = await ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)

        #  delete the scrim from the database
        await _scrim.delete()

        await ctx.followup.send(embed=discord.Embed(description=f"Scrim `{_scrim.name}` has been deleted successfully.", color=self.bot.color.red), ephemeral=True)


    @app.command(name="list", description="List all scrims in the server.")
    @app.guild_only()
    @checks.scrim_mod(interaction=True)
    async def list_scrims(self, ctx:discord.Interaction):
        """List all scrims in the server."""
        await ctx.response.defer()

        scrims = await ScrimModel.find(guild_id=ctx.guild.id)
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



    @app.command(name="ignore_me", description="Ignore the scrim mod commands in this server.")
    @app.guild_only()
    @checks.scrim_mod(interaction=True)
    async def ignore_me(self, ctx:discord.Interaction):
        """Ignore the scrim mod commands in this server."""
        await ctx.response.defer(ephemeral=True)

        ignore_role = discord.utils.get(ctx.guild.roles, name=self.bot.config.TAG_IGNORE_ROLE)
        if not ignore_role:
            ignore_role = await ctx.guild.create_role(name=self.bot.config.TAG_IGNORE_ROLE, mentionable=True)

        if ignore_role.position >= ctx.guild.me.top_role.position:
            await ctx.followup.send(self.HIGHER_ROLE_POSITION.format(role=ignore_role), ephemeral=True)
            return

        if ignore_role in ctx.user.roles:
            return await ctx.followup.send(
                embed=Embed(
                    description=f"You already have {ignore_role.mention} added to you.",
                    color=self.bot.color.red
                ),
                ephemeral=True
            )
        
        await ctx.user.add_roles(ignore_role)
        await ctx.followup.send(
            embed=Embed(
                description=f"Added {ignore_role.mention} to you.\n Now your messages will be ignored in registration channels.", 
                color=self.bot.color.cyan
            ),
            ephemeral=True
        )


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


    @set_app.command(name="multi_register", description="Set or update the multi-register option for a scrim.")
    @app.guild_only()
    @app.describe(
        reg_channel="Registration channel of the scrim to set multi-register option (required)",
        allow="Enable or disable multi-register option (required)",
    )
    @checks.scrim_mod(interaction=True)
    async def set_multi_register(self, ctx:discord.Interaction, reg_channel:discord.TextChannel, allow:bool):
        await ctx.response.defer(ephemeral=True)
        """Set or update the multi-register option for a scrim."""
        _scrim = await ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)
        
        # Update the multi-register option in the scrim
        _scrim.multi_register = allow
        await _scrim.save()
        status = "enabled" if allow else "disabled"
        await ctx.followup.send(
            embed=Embed(
                description=f"Multi-register option for scrim `{_scrim.name}` has been {status}.",
                color=self.bot.color.green
            ),
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

        scrim  = await ScrimModel.find_by_reg_channel(reg_channel.id)
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
        await idp_channel.set_permissions(
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


    @set_app.command(name="duplicate_tag", description="Enable or disable duplicate tag filter for a scrim.")
    @app.guild_only()
    @app.describe(
        reg_channel="Registration channel of the scrim to set duplicate tag filter (required)",
        filter="Enable or disable duplicate tag filter (required)",
    )
    @checks.scrim_mod(interaction=True)
    async def set_duplicate_tag(self, ctx:discord.Interaction, reg_channel:discord.TextChannel, filter:DuplicateTagCheck):
        """Enable or disable duplicate tag filter for a scrim."""
        await ctx.response.defer(ephemeral=True)

        _scrim = await ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)

        # Update the duplicate tag filter in the scrim
        _scrim.duplicate_tag = bool(filter.value)
        await _scrim.save()

        await ctx.followup.send(f"Duplicate tag filter for scrim `{_scrim.name}` has been {'Disabled' if _scrim.duplicate_tag else 'Enabled'}.", ephemeral=True)


    class TeamCompulsionCheck(Enum):
        ENABLE = 1
        DISABLE = 0


    @set_app.command(name="team_compulsion", description="Toggle Team Compulsion filter")
    @app.guild_only()
    @checks.scrim_mod(interaction=True)
    @app.describe(
        reg_channel="Registration channel of the scrim to set team compulsion filter (required)",
        filter="Enable or disable team compulsion filter (required)",
    )
    @checks.scrim_mod(interaction=True)
    async def set_team_compulsion(self, ctx:discord.Interaction, reg_channel:discord.TextChannel, filter:TeamCompulsionCheck):
        """Enable or disable team compulsion filter for a scrim."""
        await ctx.response.defer(ephemeral=True)

        _scrim = await ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)

        # Update the team compulsion filter in the scrim
        _scrim.team_compulsion = bool(filter.value)
        await _scrim.save()

        await ctx.followup.send(f"Team compulsion filter for scrim `{_scrim.name}` has been {'Disabled' if _scrim.team_compulsion else 'Enabled'}.", ephemeral=True)



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

        _scrim = await ScrimModel.find_by_reg_channel(reg_channel.id)
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

        _scrim = await ScrimModel.find_by_reg_channel(reg_channel.id)
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

        _scrim = await ScrimModel.find_by_reg_channel(reg_channel.id)
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

        _scrim = await ScrimModel.find_by_reg_channel(reg_channel.id)
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

        _scrim = await ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)

        parsed_open_time = int(self.time.parse_datetime(time_str=open_time, tz=_scrim.time_zone).timestamp())
        
        #  update the open time in the scrim
        _scrim.open_time = parsed_open_time
        await _scrim.save()
        await ctx.followup.send(f"Open time for scrim <#{reg_channel.id}> has been set to <t:{parsed_open_time}:t>.", ephemeral=True)


    @set_app.command(name="open_role", description="Set or update the open role for a scrim.")
    @app.guild_only()
    @checks.scrim_mod(interaction=True)
    @app.describe(
        reg_channel="Registration channel of the scrim to update open role (required)",
        open_role="Open role for the scrim (required)",
    )
    async def set_open_role(self, ctx:discord.Interaction, reg_channel:discord.TextChannel, open_role:discord.Role):
        """Set or update the open role for a scrim."""
        await ctx.response.defer(ephemeral=True)

        _scrim = await ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)

        #  update the open role in the scrim
        _scrim.open_role = open_role.id
        await _scrim.save()

        await ctx.followup.send(embed=EmbedBuilder.success(f"Open role for scrim <#{reg_channel.id}> has been set to {open_role}."), ephemeral=True)



    @set_app.command(name="close_time", description="Set or update the close time for a scrim.")
    @app.guild_only()
    @checks.scrim_mod(interaction=True)
    @app.describe(reg_channel="Registration channel of the scrim to update close time (required)",
                  close_time="Close time for the scrim (required)")
    async def set_close_time(self, ctx:discord.Interaction, reg_channel:discord.TextChannel, close_time:str):
        """Set or update the close time for a scrim."""
        await ctx.response.defer(ephemeral=True)

        _scrim = await ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)

        try:
            parsed_close_time = int(self.time.parse_datetime(time_str=close_time, tz=_scrim.time_zone).timestamp())
            
        except ValueError:
            return await ctx.followup.send("Invalid close time format. Please use HH:MM AM/PM format.", ephemeral=True)

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

        _scrim = await ScrimModel.find_by_reg_channel(reg_channel.id)
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

        _scrim = await ScrimModel.find_by_reg_channel(reg_channel.id)
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

        _scrim = await ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)

        #  update the slot channel in the scrim
        _scrim.slot_channel = slot_channel.id
        await _scrim.save()

        await ctx.followup.send(f"Slot channel for scrim `{_scrim.name}` has been set to <#{slot_channel.id}>.", ephemeral=True)


    @set_app.command(name="days", description="Set or update days for scrim to operate")
    @app.guild_only()
    @checks.scrim_mod(interaction=True)
    @app.describe(reg_channel="The registration channel of the scrim to update")
    async def set_days(self, ctx:discord.Interaction, reg_channel:discord.TextChannel):
        await ctx.response.defer(ephemeral=True)

        _scrim = await ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)

        select = discord.ui.Select(
            placeholder="Select the days for the scrim to operate",
            min_values=1,
            max_values=7,
            options=[
                discord.SelectOption(label=day, value=day.lower(), default=(day.lower() in _scrim.open_days))
                for day in ["mo", "tu", "we", "th", "fr", "sa", "su"]
            ]
        )

        async def update_days(callback_interaction: discord.Interaction):
            await callback_interaction.response.defer(ephemeral=True)
            selected_days = select.values
            if not selected_days:
                return await callback_interaction.followup.send("Please select at least one day.", ephemeral=True)

            _scrim.open_days = selected_days
            await _scrim.save()
            await callback_interaction.followup.send(f"Updated days for scrim `{_scrim.name}` to: {', '.join(selected_days)}", ephemeral=True)

        select.callback = update_days


        view = discord.ui.View()
        view.add_item(select)

        await ctx.followup.send(
            embed=discord.Embed(
                title=f"Select Days for Scrim: {_scrim.name}",
                description="Select the days for the scrim to operate. You can select multiple days.",
                color=self.bot.color.random()
            ),
            view=view,
            ephemeral=True
        )


    @set_app.command(name="manager", description="Set the manager for the tournament")
    @commands.guild_only()
    @checks.scrim_mod()
    @app.describe(reg_channel="The channel where the scrim is registered")
    async def set_manager(self, ctx:discord.Interaction, reg_channel:discord.TextChannel):
        await ctx.response.defer(ephemeral=True)

        scrim = await ScrimModel.find_by_reg_channel(reg_channel.id)
        if not scrim:
            return await ctx.followup.send(embed=discord.Embed(description=self.DEFAULT_NO_SCRIM_MSG, color=self.bot.color.red))
        
        manage_channel = await reg_channel.category.create_text_channel(name="manage-slot")
        emb = discord.Embed(
            title=reg_channel.category.name,
            description=f"{self.bot.emoji.arow} **Cancel Slot** : To Cancel Your Slot\n{self.bot.emoji.arow} **My Slot** : To Get Details Of Your Slot\n{self.bot.emoji.arow} **Team Name** : To Change Your Team Name\n{self.bot.emoji.arow} **Transfer Slot** : To Transfer Your Slot To Another User",
            color=self.bot.base_color
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


    @setup_app.command(name="group", description="setup scrim group.")
    @app.guild_only()
    @app.describe(reg_channel="Registration channel of the scrim to setup group (required)",)
    @checks.scrim_mod(interaction=True)
    async def scrim_group_setup(self, ctx:Interaction, reg_channel:TextChannel):
        """Setup the scrim group with the provided registration channel."""
        await ctx.response.defer(ephemeral=True)
         # remove this before release
        _scrim = await ScrimModel.find_by_reg_channel(reg_channel.id)

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
        _scrim =  await ScrimModel.find_by_reg_channel(reg_channel.id)
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


    @add_app.command(name="reserved_slot", description="View or update the reserved slots for a scrim.")
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
        

        _scrim = await ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)
        
        if(len(_scrim.reserved) >= _scrim.total_slots):
            return await ctx.followup.send("All slots are already reserved for this scrim.", ephemeral=True)

        if _scrim.available_slots() <= 0:
            return await ctx.followup.send(
                embed=EmbedBuilder.warning(
                    message="No available slots for this scrim. try again after finishing it. or remove a slot to get one"
                    ), ephemeral=True
            )

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

        scrim = await ScrimModel.find_by_reg_channel(reg_channel.id)
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

        _scrim = await ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)

        #  find the reserved slot by captain id
        if captain.id not in _scrim.reserved:
            return await ctx.followup.send(f"No reserved slot found for captain {captain.mention} in this scrim.", ephemeral=True)
        
        #  remove the reserved slot
        _scrim.reserved.remove(captain.id)
        await _scrim.save()

        await ctx.followup.send(f"Reserved slot for captain {captain.mention} has been removed successfully.", ephemeral=True)


    @app.command(name="clear", description="Clear teams, messages for a specific scrim")
    @app.guild_only()
    @checks.scrim_mod(interaction=True)
    @app.checks.cooldown(1, 30, key=lambda i: i.guild_id)
    @app.describe(reg_channel="Registration channel of the scrim to clear (required)")
    async def clear_scrim(self, ctx:discord.Interaction, reg_channel:discord.TextChannel):
        await ctx.response.defer(ephemeral=True)
        _scrim = await ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send(self.DEFAULT_NO_SCRIM_MSG, ephemeral=True)

        _scrim.clear_teams()
        _reg_channel = self.bot.get_channel(_scrim.reg_channel)
        if not _reg_channel:
            return

        idp_role = await _reg_channel.guild.fetch_role(_scrim.idp_role)
        if not idp_role:
            return
        
        old_players = [await self.get_member(idp_role.guild, _id) for _id in _scrim.captain_ids()]

        for member in old_players:
            await member.remove_roles(idp_role)

        await _reg_channel.purge(reason="Clearing old scrim participants")
        _scrim.cleared = True
        _scrim.clear_teams()
        await _scrim.save()
        await ctx.followup.send(EmbedBuilder.success(f"Scrim <#{_scrim.reg_channel}> has been cleaned up."), ephemeral=True)



    async def current_scrims(self, is_open:bool,  time:str):
        _time=self.time.now().timestamp()

        _resolved_scrims.clear()
        _resolved_scrims[time] = True

        if is_open:
            return await ScrimModel.find(
                open_time={"$lte": int(_time)},
                status=False
            )

        return await ScrimModel.find(
            close_time={"$lte": int(_time)},
            status=True
        )


    async def schedule_scrim_cleaner(self):
        _time = int(self.time.now().timestamp())
        _count = 0
        for _scrim in ScrimModel._cache.values():
            if all([
                _scrim.status is False,
                not _scrim.cleared,
                _scrim.open_time < _time + 3600
            ]):
                self.bot.dispatch("scrim_clean_time_hit", _scrim)

            if _count % 50 == 0 : 
                await self.bot.sleep(0.3)

            _count += 1



    @tasks.loop(seconds=2)
    async def monitor_scrims(self):
        _debug = False
        time = self.time.now().strftime("%H%M")

        if time in _resolved_scrims:
            return

        scrims_by_open_time = await  self.current_scrims(is_open=True, time=time)
        scrims_by_close_time = await self.current_scrims(is_open=False, time=time)


        if len(scrims_by_open_time) > 0:
            for scrim in scrims_by_open_time:
                scrim.status = True
                self.bot.debug(f"Scrim {scrim.name} is now open for registration at {time}.", is_debug=_debug)
                self.bot.dispatch("scrim_open_time_hit", scrim)

        if len(scrims_by_close_time) > 0:
            for scrim in scrims_by_close_time:
                scrim.status = False
                self.bot.debug(f"Scrim {scrim.name} is now closed for registration at {time}.", is_debug=_debug)
                self.bot.dispatch("scrim_close_time_hit", scrim)


        await self.bot.loop.create_task(self.schedule_scrim_cleaner())


    @monitor_scrims.before_loop
    async def before_monitor_scrims(self):
        """Wait for the bot to be ready before starting the monitor loop."""
        await self.bot.wait_until_ready()



    @commands.Cog.listener()
    async def on_ready(self):
        await ScrimModel.load_all()

    @commands.Cog.listener()
    async def on_scrim_open_time_hit(self, scrim:ScrimModel):
        """Listener for when a scrim open time is hit."""
        await scrim_events.handle_scrim_start(self, scrim)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await scrim_events.handle_scrim_registration(self, message)

    @commands.Cog.listener()
    async def on_scrim_close_time_hit(self, scrim:ScrimModel):
        await scrim_events.handle_scrim_end(self, scrim)

    @commands.Cog.listener()
    async def on_scrim_clean_time_hit(self, scrim: ScrimModel):
        await scrim_events.handle_scrim_clear(self, scrim)


    @commands.Cog.listener()
    async def on_interaction(self, interaction:discord.Interaction):
        """Listener for when an interaction is received."""
        if not interaction.guild:
            return
        custom_id = interaction.data.get("custom_id", "")
        

        if f"-{interaction.guild.id}-scrim" in custom_id:
                await scrim_events.handle_scrim_slot_manager_interaction(self, interaction)


    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel:discord.abc.GuildChannel):
        """Listener for when a scrim registration channel is deleted."""
        if not isinstance(channel, discord.TextChannel):
            return

        _scrim = await ScrimModel.find_by_reg_channel(channel.id)
        if not _scrim:
            return

        #  delete the scrim from the database
        await _scrim.delete()
        await self.log(
            channel.guild,
            f"Scrim `{_scrim.name}` has been deleted as its registration channel <#{channel.id}> was deleted.",
            self.bot.color.red
        )