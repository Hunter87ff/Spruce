"""
Tournament Management System for Discord Esports
A comprehensive module for managing esports tournaments in Discord servers.

:author: hunter87
:copyright: (c) 2022-present hunter87.dev@gmail.com
:license: GPL-3, see LICENSE for more details.
"""

import asyncio
import logging
import traceback
from typing import TYPE_CHECKING, Optional, List
from random import shuffle as random_shuffle

import discord
from discord.ext import commands
from discord import app_commands

from core.abstract import GroupCog
from models.tourney import TourneyModel, ConfirmedTeamModel
from ext import (
    checks, color, emoji, files, EmbedBuilder,
    constants
)

if TYPE_CHECKING:
    from core.bot import Spruce

logger = logging.getLogger(__name__)


class TourneyError(Exception):
    """Base exception for tournament-related errors."""
    pass


class TourneyNotFoundError(TourneyError):
    """Raised when a tournament is not found."""
    pass


class InvalidTourneyConfigError(TourneyError):
    """Raised when tournament configuration is invalid."""
    pass


class GroupConfig:
    """Configuration for group generation."""
    
    def __init__(
        self,
        current_group: int,
        messages: List[discord.Message],
        total_messages: int,
        event: TourneyModel,
        group_channel: discord.TextChannel,
        group_category: Optional[discord.CategoryChannel] = None
    ):
        self.current_group = current_group
        self.messages = messages
        self.total_messages = total_messages
        self.event = event
        self.group_channel = group_channel
        self.group_category = group_category


class Esports(GroupCog, name="esports", group_name="esports"):
    """
    Tournament Management Cog
    """
    
    # Constants
    ONLY_AUTHOR_BUTTON = "Only Author Can Use This Button"
    MANAGER_PREFIXES = ["Cslot", "Mslot", "Tname", "Cancel"]
    
    def __init__(self, bot: 'Spruce'):
        self.bot: 'Spruce' = bot
        self.emoji = self.bot.emoji.cup
        self.TOURNEY_LOG_CHANNEL_NAME = f"{self.bot.user.name.lower()}-tourney-log"
        self.HIGHER_ROLE_POSITION = "{role.mention} has a higher role position than me. Please move it below my role and try again."
        
        # Setup the model collection reference
        TourneyModel._col = self.bot.db.dbc
        TourneyModel.bot = self.bot

    # App command groups
    app_set = app_commands.Group(name="set", description="Tournament configuration commands")

    async def cog_load(self):
        """Called when the cog is loaded."""
        logger.info("Tournament cog loaded successfully")

    async def cog_unload(self):
        """Called when the cog is unloaded."""
        logger.info("Tournament cog unloaded")

    # Utility Methods
    # ================

    def is_tourney_mod(self, member: discord.Member) -> bool:
        """Check if a member has tournament moderation permissions."""
        return any([
            member.guild_permissions.manage_guild,
            member.guild_permissions.administrator,
            discord.utils.get(member.guild.roles, name="tourney-mod") in member.roles,
        ])

    async def get_tourney_or_error(self, channel_id: int) -> TourneyModel:
        """Get tournament or raise appropriate error."""
        tourney = await TourneyModel.get(channel_id)
        if not tourney:
            raise TourneyNotFoundError("Tournament not found for this channel.")
        return tourney

    async def log_tournament_action(
        self,
        guild: discord.Guild,
        message: str,
        embed_color: int = color.cyan
    ) -> None:
        """Log tournament actions to the designated log channel."""
        try:
            channel = discord.utils.get(guild.text_channels, name=self.TOURNEY_LOG_CHANNEL_NAME)
            if not channel:
                return

            embed = discord.Embed(description=message, color=embed_color)
            embed.set_author(name=guild.me.name, icon_url=guild.me.avatar)
            await channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Failed to log tournament action: {e}")

    async def get_user_input(
        self,
        ctx: commands.Context,
        check=None,
        timeout: int = 30
    ) -> Optional[str]:
        """Get user input with timeout handling."""
        check = check or (lambda m: m.channel == ctx.channel and m.author == ctx.author)
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=timeout)
            return msg.content
        except asyncio.TimeoutError:
            await ctx.send("⏰ Time out! Try again.", delete_after=5)
            return None

    # Setup Commands
    # ==============

    @app_set.command(name="log", description="Setup tournament log channel")
    @checks.tourney_mod(interaction=True)
    @app_commands.guild_only()
    @commands.bot_has_guild_permissions(send_messages=True, attach_files=True, manage_channels=True)
    async def setup_tourney_log(self, interaction: discord.Interaction):
        """Setup or configure the tournament log channel."""
        await interaction.response.defer(ephemeral=True)

        try:
            # Get or create log channel
            channel = discord.utils.get(interaction.guild.text_channels, name=self.TOURNEY_LOG_CHANNEL_NAME)
            
            if not channel:
                channel = await interaction.guild.create_text_channel(
                    name=self.TOURNEY_LOG_CHANNEL_NAME,
                    topic="Tournament event logs and notifications"
                )

            # Set permissions
            await channel.set_permissions(interaction.guild.default_role, read_messages=False)
            await channel.set_permissions(
                interaction.guild.me,
                read_messages=True,
                send_messages=True,
                attach_files=True,
                manage_channels=True,
                manage_messages=True,
                add_reactions=True,
                external_emojis=True
            )

            # Send confirmation
            await interaction.followup.send(
                f"**Tournament Log Channel Set To {channel.mention}**",
                ephemeral=True
            )

            # Send welcome message to log channel
            embed = discord.Embed(
                title="Tournament Log Channel Created",
                description=f"**This channel will be used to log tournament events**\n\n{emoji.tick} | **Created By**: {interaction.user.mention}",
                color=color.cyan
            )
            await channel.send(embed=embed)

        except Exception as e:
            logger.error(f"Error setting up tournament log: {e}")
            await interaction.followup.send(
                embed=EmbedBuilder.warning("Failed to setup tournament log channel. Please check bot permissions."),
                ephemeral=True
            )

    # Tournament Management Commands
    # ==============================

    @app_commands.command(name="setup", description="Create a new tournament")
    @app_commands.describe(
        total_slots="Total number of slots for the tournament",
        mentions="Number of mentions required for registration",
        slots_per_group="Number of slots per group",
        name="Name of the tournament"
    )
    @commands.bot_has_guild_permissions(
        manage_channels=True,
        manage_roles=True,
        send_messages=True,
        add_reactions=True,
        read_message_history=True
    )
    @commands.guild_only()
    @app_commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @checks.tourney_mod(interaction=True)
    async def tourney_setup(
        self,
        interaction: discord.Interaction,
        total_slots: int,
        mentions: int,
        slots_per_group: int,
        *,
        name: str
    ):
        """Setup a new tournament with the specified configuration."""
        await interaction.response.defer(ephemeral=True)

        try:
            # Validation
            if slots_per_group < 1:
                raise InvalidTourneyConfigError("Slots per group must be at least 1.")
            
            if total_slots < slots_per_group:
                raise InvalidTourneyConfigError("Total slots must be greater than or equal to slots per group.")
            
            if mentions < 1:
                raise InvalidTourneyConfigError("Mentions must be at least 1.")

            # Get tournament prefix
            prefix = self.bot.helper.get_event_prefix(name)

            # Create tournament category
            category = await interaction.guild.create_category(name=name.upper())

            # Create registration channel
            reg_channel = await interaction.guild.create_text_channel(
                name=f"{prefix.lower()}-registration",
                category=category
            )

            # Create confirmation channel
            confirm_channel = await interaction.guild.create_text_channel(
                name=f"{prefix.lower()}-confirmed",
                category=category
            )

            # Create group channel
            group_channel = await interaction.guild.create_text_channel(
                name=f"{prefix.lower()}-groups",
                category=category
            )

            # Create confirmation role
            confirm_role = await interaction.guild.create_role(
                name=f"{prefix.upper()}-CONFIRMED",
                color=color.green
            )

            # Create tournament in database
            tournament = await TourneyModel.create(
                guild=interaction.guild.id,
                name=name,
                rch=reg_channel.id,
                cch=confirm_channel.id,
                mentions=mentions,
                crole=confirm_role.id,
                gch=group_channel.id,
                tslot=total_slots,
                spg=slots_per_group,
                mch=confirm_channel.id,  # Slot manager channel is the confirmation channel
            )

            # Set channel permissions
            await self._setup_tournament_permissions(
                category, reg_channel, confirm_channel, group_channel, confirm_role, interaction.guild
            )

            # Log the creation
            await self.log_tournament_action(
                interaction.guild,
                f"Tournament **{name}** created by {interaction.user.mention}\n"
                f"• Registration: {reg_channel.mention}\n"
                f"• Confirmed: {confirm_channel.mention}\n"
                f"• Groups: {group_channel.mention}\n"
                f"• Total Slots: {total_slots}\n"
                f"• Mentions Required: {mentions}"
            )

            embed = EmbedBuilder.success(
                f"Tournament **{name}** created successfully!\n\n"
                f"**Registration Channel:** {reg_channel.mention}\n"
                f"**Confirmed Channel:** {confirm_channel.mention}\n"
                f"**Group Channel:** {group_channel.mention}\n"
                f"**Total Slots:** {total_slots}\n"
                f"**Required Mentions:** {mentions}"
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

        except TourneyError as e:
            await interaction.followup.send(embed=EmbedBuilder.warning(str(e)), ephemeral=True)
        except Exception as e:
            logger.error(f"Error creating tournament: {traceback.format_exc()}")
            await interaction.followup.send(
                embed=EmbedBuilder.warning("An error occurred while creating the tournament. Please try again."),
                ephemeral=True
            )

    async def _setup_tournament_permissions(
        self,
        category: discord.CategoryChannel,
        reg_channel: discord.TextChannel,
        confirm_channel: discord.TextChannel,
        group_channel: discord.TextChannel,
        confirm_role: discord.Role,
        guild: discord.Guild
    ):
        """Setup permissions for tournament channels."""
        # Category permissions
        await category.set_permissions(guild.default_role, view_channel=True, send_messages=False)
        await category.set_permissions(guild.me, view_channel=True, send_messages=True, manage_messages=True)

        # Registration channel - everyone can send messages
        await reg_channel.set_permissions(guild.default_role, send_messages=True, add_reactions=True)

        # Confirmation channel - only confirmed teams can see
        await confirm_channel.set_permissions(guild.default_role, view_channel=False)
        await confirm_channel.set_permissions(confirm_role, view_channel=True, send_messages=False)
        await confirm_channel.set_permissions(guild.me, view_channel=True, send_messages=True)

        # Group channel - read-only for everyone
        await group_channel.set_permissions(guild.default_role, send_messages=False, add_reactions=False)
        await group_channel.set_permissions(guild.me, send_messages=True, manage_messages=True)

    @app_commands.command(name="start", description="Start tournament registration")
    @app_commands.guild_only()
    @checks.tourney_mod(interaction=True)
    @app_commands.describe(
        reg_channel="The tournament registration channel"
    )
    async def start_tourney(self, interaction: discord.Interaction, reg_channel: discord.TextChannel):
        """Start registration for a tournament."""
        await interaction.response.defer(ephemeral=True)

        try:
            tournament = await self.get_tourney_or_error(reg_channel.id)
            
            # Update tournament status (you might want to add a status field to the model)
            # For now, we'll just send the registration started message
            
            available_slots = tournament.total_slots - tournament.team_count
            
            embed = EmbedBuilder(
                title="🏆 Tournament Registration Started!",
                description=f"Registration is now **OPEN**\n\n"
                           f"**{emoji.tick} Available Slots:** {available_slots}\n"
                           f"**{emoji.tick} Required Mentions:** {tournament.mentions}\n"
                           f"**{emoji.tick} Tournament:** {tournament.name}",
                color=color.green
            )
            embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon)
            
            await reg_channel.send(embed=embed)
            await interaction.followup.send(embed=EmbedBuilder.success("Tournament registration started successfully!"))
            
            await self.log_tournament_action(
                interaction.guild,
                f"Tournament registration started by {interaction.user.mention} in {reg_channel.mention}"
            )

        except TourneyNotFoundError as e:
            await interaction.followup.send(embed=EmbedBuilder.warning(str(e)), ephemeral=True)
        except Exception as e:
            logger.error(f"Error starting tournament: {e}")
            await interaction.followup.send(
                embed=EmbedBuilder.warning("Failed to start tournament registration."),
                ephemeral=True
            )

    @app_commands.command(name="pause", description="Pause tournament registration")
    @checks.tourney_mod(interaction=True)
    @app_commands.describe(
        reg_channel="The tournament registration channel"
    )
    async def pause_tourney(self, interaction: discord.Interaction, reg_channel: discord.TextChannel):
        """Pause registration for a tournament."""
        await interaction.response.defer(ephemeral=True)

        try:
            tournament = await self.get_tourney_or_error(reg_channel.id)
            
            embed = EmbedBuilder(
                title="⏸️ Tournament Registration Paused",
                description="Registration has been temporarily paused by moderators.",
                color=color.yellow
            )
            
            await reg_channel.send(embed=embed)
            await interaction.followup.send(embed=EmbedBuilder.success("Tournament registration paused successfully!"))
            
            await self.log_tournament_action(
                interaction.guild,
                f"Tournament registration paused by {interaction.user.mention} in {reg_channel.mention}",
                color.yellow
            )

        except TourneyNotFoundError as e:
            await interaction.followup.send(embed=EmbedBuilder.warning(str(e)), ephemeral=True)
        except Exception as e:
            logger.error(f"Error pausing tournament: {e}")
            await interaction.followup.send(
                embed=EmbedBuilder.warning("Failed to pause tournament registration."),
                ephemeral=True
            )

    # Data Export Command
    # ===================

    @app_commands.command(name="export", description="Export tournament data to CSV file")
    @checks.tourney_mod(interaction=True)
    @app_commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.bot_has_guild_permissions(send_messages=True, attach_files=True)
    @app_commands.describe(
        registration_channel="The tournament registration channel"
    )
    async def export(self, interaction: discord.Interaction, registration_channel: discord.TextChannel):
        """Export tournament data to a CSV file."""
        await interaction.response.defer(ephemeral=True)

        try:
            tournament = await self.get_tourney_or_error(registration_channel.id)
            
            # Get confirmation channel
            confirm_channel = self.bot.get_channel(tournament.slot_channel)
            if not confirm_channel:
                raise TourneyError("Confirmation channel not found.")

            if not confirm_channel.permissions_for(interaction.guild.me).read_message_history:
                raise TourneyError("Bot lacks permission to read message history in confirmation channel.")

            # Collect team data
            teams_data = []
            slot_number = 1

            async for message in confirm_channel.history(limit=tournament.team_count + 50):
                if message.author == self.bot.user and message.mentions:
                    try:
                        team = ConfirmedTeamModel(message)
                        teams_data.append(f"{slot_number},{team.name},{team.captain.display_name},{';'.join(team.players)}\n")
                        slot_number += 1
                    except Exception:
                        continue  # Skip invalid messages

            # Create CSV content
            csv_content = "Event,Slots,Registered,Mentions,Prize\n"
            csv_content += f"{tournament.name},{tournament.total_slots},{tournament.team_count},{tournament.mentions},TBD\n\n"
            csv_content += "Slot,Team Name,Captain,Players\n"
            csv_content += "".join(teams_data)

            # Generate file
            filename = f"tournament_data_{tournament.reg_channel}"
            fp, cleanup = files.export_to_csv(
                csv_content,
                filename,
                lambda module, loc, e: logger.error(f"CSV export error in {module}:{loc} - {e}")
            )
            
            await interaction.followup.send(file=discord.File(fp, filename=f"{filename}.csv"))
            cleanup()

            await self.log_tournament_action(
                interaction.guild,
                f"Tournament data exported by {interaction.user.mention} for {registration_channel.mention}"
            )

        except TourneyError as e:
            await interaction.followup.send(embed=EmbedBuilder.warning(str(e)), ephemeral=True)
        except Exception as e:
            logger.error(f"Error exporting tournament data: {e}")
            await interaction.followup.send(
                embed=EmbedBuilder.warning("Something went wrong during export. Please try again later."),
                ephemeral=True
            )

    # Group Management Commands
    # =========================

    @app_commands.command(name="auto_group", description="Automatically create groups for the tournament")
    @app_commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.guild)
    @checks.tourney_mod(interaction=True)
    @app_commands.describe(
        reg_channel="The tournament registration channel",
        from_group="Group number to start from (default is 1)",
        group_category="Category to create group channels in (optional)",
        shuffle="Shuffle the teams before grouping (default is False)"
    )
    async def auto_group(
        self,
        interaction: discord.Interaction,
        reg_channel: discord.TextChannel,
        from_group: int = 1,
        shuffle: bool = False,
        group_category: Optional[discord.CategoryChannel] = None
    ):
        """Automatically generate groups for the tournament."""
        await interaction.response.defer(ephemeral=True)

        try:
            tournament = await self.get_tourney_or_error(reg_channel.id)
            
            confirm_channel = self.bot.get_channel(tournament.slot_channel)
            group_channel = self.bot.get_channel(tournament.group_channel)

            if not confirm_channel or not group_channel:
                raise TourneyError("Tournament channels not found. Please check the tournament setup.")

            # Calculate message limits
            base_index = (from_group * tournament.slot_per_group) - tournament.slot_per_group
            limit = tournament.team_count - (base_index + tournament.slot_per_group)
            
            # Collect confirmed team messages
            messages = []
            async for message in confirm_channel.history(limit=limit + tournament.slot_per_group, oldest_first=True):
                if message.author == self.bot.user and message.mentions:
                    messages.append(message)

            if shuffle:
                random_shuffle(messages)

            total_messages = len(messages)
            if base_index > total_messages:
                raise TourneyError(f"Starting group {from_group} is beyond available teams.")

            # Generate groups
            group_config = GroupConfig(from_group, messages, total_messages, tournament, group_channel, group_category)
            await self._generate_groups(group_config)
            
            await interaction.followup.send(
                embed=EmbedBuilder.success(
                    f"Groups generated from {from_group} to {group_config.current_group - 1} in {group_channel.mention}"
                )
            )

            await self.log_tournament_action(
                interaction.guild,
                f"Groups generated by {interaction.user.mention} for {reg_channel.mention}"
            )

        except TourneyError as e:
            await interaction.followup.send(embed=EmbedBuilder.warning(str(e)), ephemeral=True)
        except Exception as e:
            logger.error(f"Error generating groups: {e}")
            await interaction.followup.send(
                embed=EmbedBuilder.warning("Failed to generate groups. Please try again."),
                ephemeral=True
            )

    async def _generate_groups(self, group_config: GroupConfig):
        """Recursively generate tournament groups."""
        base_index = (group_config.current_group * group_config.event.slot_per_group) - group_config.event.slot_per_group
        to_index = base_index + group_config.event.slot_per_group
        team_count = 1

        if base_index >= group_config.total_messages:
            return

        # Create group message
        msg_content = f"**__Group {group_config.current_group}__**\n"
        
        for i in range(base_index, to_index):
            if i >= group_config.total_messages:
                break
            
            team_msg = group_config.messages[i]
            try:
                team = ConfirmedTeamModel(team_msg)
                msg_content += f"> {team_count:02d}) **{team.name}** - {team.captain.mention}\n"
                team_count += 1
            except Exception:
                continue  # Skip invalid team messages

        # Send group message
        group_msg = await group_config.group_channel.send(msg_content)
        await group_msg.add_reaction("✅")

        # Create group-specific channel if category is provided
        if isinstance(group_config.group_category, discord.CategoryChannel):
            try:
                await self._create_group_channel(group_config, msg_content)
            except Exception as e:
                logger.error(f"Error creating group channel: {e}")

        # Continue with next group
        group_config.current_group += 1
        await self._generate_groups(group_config)

    async def _create_group_channel(self, group_config: GroupConfig, msg_content: str):
        """Create a dedicated channel for a group."""
        prefix = self.bot.helper.get_event_prefix(group_config.event.name)
        
        channel = await group_config.group_category.guild.create_text_channel(
            name=f"{prefix.lower()}-group-{group_config.current_group}",
            category=group_config.group_category
        )
        
        # Send group info to the new channel
        msg = await channel.send(msg_content)
        await msg.add_reaction("✅")
        
        # Create group role
        role = await group_config.group_category.guild.create_role(
            name=f"{prefix.upper()}G{group_config.current_group}",
            color=self.bot.base_color if hasattr(self.bot, 'base_color') else color.cyan
        )
        
        # Set channel permissions
        overwrite = channel.overwrites_for(role)
        overwrite.update(view_channel=True, send_messages=False, add_reactions=False, attach_files=True)
        await channel.set_permissions(role, overwrite=overwrite)
        
        # Add role to team members
        for member in msg.mentions:
            try:
                await member.add_roles(role)
            except Exception as e:
                logger.error(f"Failed to add role to {member}: {e}")

    # Utility Commands
    # ================

    @app_commands.command(name="ignore_me", description="Ignore user in registration channels")
    @app_commands.guild_only()
    @checks.tourney_mod(interaction=True)
    async def ignore_me(self, interaction: discord.Interaction):
        """Add the ignore role to the user to prevent registration."""
        await interaction.response.defer(ephemeral=True)

        try:
            ignore_role = discord.utils.get(interaction.guild.roles, name="tag-ignore")
            
            if not ignore_role:
                ignore_role = await interaction.guild.create_role(
                    name="tag-ignore",
                    reason="Tournament registration ignore role"
                )

            if ignore_role.position >= interaction.guild.me.top_role.position:
                raise TourneyError("The ignore role has a higher position than my role. Please move it below my role.")

            if ignore_role in interaction.user.roles:
                await interaction.user.remove_roles(ignore_role)
                embed = EmbedBuilder.success(
                    f"Removed {ignore_role.mention} from you.\nYour messages will now be processed in registration channels."
                )
            else:
                await interaction.user.add_roles(ignore_role)
                embed = EmbedBuilder.success(
                    f"Added {ignore_role.mention} to you.\nYour messages will now be ignored in registration channels."
                )

            await interaction.followup.send(embed=embed, ephemeral=True)

        except TourneyError as e:
            await interaction.followup.send(embed=EmbedBuilder.warning(str(e)), ephemeral=True)
        except Exception as e:
            logger.error(f"Error toggling ignore role: {e}")
            await interaction.followup.send(
                embed=EmbedBuilder.warning("Failed to toggle ignore role."),
                ephemeral=True
            )

    # Team Management Commands
    # ========================

    @app_commands.command(name="cancel_slot", description="Cancel a slot for a team")
    @app_commands.guild_only()
    @checks.tourney_mod(interaction=True)
    @app_commands.describe(
        registration_channel="The tournament registration channel",
        member="The member whose slot you want to cancel",
        reason="The reason for canceling the slot"
    )
    async def cancel_slot(
        self,
        interaction: discord.Interaction,
        registration_channel: discord.TextChannel,
        member: discord.Member,
        reason: str = "Not Provided"
    ):
        """Cancel a team's slot in the tournament."""
        await interaction.response.defer(ephemeral=True)

        try:
            tournament = await self.get_tourney_or_error(registration_channel.id)
            
            confirm_role = interaction.guild.get_role(tournament.confirm_role)
            confirm_channel = self.bot.get_channel(tournament.slot_channel)

            if not confirm_channel:
                raise TourneyError("Confirmation channel not found.")

            if interaction.channel == confirm_channel:
                raise TourneyError("Cannot use this command in the confirmation channel.")

            if confirm_role not in member.roles:
                raise TourneyError(f"{member.mention} is not registered in this tournament.")

            # Find and delete the team's confirmation message
            async for message in confirm_channel.history(limit=tournament.team_count + 50):
                if message.author == self.bot.user and member in message.mentions:
                    try:
                        team = ConfirmedTeamModel(message)
                        await team.delete()
                        
                        # Remove role from member
                        await member.remove_roles(confirm_role)
                        
                        # Update tournament team count
                        tournament.team_count -= 1
                        await tournament.save()
                        
                        embed = EmbedBuilder.success(
                            f"Slot canceled for {member.mention}\n**Reason:** {reason}"
                        )
                        await interaction.followup.send(embed=embed)
                        
                        await self.log_tournament_action(
                            interaction.guild,
                            f"Slot canceled for {member.mention} by {interaction.user.mention}\nReason: {reason}",
                            color.red
                        )
                        return
                    except Exception:
                        continue

            raise TourneyError("Could not find the team's registration message.")

        except TourneyError as e:
            await interaction.followup.send(embed=EmbedBuilder.warning(str(e)), ephemeral=True)
        except Exception as e:
            logger.error(f"Error canceling slot: {e}")
            await interaction.followup.send(
                embed=EmbedBuilder.warning("Failed to cancel slot. Please try again."),
                ephemeral=True
            )

    @app_commands.command(name="add_slot", description="Add a slot for a team")
    @app_commands.guild_only()
    @checks.tourney_mod(interaction=True)
    @app_commands.describe(
        reg_channel="The tournament registration channel",
        member="The member to add to the slot",
        team_name="The name of the team"
    )
    async def add_slot(
        self,
        interaction: discord.Interaction,
        reg_channel: discord.TextChannel,
        member: discord.Member,
        *,
        team_name: str
    ):
        """Add a slot for a team in the tournament."""
        await interaction.response.defer(ephemeral=True)

        try:
            tournament = await self.get_tourney_or_error(reg_channel.id)
            
            confirm_role = interaction.guild.get_role(tournament.confirm_role)
            confirm_channel = self.bot.get_channel(tournament.slot_channel)

            if not confirm_role:
                raise TourneyError("Confirmation role not found.")

            if not confirm_channel:
                raise TourneyError("Confirmation channel not found.")

            if confirm_role in member.roles:
                raise TourneyError(f"{member.mention} is already registered in this tournament.")

            if tournament.team_count >= tournament.total_slots:
                raise TourneyError("Tournament is full. No more slots available.")

            # Add role to member
            await member.add_roles(confirm_role)
            
            # Create confirmation message
            embed = discord.Embed(
                title="Team Registered",
                description=f"Team: **{team_name}**\nCaptain: {member.mention}",
                color=color.green
            )
            
            confirmation_msg = await confirm_channel.send(
                content=f"{team_name} {member.mention}",
                embed=embed
            )
            await confirmation_msg.add_reaction("✅")
            
            # Update tournament team count
            tournament.team_count += 1
            await tournament.save()
            
            success_embed = EmbedBuilder.success(
                f"Slot added for {member.mention}\n**Team:** {team_name}"
            )
            await interaction.followup.send(embed=success_embed)
            
            await self.log_tournament_action(
                interaction.guild,
                f"Slot added for {member.mention} by {interaction.user.mention}\nTeam: {team_name}"
            )

        except TourneyError as e:
            await interaction.followup.send(embed=EmbedBuilder.warning(str(e)), ephemeral=True)
        except Exception as e:
            logger.error(f"Error adding slot: {e}")
            await interaction.followup.send(
                embed=EmbedBuilder.warning("Failed to add slot. Please try again."),
                ephemeral=True
            )

    @app_set.command(name="team_name", description="Change team name in the tournament")
    @app_commands.guild_only()
    @checks.tourney_mod(interaction=True)
    async def team_name(
        self,
        interaction: discord.Interaction,
        registration_channel: discord.TextChannel,
        player: discord.Member,
        new_name: Optional[str] = None
    ):
        """Change a team's name in the tournament."""
        await interaction.response.defer(ephemeral=True)

        try:
            tournament = await self.get_tourney_or_error(registration_channel.id)
            
            confirm_channel = self.bot.get_channel(tournament.slot_channel)
            if not confirm_channel:
                raise TourneyError("Confirmation channel not found.")

            # Find the team's message
            team_message = None
            async for msg in confirm_channel.history(limit=tournament.team_count + 20):
                if msg.author == self.bot.user and player in msg.mentions:
                    team_message = msg
                    break

            if not team_message:
                raise TourneyError(f"Could not find {player.mention}'s team registration.")

            if not new_name:
                # If no new name provided, get the current team name for reference
                try:
                    team = ConfirmedTeamModel(team_message)
                    current_name = team.name
                    raise TourneyError(f"Please provide a new team name. Current name: **{current_name}**")
                except Exception:
                    raise TourneyError("Please provide a new team name.")

            # Update the team name
            try:
                team = ConfirmedTeamModel(team_message)
                await team.edit(name=new_name)
                
                embed = EmbedBuilder.success(f"Team name updated to **{new_name}** for {player.mention}")
                await interaction.followup.send(embed=embed, ephemeral=True)
                
                await self.log_tournament_action(
                    interaction.guild,
                    f"Team name changed to '{new_name}' for {player.mention} by {interaction.user.mention}"
                )

            except Exception as e:
                logger.error(f"Error updating team name: {e}")
                raise TourneyError("Failed to update team name.")

        except TourneyError as e:
            await interaction.followup.send(embed=EmbedBuilder.warning(str(e)), ephemeral=True)
        except Exception as e:
            logger.error(f"Error changing team name: {e}")
            await interaction.followup.send(
                embed=EmbedBuilder.warning("Failed to change team name."),
                ephemeral=True
            )


    # Configuration Commands
    # ======================

    @app_set.command(name="group_channel", description="Change the group channel for the tournament")
    @app_commands.guild_only()
    @checks.tourney_mod(interaction=True)
    async def group_channel(
        self,
        interaction: discord.Interaction,
        registration_channel: discord.TextChannel
    ):
        """Create or update the group channel for a tournament."""
        await interaction.response.defer(ephemeral=True)

        try:
            tournament = await self.get_tourney_or_error(registration_channel.id)
            
            # Create new group channel
            prefix = self.bot.helper.get_event_prefix(tournament.name)
            group_channel = await registration_channel.guild.create_text_channel(
                name=f"{prefix.lower()}-groups",
                category=registration_channel.category,
                position=registration_channel.position + 1
            )
            
            # Update tournament
            tournament.group_channel = group_channel.id
            await tournament.save()
            
            # Set permissions
            await group_channel.set_permissions(
                target=interaction.guild.default_role,
                overwrite=discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=False,
                    add_reactions=False,
                    attach_files=True,
                    create_public_threads=False,
                )
            )
            await group_channel.set_permissions(
                target=interaction.guild.me,
                overwrite=discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    add_reactions=True,
                    attach_files=True,
                    create_public_threads=True,
                )
            )

            embed = EmbedBuilder.success(f"Group channel created: {group_channel.mention}")
            await interaction.followup.send(embed=embed, ephemeral=True)

        except TourneyError as e:
            await interaction.followup.send(embed=EmbedBuilder.warning(str(e)), ephemeral=True)
        except Exception as e:
            logger.error(f"Error creating group channel: {e}")
            await interaction.followup.send(
                embed=EmbedBuilder.warning("Failed to create group channel."),
                ephemeral=True
            )

    # Event Listeners
    # ===============

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.TextChannel):
        """Handle tournament channel deletion."""
        try:
            # Check if this was a tournament channel
            tournament = await TourneyModel.get(channel.id)
            if tournament:
                await TourneyModel.delete(channel.id)
                logger.info(f"Tournament deleted due to channel deletion: {channel.id}")

        except Exception as e:
            logger.error(f"Error handling channel deletion: {e}")

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        """Handle tournament role deletion."""
        try:
            # You might want to implement logic to handle role deletion
            # For now, just log it
            logger.info(f"Role deleted: {role.name} ({role.id})")
        except Exception as e:
            logger.error(f"Error handling role deletion: {e}")
