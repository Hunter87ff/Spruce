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
from ext import permissions, constants, color, emoji
from discord.ext import commands, tasks
from ext.models.scrim import ScrimModel, ReservedSlot
from discord import Embed, TextChannel,  Interaction,   app_commands as app


if TYPE_CHECKING:
    from modules.bot import Spruce    


_resolved_scrims: dict[str, bool] = {}

class ScrimCog(commands.GroupCog, name="scrim", group_name="scrim", command_attrs={"help": "Manage scrims for the server."}):
    """Currently in development mode!!"""
    def __init__(self, bot:"Spruce") -> None:
        self.bot = bot
        self.time = bot.time
        self.monitor_scrims.start()
        self.DEFAULT_START_TIME = "10:00 AM"
        self.DEFAULT_END_TIME = "4:00 PM"
        self.DEFAULT_TIMEZONE = constants.TimeZone.Asia_Kolkata.value
        self.DEFAULT_END_MESSAGE = "Scrim has ended! Thank you for participating."
        self.TAG_IGNORE_ROLE = "scrim-ignore-tag"
        self.scrim_interval = 86400 # seconds in 24 hours


    set_app = app.Group(name="set",  description="Set scrim configurations.")
    setup_app = app.Group(name="setup", description="Setup scrim configurations.")
    add_app = app.Group(name="add", description="Add scrim configurations.")
    remove_app = app.Group(name="remove", description="Remove scrim configurations.")


    def log_embed(self, message:str, color=color.green):
        embed = Embed(title="Scrim Log", description=message, color=color)
        return embed
    

    def is_moderator(self, ctx:Interaction) -> bool:
        """Check if the user is a moderator."""
        return any([
            permissions.is_dev(ctx),
            ctx.user.guild_permissions.manage_guild,
            ctx.user.guild_permissions.administrator,
            discord.utils.get(ctx.guild.roles, name="scrim-mod")
        ])
    

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
        teams:list[ReservedSlot] = []

        if scrim.reserved:
            teams.extend([ReservedSlot(captain_id, team_name) for captain_id, team_name in scrim.reserved.items()])

        async for message in slot_channel.history(limit=scrim.total_slots+10):
            if message.author.id == self.bot.user.id:
                continue
            
            team_name = self.bot.helper.parse_team_name(message)
            if not team_name:
                continue
            
            teams.append(ReservedSlot(team_name=team_name, captain_id=message.author.id))


        def format_slot(number:int, team_name:str):
            """Format the slot number and team name."""
            return f"Slot {number:02d} -> Team {team_name}"
        
        time_taken = int(discord.utils.utcnow().timestamp()) - (scrim.open_time - self.scrim_interval)  # Interval is now configurable
        group_embed = discord.Embed(
            title=f"**{self.bot.emoji.cup} | {scrim.name.upper()} SLOT LIST | {self.bot.emoji.cup}**",
            color=self.bot.color.random()
        )
        group_embed.set_footer(text=f"Registration Took : {self.time.by_seconds(time_taken)}")
        _description = "```" + "\n".join(["Team "+format_slot(i, team.team_name) for i, team in enumerate(teams, start=1)]) + "```"
        group_embed.description = _description

        await reg_channel.send(embed=group_embed)


    @setup_app.command(name="group", description="setup scrim group.")
    @app.guild_only()
    @app.describe(
        reg_channel="Registration channel of the scrim to setup group (required)",
        slot_per_group="Number of slots per group (default: 12)",   
    )
    
    @app.checks.bot_has_permissions(manage_channels=True, send_messages=True, embed_links=True)
    async def scrim_group_setup(self, ctx:Interaction, reg_channel:TextChannel, slot_per_group:app.Range[int, 1, 30] = 12):
        """Setup the scrim group with the provided registration channel."""
        await ctx.response.defer(ephemeral=True)

        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)

        if not _scrim:
            return await ctx.followup.send("No scrim found for the provided registration channel.", ephemeral=True)

        try:
            await self.setup_group(scrim=_scrim, slot_per_group=slot_per_group)
            await ctx.followup.send("Scrim group setup successfully.", ephemeral=True)

        except Exception as e:
            return await ctx.followup.send(f"Error occurred while setting up scrim group: {str(e)}", ephemeral=True)


    @staticmethod
    def scrim_info_embed(scrim:ScrimModel):
        embed = Embed(
            title=f"{scrim.name}",
            color=color.random()
        )
        embed.add_field(name="Start Time", value=f"<t:{scrim.open_time}:t>")
        embed.add_field(name="End Time", value=f"<t:{scrim.close_time}:t>")
        embed.add_field(name="Status", value="`Open`" if scrim.status else "`Closed`")
        embed.add_field(name="Time Zone", value=f"`{scrim.time_zone}`")
        embed.add_field(name="Registration Channel", value=f"<#{scrim.reg_channel}>")
        embed.add_field(name="Slot Channel", value=f"<#{scrim.slot_channel}>")
        embed.add_field(name="Tags", value=f"{scrim.mentions:02d}")
        embed.add_field(name="IDP Role", value=f"<@&{scrim.idp_role}>")
        embed.add_field(name="Ping Role", value=f"<@&{scrim.ping_role}>" if scrim.ping_role else "None")
        embed.add_field(name="Slots", value=f"`{scrim.team_count}/{scrim.total_slots}`")
        embed.add_field(name="Reserved Slots", value=f"`{len(scrim.reserved)}`")
        embed.set_footer(text=f"Scrim ID: {scrim.reg_channel}")
        embed.timestamp = discord.utils.utcnow()
        return embed


    def configure_start_message(self, scrim: ScrimModel):
        return f"""**{self.bot.emoji.tick} | AVAILABLE SLOTS : {scrim.total_slots - (len(scrim.reserved) + scrim.team_count)}
                    {self.bot.emoji.tick} | REQUIRED MENTIONS : {scrim.mentions}
                    {self.bot.emoji.tick} | CLOSE TIME : <t:{int(scrim.close_time)}:t>**""".strip()


    @app.command(name="create", description="Create a scrim for the server.")
    @app.guild_only()
    @app.describe(
        scrim_name="Name of the scrim",
        mentions="Number of mentions required to register a team (default: 4)",
        total_slots="Total number of slots for the scrim (default: 12)",
        open_time="examples: 10am, 10:00, 22:00, 7:00 PM (default: 10:00 AM)",
        close_time="examples: 10am, 10:00, 22:00, 7:00 PM (default: 4:00 PM)",
        timezone="Timezone of the scrim (default: Asia/Kolkata)",
        reg_channel="Registration channel for the scrim (default: create's new channel)",
        slot_channel="Slot channel for the scrim (default: registration channel)",
        ping_role="Role to ping when the scrim starts (optional)",
    )
    @commands.cooldown(1, 15, commands.BucketType.guild)
    @commands.bot_has_guild_permissions(embed_links=True, manage_messages=True, read_message_history=True)
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
        slot_channel: TextChannel | None = None
    ):
        """Create a new scrim
        """

        await ctx.response.defer(ephemeral=True)


        _is_eligible = any([
            permissions.is_dev(ctx),
            ctx.user.guild_permissions.manage_guild,
            ctx.user.guild_permissions.administrator,
            discord.utils.get(ctx.guild.roles, name="scrim-mod")
        ])

        if not _is_eligible:
            await ctx.followup.send("You do not have permission to create a scrim.", ephemeral=True)
            return


        try:
            _parsed_open_time = int(self.time.parse_datetime(time_str=open_time, tz=timezone.value).timestamp())
            _parsed_close_time = int(self.time.parse_datetime(time_str=close_time, tz=timezone.value).timestamp())

        except ValueError as e:
            return await ctx.followup.send(f"{str(e)}. Please use HH:MM AM/PM format.", ephemeral=True)

        if _parsed_open_time is None or _parsed_close_time is None:
            return await ctx.followup.send("Invalid time format. Please use HH:MM AM/PM format.", ephemeral=True)

        _event_prefix = self.bot.helper.get_event_prefix(scrim_name)
        _scrim_category: discord.CategoryChannel
        _registration_channel: TextChannel
        
        # if registration channel is provided, use it, otherwise create a new one
        # 
        if reg_channel:
            _registration_channel = reg_channel
            if _registration_channel.category is not None:
                _scrim_category = _registration_channel.category

        else:
            _scrim_category = await ctx.guild.create_category(name=str(scrim_name))
            _registration_channel = await _scrim_category.create_text_channel(name=f"{_event_prefix}register-here")


        _slot_channel = slot_channel or _registration_channel
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
            _scrim_obj = ScrimModel(
                name=scrim_name,
                mentions=mentions,
                reg_channel=_registration_channel.id,
                slot_channel=_slot_channel.id,
                idp_role=idp_role.id,
                guild_id=ctx.guild.id,
                scrim_name=scrim_name,
                open_time=_parsed_open_time,
                close_time=_parsed_close_time,
                total_slots=total_slots,
                time_zone=timezone.value,
                ping_role=ping_role.id if ping_role else None,
            )
            _scrim_obj.save()

            await ctx.followup.send(embed=self.scrim_info_embed(scrim=_scrim_obj), ephemeral=True)

            await _registration_channel.send(embed=Embed(
                description=f"Scrim will start at {open_time}",
                color=self.bot.color.random()
            ))
            if self.bot.helper.get_scrim_log(ctx.guild):
                await self.bot.helper.get_scrim_log(ctx.guild).send(
                    embed=self.log_embed(f"Scrim created by {ctx.user.mention} in {ctx.guild.name} with name: {scrim_name}")
                )

        except ValueError as e:
            return await ctx.followup.send(f"Unable to create scrim: {str(e)}", ephemeral=True)
        

    @app.command(name="start", description="Start a scrim by its ID.")
    @app.guild_only()
    
    @app.describe(
        reg_channel="ID of the scrim to start (required)",
    )
    async def start_scrim(self, ctx:discord.Interaction, reg_channel:discord.TextChannel):
        """Start a scrim by its ID."""
        await ctx.response.defer(ephemeral=True)
        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send("No scrim found for the provided registration channel.", ephemeral=True)

        # Start the scrim
        _scrim.status = True
        ping_role =  f"<@&{_scrim.ping_role}>" if _scrim.ping_role else ""
        _scrim.save()
        await reg_channel.send(f"The scrim has been started!\n{ping_role}")
        await ctx.followup.send(f"Scrim {reg_channel.mention} has been started.", ephemeral=True)


    @app.command(name="audit", description="Audit a scrim by its ID.")
    @app.guild_only()
    @app.describe(
        reg_channel="Registration channel of the scrim to audit (required)",
    )
    async def audit_scrim(self, ctx:discord.Interaction, reg_channel:discord.TextChannel):
        """Audit a scrim by its registration channel."""
        await ctx.response.defer(ephemeral=True)

        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)

        if not _scrim:
            return await ctx.followup.send("No scrim found for the provided registration channel.", ephemeral=True)
        
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

        missing_perms = []
        if not having_perm:
            if not reg_read_perms:
                missing_perms.append("read_messages")
            if not reg_send_perms:
                missing_perms.append("send_messages")
            if not reg_manage_message_perms:
                missing_perms.append("manage_messages")
            if not reg_add_reactions_perms:
                missing_perms.append("add_reactions")
            if not manage_role_perms:
                missing_perms.append("manage_roles")
            if not manage_channel_perms:
                missing_perms.append("manage_channels")
            if not read_history_perms:
                missing_perms.append("read_message_history")

            return await ctx.followup.send(
                f"Missing permissions to manage the scrim: `{'`, '.join(missing_perms)}. Please update the permissions and try again.",
                ephemeral=True
            )



        await ctx.followup.send(embed=self.scrim_info_embed(scrim=_scrim), ephemeral=True)



    @app.command(name="info", description="Get information about a scrim by its ID.")
    @app.guild_only()
    @app.describe(
        reg_channel="Registration channel of the scrim to get information about (required)",
    )
    async def scrim_info(self, ctx:discord.Interaction, reg_channel:discord.TextChannel):
        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        """Get information about a scrim by its registration channel."""
        await ctx.response.defer(ephemeral=True)
        if not _scrim:
            return await ctx.followup.send("No scrim found for the provided registration channel.", ephemeral=True)

        await ctx.followup.send(
            embed=self.scrim_info_embed(scrim=_scrim),
            ephemeral=True
        )

    class DuplicateTagCheck(Enum):
        ENABLED = "enabled"
        DISABLED = "disabled"


    @set_app.command(name="fake_tag", description="Enable or disable fake tag filter for a scrim.")
    @app.guild_only()
    @app.describe(
        reg_channel="Registration channel of the scrim to set fake tag filter (required)",
        fake_tag="Enable or disable fake tag filter (required)",
    )
    @app.checks.bot_has_permissions(manage_roles=True, manage_channels=True, send_messages=True, embed_links=True)
    async def set_fake_tag(self, ctx:discord.Interaction, reg_channel:discord.TextChannel, fake_tag:DuplicateTagCheck):
        """Enable or disable fake tag filter for a scrim."""
        await ctx.response.defer(ephemeral=True)

        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send("No scrim found for the provided registration channel.", ephemeral=True)

        # Update the fake tag filter in the scrim
        _scrim.duplicate_tag_check = fake_tag.value
        _scrim.save()

        await ctx.followup.send(f"Fake tag filter for scrim `{_scrim.name}` has been {fake_tag.value}.", ephemeral=True)



    @set_app.command(name="idp_role", description="Set or update the IDP role for a scrim.")
    @app.guild_only()
    @app.describe(
        reg_channel="Registration channel of the scrim to set IDP role (required)",
        idp_role="IDP role to set for the scrim (required)",
    )
    @app.checks.bot_has_permissions(manage_roles=True, manage_channels=True, send_messages=True, embed_links=True)
    async def set_idp_role(self, ctx:discord.Interaction, reg_channel:discord.TextChannel, idp_role:discord.Role):
        """Set or update the IDP role for a scrim."""
        await ctx.response.defer(ephemeral=True)

        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send("No scrim found for the provided registration channel.", ephemeral=True)

        #  update the idp role in the scrim
        _scrim.idp_role = idp_role.id
        _scrim.save()

        await ctx.followup.send(f"IDP role for scrim `{_scrim.name}` has been set to {idp_role.mention}.", ephemeral=True)


    @set_app.command(name="ping_role", description="Set or update the ping role for a scrim.")
    @app.guild_only()
    @app.describe(
        reg_channel="Registration channel of the scrim to set ping role (required)",
        ping_role="Ping role to set for the scrim (required)",
    )
    @app.checks.bot_has_permissions(manage_roles=True, manage_channels=True, send_messages=True, embed_links=True)
    async def set_ping_role(self, ctx:discord.Interaction, reg_channel:discord.TextChannel, ping_role:discord.Role):
        """Set or update the ping role for a scrim."""
        await ctx.response.defer(ephemeral=True)

        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send("No scrim found for the provided registration channel.", ephemeral=True)

        #  update the ping role in the scrim
        _scrim.ping_role = ping_role.id
        _scrim.save()

        await ctx.followup.send(f"Ping role for scrim `{_scrim.name}` has been set to {ping_role.mention}.", ephemeral=True)


    @set_app.command(name="mentions", description="Set or update the number of mentions required to register a team for a scrim.")
    @app.guild_only()
    @app.describe(
        reg_channel="Registration channel of the scrim to update mentions (required)",
        mentions="Number of mentions required to register a team (required)",
    )
    @app.checks.bot_has_permissions(manage_roles=True, manage_channels=True, send_messages=True, embed_links=True)
    async def set_mentions(self, ctx:discord.Interaction, reg_channel:discord.TextChannel, mentions:int):
        """Set or update the number of mentions required to register a team for a scrim."""
        await ctx.response.defer(ephemeral=True)

        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send("No scrim found for the provided registration channel.", ephemeral=True)

        #  update the mentions in the scrim
        _scrim.mentions = mentions
        _scrim.save()

        await ctx.followup.send(f"Mentions required for scrim `{_scrim.name}` have been set to {mentions}.", ephemeral=True)


    
    @set_app.command(name="total_slots", description="Set or update the total number of slots for a scrim.")
    @app.guild_only()
    @app.describe(
        reg_channel="Registration channel of the scrim to update total slots (required)",
        total_slots="Total number of slots for the scrim (required)",
    )
    @app.checks.bot_has_permissions(manage_roles=True, manage_channels=True, send_messages=True, embed_links=True)
    async def set_total_slots(self, ctx:discord.Interaction, reg_channel:discord.TextChannel, total_slots:int):
        """Set or update the total number of slots for a scrim."""
        await ctx.response.defer(ephemeral=True)

        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send("No scrim found for the provided registration channel.", ephemeral=True)

        #  update the total slots in the scrim
        _scrim.total_slots = total_slots
        _scrim.save()

        await ctx.followup.send(f"Total slots for scrim `{_scrim.name}` have been set to {total_slots}.", ephemeral=True)



    @set_app.command(name="open_time", description="Set or update the open time for a scrim.")
    @app.guild_only()
    @app.describe(
        reg_channel="Registration channel of the scrim to update open time (required)",
        open_time="Open time for the scrim (required)",
    )
    @app.checks.bot_has_permissions(manage_roles=True, manage_channels=True, send_messages=True, embed_links=True)
    async def set_open_time(self, ctx:discord.Interaction, reg_channel:discord.TextChannel, open_time:str):
        """Set or update the open time for a scrim."""
        await ctx.response.defer(ephemeral=True)

        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send("No scrim found for the provided registration channel.", ephemeral=True)

        parsed_open_time = int(self.time.parse_datetime(time_str=open_time, tz=_scrim.time_zone).timestamp())

        #  update the open time in the scrim
        _scrim.open_time = parsed_open_time
        _scrim.save()

        await ctx.followup.send(f"Open time for scrim <#{reg_channel.id}> has been set to <t:{parsed_open_time}:t>.", ephemeral=True)


    @set_app.command(name="close_time", description="Set or update the close time for a scrim.")
    @app.guild_only()
    @app.describe(reg_channel="Registration channel of the scrim to update close time (required)",
                  close_time="Close time for the scrim (required)")
    @app.checks.bot_has_permissions(manage_roles=True, manage_channels=True, send_messages=True, embed_links=True)
    async def set_close_time(self, ctx:discord.Interaction, reg_channel:discord.TextChannel, close_time:str):
        """Set or update the close time for a scrim."""
        await ctx.response.defer(ephemeral=True)

        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send("No scrim found for the provided registration channel.", ephemeral=True)

        try:
            parsed_close_time = int(self.time.parse_datetime(time_str=close_time, tz=_scrim.time_zone).timestamp())
            
        except ValueError:
            return await ctx.followup.send(f"Invalid close time format. Please use HH:MM AM/PM format.", ephemeral=True)

        #  update the close time in the scrim
        _scrim.close_time = parsed_close_time
        _scrim.save()

        await ctx.followup.send(f"Close time for scrim <#{reg_channel.id}> has been set to <t:{parsed_close_time}:t>.", ephemeral=True)


    @set_app.command(name="time_zone", description="Set or update the time zone for a scrim.")
    @app.guild_only()
    @app.describe(
        reg_channel="Registration channel of the scrim to update time zone (required)",
        time_zone="Time zone for the scrim (required)",
    )
    @app.checks.bot_has_permissions(manage_roles=True, manage_channels=True, send_messages=True, embed_links=True)
    async def set_time_zone(self, ctx:discord.Interaction, reg_channel:discord.TextChannel, time_zone:constants.TimeZone):
        """Set or update the time zone for a scrim."""
        await ctx.response.defer(ephemeral=True)

        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send("No scrim found for the provided registration channel.", ephemeral=True)

        #  update the time zone in the scrim
        _scrim.time_zone = time_zone.value
        _scrim.save()

        await ctx.followup.send(f"Time zone for scrim <#{reg_channel.id}> has been set to {time_zone.value}.", ephemeral=True)



    @set_app.command(name="reg_channel", description="Set or update the registration channel for a scrim.")
    @app.guild_only()
    @app.describe(
        reg_channel="Registration channel of the scrim to update (required)",
    )
    @app.checks.bot_has_permissions(manage_roles=True, manage_channels=True, send_messages=True, embed_links=True)
    async def set_reg_channel(self, ctx:discord.Interaction, reg_channel:discord.TextChannel):
        """Set or update the registration channel for a scrim."""
        await ctx.response.defer(ephemeral=True)

        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send("No scrim found for the provided registration channel.", ephemeral=True)

        #  update the registration channel in the scrim
        _scrim.reg_channel = reg_channel.id
        _scrim.save()

        await ctx.followup.send(f"Registration channel for scrim `{_scrim.name}` has been set to <#{reg_channel.id}>.", ephemeral=True)


    @set_app.command(name="slot_channel", description="Set or update the slot channel for a scrim.")
    @app.guild_only()
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
            return await ctx.followup.send("No scrim found for the provided registration channel.", ephemeral=True)

        #  update the slot channel in the scrim
        _scrim.slot_channel = slot_channel.id
        _scrim.save()

        await ctx.followup.send(f"Slot channel for scrim `{_scrim.name}` has been set to <#{slot_channel.id}>.", ephemeral=True)



    @add_app.command(name="reserved_slots", description="View or update the reserved slots for a scrim.")
    @app.guild_only()
    @app.describe(
        reg_channel="Registration channel of the scrim to view or update reserved slots (required)",
        team_name="Name of the team to reserve a slot (required)",
        captain="ID of the captain of the team (required)",
    )
    @app.checks.bot_has_permissions(manage_roles=True, manage_channels=True, send_messages=True, embed_links=True)
    async def add_reserved_slots(self, ctx:discord.Interaction, reg_channel:discord.TextChannel, team_name:str, captain:discord.Member):
        """View or update the reserved slots for a scrim."""
        await ctx.response.defer(ephemeral=True)

        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send("No scrim found for the provided registration channel.", ephemeral=True)
        
        if(len(_scrim.reserved) >= _scrim.total_slots):
            return await ctx.followup.send("All slots are already reserved for this scrim.", ephemeral=True)

        #  check if the team is already reserved
        if any(team_name.lower() in list(_scrim.reserved.values())):
            return await ctx.followup.send(f"Team `{team_name}` is already reserved in this scrim.", ephemeral=True)
    
        #  add the reserved slot
        _scrim.reserved[captain.id] = team_name
        _scrim.save()

        await ctx.followup.send(f"Reserved slot for team `{team_name}` has been added successfully.", ephemeral=True)

    
    @remove_app.command(name="reserved_slots", description="View or remove a reserved slot for a scrim.")
    @app.guild_only()
    @app.describe(
        reg_channel="Registration channel of the scrim to view or remove reserved slots (required)",
        captain="ID of the captain of the team whose reserved slot you want to remove (required)",
    )
    @app.checks.bot_has_permissions(manage_roles=True, manage_channels=True, send_messages=True, embed_links=True)
    async def remove_reserved_slots(self, ctx:discord.Interaction, reg_channel:discord.TextChannel, captain:discord.Member):
        """View or remove a reserved slot for a scrim."""
        await ctx.response.defer(ephemeral=True)

        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send("No scrim found for the provided registration channel.", ephemeral=True)

        #  find the reserved slot by captain id
        if captain.id not in _scrim.reserved:
            return await ctx.followup.send(f"No reserved slot found for captain {captain.mention} in this scrim.", ephemeral=True)

        #  remove the reserved slot
        _scrim.reserved.pop(captain.id)
        _scrim.save()

        await ctx.followup.send(f"Reserved slot for captain {captain.mention} has been removed successfully.", ephemeral=True)







    @app.command(name="delete", description="Delete a scrim by its ID.")
    @app.guild_only()
    @app.describe(
        reg_channel="Registration channel of the scrim to delete (required)",
    )
    @app.checks.bot_has_permissions(manage_roles=True, manage_channels=True, manage_messages=True, read_message_history=True)
    async def delete_scrim(self, ctx:discord.Interaction, reg_channel:discord.TextChannel):
        """Delete a scrim by its registration channel."""
        await ctx.response.defer(ephemeral=True)

        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send("No scrim found for the provided registration channel.", ephemeral=True)

        #  delete the scrim from the database
        _scrim.delete()

        await ctx.followup.send(f"Scrim `{_scrim.name}` has been deleted successfully.", ephemeral=True)




    @app.command(name="toggle", description="Toggle the status of a scrim by its ID.")
    @app.guild_only()
    @app.describe(
        reg_channel="Registration channel of the scrim to toggle (required)",
    )
    
    @app.checks.bot_has_permissions(manage_roles=True, manage_channels=True, send_messages=True, embed_links=True)
    async def toggle_scrim(self, ctx:discord.Interaction, reg_channel:discord.TextChannel):
        await ctx.response.defer(ephemeral=True)
        """Toggle the status of a scrim by its registration channel."""
        _scrim = ScrimModel.find_by_reg_channel(reg_channel.id)
        if not _scrim:
            return await ctx.followup.send("No scrim found for the provided registration channel.", ephemeral=True)
        
        # Toggle the scrim status
        _scrim.status = not _scrim.status
        _scrim.save()
        status = "opened" if _scrim.status else "closed"
        await reg_channel.send(f"The scrim has been {status}!")
        await ctx.followup.send(f"Scrim {reg_channel.mention} has been {status}.", ephemeral=True)




    @set_app.command(name="log", description="Setup or update the scrim log channel.")
    @app.guild_only()
    
    @app.checks.bot_has_permissions(manage_channels=True, send_messages=True, embed_links=True)
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


    @app.command(name="list", description="List all scrims in the server.")
    @app.guild_only()
    @permissions.under_maintenance()
    
    async def list_scrims(self, ctx:discord.Interaction):
        """List all scrims in the server."""
        await ctx.response.defer(ephemeral=True)

        scrims = ScrimModel.find(guild_id=ctx.guild.id)
        if not scrims:
            return await ctx.followup.send("No scrims found in this server.", ephemeral=True)


        class ScrimConfigView:
            def __init__(self, embed:discord.Embed, view:discord.ui.View):
                self.embed = embed
                self.view = view


        class ScrimActionDropdown(discord.ui.Select):
            def __init__(self, bot:"Spruce", scrim: ScrimModel):
                self.bot = bot
                options = [
                    discord.SelectOption(label="IDP Role", value=f"idp_role_{scrim.reg_channel}", description="Update the IDP role for this scrim."),
                    discord.SelectOption(label="Ping Role", value=f"ping_role_{scrim.reg_channel}", description="View or update the ping role for this scrim."),
                    discord.SelectOption(label="Mentions", value=f"mentions_{scrim.reg_channel}", description="View or update the number of mentions required to register a team."),
                    discord.SelectOption(label="Total Slots", value=f"total_slots_{scrim.reg_channel}", description="View or update the total number of slots for this scrim."),
                    discord.SelectOption(label="Open Time", value=f"open_time_{scrim.reg_channel}", description="View or update the open time for this scrim."),
                    discord.SelectOption(label="Close Time", value=f"close_time_{scrim.reg_channel}", description="View or update the close time for this scrim."),
                    discord.SelectOption(label="Time Zone", value=f"time_zone_{scrim.reg_channel}", description="View or update the time zone for this scrim."),
                    discord.SelectOption(label="Registration Channel", value=f"reg_channel_{scrim.reg_channel}", description="View or update the registration channel for this scrim."),
                    discord.SelectOption(label="Slot Channel", value=f"slot_channel_{scrim.reg_channel}", description="View or update the slot channel for this scrim."),
                    discord.SelectOption(label="Reserved Slots", value=f"reserved_slots_{scrim.reg_channel}", description="View the reserved slots for this scrim."),
                    discord.SelectOption(label="Cancel Slot", value=f"cancel_slot_{scrim.reg_channel}", description="Cancel a slot for this scrim."),
                ]
                super().__init__(placeholder="Select an action", options=options, custom_id=f"scrim_select_{scrim.reg_channel}")
                self.scrim = scrim


            async def callback(self, interaction:discord.Interaction):
                if interaction.user.id != self.bot.user.id:
                    return await interaction.response.send_message("You are not allowed to use this dropdown.", ephemeral=True)
                
                if self.values[0] == f"idp_role_{self.scrim.reg_channel}":
                    await interaction.response.send_message("IDP Role selected.", ephemeral=True)

        scrim_views: list[ScrimConfigView] = []
        # current_index = 0
        for current_index, scrim in enumerate(scrims):
            _view = discord.ui.View(timeout=None)
            _items = [
                ScrimActionDropdown(bot=self.bot, scrim=scrim),
                discord.ui.Button(emoji="◀️", disabled=current_index == 0, custom_id=f"scrim_prev_{scrim.reg_channel}"),
                discord.ui.Button(emoji="📢", disabled=True, custom_id=f"scrim_promote_{scrim.reg_channel}"),
                discord.ui.Button(emoji="🗑️", disabled=True, style=discord.ButtonStyle.danger, custom_id=f"scrim_delete_{scrim.reg_channel}"),
                discord.ui.Button(emoji="▶️", disabled=current_index == len(scrims) - 1, custom_id=f"scrim_next_{scrim.reg_channel}")
            ]
            for item in _items:
                _view.add_item(item)
            
            scrim_views.append(ScrimConfigView(embed=self.scrim_info_embed(scrim=scrim), view=_view))


        await ctx.followup.send(embed=scrim_views[0].embed, view=scrim_views[0].view, ephemeral=True)



    @commands.Cog.listener()
    async def on_scrim_open_time_hit(self, scrim:ScrimModel):
        """Listener for when a scrim start time is hit."""

        scrim.status = True
        scrim.open_time += self.scrim_interval  # Interval is now configurable
        print("Set scrim open time:", self.time.parse_timestamp(scrim.open_time, tz=scrim.time_zone))
        scrim.save()

        _channel = self.bot.get_channel(scrim.reg_channel)

        if not _channel.guild.me.guild_permissions.manage_roles:

            return await self.bot.helper.get_scrim_log(_channel.guild).send(
                embed=self.log_embed(f"Scrim {scrim.name} could not be started as I don't have permission to manage roles.")
            ) if self.bot.helper.get_scrim_log(_channel.guild) else None

        if _channel.permissions_for(_channel.guild.me).send_messages:
    
            start_message = await  _channel.send(
                content=f"<@&{scrim.ping_role}>" if scrim.ping_role else None,
                embed = discord.Embed(
                    title=f"**{self.bot.emoji.cup} | REGISTRATION STARTED | {self.bot.emoji.cup}**",
                    description=self.configure_start_message(scrim=scrim), color=self.bot.color.random())
                )

            if _channel.permissions_for(_channel.guild.me).add_reactions:
                await start_message.add_reaction(self.bot.emoji.tick)


            def purge_filter(message:discord.Message):

                if message.id == start_message.id:
                    return False

                if self.bot.is_ws_ratelimited():
                    return False

                return True


            if _channel.permissions_for(_channel.guild.me).manage_messages:
                await _channel.purge(limit=scrim.total_slots+10, check=purge_filter, before=start_message)





    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        """Listener for when a message is sent in a scrim registration channel."""
        if message.author.bot or not isinstance(message.channel, discord.TextChannel):
            return
        
        if not message.channel.permissions_for(message.guild.me).send_messages:
            return
        
        if not message.guild.me.guild_permissions.manage_messages:
            return
        
        if not message.channel.permissions_for(message.guild.me).read_message_history:
            return

        if not message.channel.permissions_for(message.guild.me).add_reactions:
            return
        
        if not message.guild.me.guild_permissions.manage_roles:
            return

        if discord.utils.get(message.author.roles, name=self.TAG_IGNORE_ROLE):
            return  # Ignore messages from users with the scrim-ignore-tag role

        log_channel = self.bot.helper.get_scrim_log(message.guild)
        _scrim = ScrimModel.find_by_reg_channel(message.channel.id)
        
        #  if no scrim is found, return
        if not _scrim or not _scrim.status:
            return
        
        available_slots = _scrim.total_slots - (len(_scrim.reserved) + _scrim.team_count)
        scrim_mod_role = discord.utils.get(message.guild.roles, name="scrim-mod")
        confirm_role = message.guild.get_role(_scrim.idp_role)


        # check if idp role exists or not, if  not, then close the scrim and inform the scrim mod role if exists
        if not confirm_role:
            _scrim.status = False
            _scrim.save()

            await log_channel.send(
                content=scrim_mod_role.mention if scrim_mod_role else None,
                embed=self.log_embed(f"IDP role not found for scrim <#{_scrim.reg_channel}>. Please check the scrim configuration.", color=self.bot.color.red)
            ) if log_channel else None


        #  Check if the member is already registered for the scrim (having idp role)
        if discord.utils.get(message.author.roles, id=_scrim.idp_role):
            await message.channel.send(
                f"**{message.author.mention}**: You already have IDP role for this scrim. You cannot register again.",
                delete_after=10
            )
            await message.delete()
            return

        #  check if there is any available slot for registration
        if available_slots <= 0:

            await message.channel.send(
                f"**{message.author.mention}**: All slots are full for this scrim. Please wait for the next one.",
                delete_after=10
            )

            #  log action info
            if log_channel:
                await log_channel.send(
                    embed=self.log_embed(f"{_scrim.name} closed as all slots are full. still {message.author.mention} tried to register a team.")
                )

            await self.bot.dispatch("scrim_close_time_hit", _scrim)  # Dispatch the close time hit event
            return None # no available slots
        

        _team_name = self.bot.helper.parse_team_name(message)

        #  Check if the team name is valid
        if len(_team_name) < 3 or len(_team_name) > 20:
            await message.channel.send(
                f"**{message.author.mention}**: Team name must be between 3 and 20 characters long.",
                delete_after=10
            )
            return
        
        #  check if the required mentions are met
        if len(message.mentions) < _scrim.mentions:
            await message.channel.send(
                f"**{message.author.mention}**: You must mention at least {_scrim.mentions} members to register a team.",
                delete_after=10
            )
            await message.delete()
            await log_channel.send(
                embed=self.log_embed(f"{message.author.mention} tried to register a team but did not mention enough members. Required: {_scrim.mentions}, Mentioned: {len(message.mentions)}")
            ) if log_channel else None
            return

        #  checking for duplicate tag invalidation if duplicate tag is enabled
        if _scrim.duplicate_tag_check:
            is_duplicate_tag = await self.bot.helper.duplicate_tag_check(confirm_role, message)
                
            if is_duplicate_tag:
                await message.delete()
                await message.channel.send(
                    embed=discord.Embed(
                        title="Duplicate Tag Detected",
                        description=f"{is_duplicate_tag.mention} you've mentioned is registered to a different [team]({is_duplicate_tag.message.jump_url}). Please check your mentions and try again.",
                    )
                )
                if log_channel:
                    await log_channel.send(
                        embed=self.log_embed(f"{message.author.mention} tried to register a team with a duplicate tag: {is_duplicate_tag.mention}.", color=self.bot.color.red)
                    )
                return
            
        await message.author.add_roles(confirm_role, reason="Scrim registration")
        await message.add_reaction(self.bot.emoji.tick)
        _scrim.team_count += 1
        _scrim.save()

        await log_channel.send(
            embed=self.log_embed(f"{message.author.mention} has registered for scrim {_scrim.name}.")
        ) if log_channel else None



    @commands.Cog.listener()
    async def on_scrim_close_time_hit(self, scrim:ScrimModel):
        """Listener for when a scrim end time is hit."""

        scrim.close_time += self.scrim_interval

        # error correction for scrim open time
        # if scrim open time is in the past, but status is True means the open_time was not updated
        if scrim.open_time < self.time.now().timestamp() and scrim.status==True:
            scrim.open_time += self.scrim_interval

        scrim.status = False
        scrim.save()

        _channel = self.bot.get_channel(scrim.slot_channel)
        scrim_log = self.bot.helper.get_scrim_log(_channel.guild)

        if scrim_log and scrim_log.permissions_for(_channel.guild.me).send_messages:
            await scrim_log.send(
                embed=self.log_embed(f"Scrim <#{scrim.reg_channel}> has ended. ")
            )

        await self.setup_group(scrim)




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



    @tasks.loop(seconds=1)
    async def monitor_scrims(self):
        time = self.time.now().strftime("%H%M")

        if time in _resolved_scrims:
            return
        print(_resolved_scrims)

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
