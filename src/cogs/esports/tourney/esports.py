"""
Tournament Management System for Discord Esports
A comprehensive module for managing esports tournaments in Discord servers.

:author: hunter87
:copyright: (c) 2022-present hunter87.dev@gmail.com
:license: GPL-3, see LICENSE for more details.
"""


import logging
import discord
import traceback
from typing import TYPE_CHECKING, Optional, List

from .ext.utils import TourneyUtils
from core.abstract import EmbedPaginator, GroupCog
from models.tourney import TourneyModel

from ext import ( checks, EmbedBuilder)
from discord import Interaction, TextChannel, app_commands


if TYPE_CHECKING:
    from core.bot import Spruce

logger = logging.getLogger(__name__)



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
    
    MANAGER_PREFIXES = ["Cslot", "Mslot", "Tname", "Cancel"]
    model : TourneyModel = TourneyModel
    
    def __init__(self, bot: 'Spruce'):
        self.bot: 'Spruce' = bot
        self.utils = TourneyUtils(self.bot)
        self.TOURNEY_LOG_CHANNEL_NAME = f"{self.bot.user.name.lower()}-tourney-log"
        self.HIGHER_ROLE_POSITION = "{role.mention} has a higher role position than me. Please move it below my role and try again."
        
        # Setup the model collection reference
        TourneyModel._col = self.bot.db.dbc
        TourneyModel.bot = self.bot

    # App command groups
    app_set = app_commands.Group(name="set", description="Tournament configuration commands")


    @app_commands.command(name="setup", description="Setup a new tournament")
    @app_commands.guild_only()
    @app_commands.describe(
        total_slot="Total number of slots available for the tournament (2-500)",
        mentions="Number of players to mention in the registration form (0-11)",
        slot_per_group="Number of slots per group (1-25)",
        event_name="Name of the tournament event (default: 'New Tournament')"
    )
    @checks.tourney_mod(True)
    async def setup_tourney(
        self,
        ctx: Interaction,
        total_slot:  app_commands.Range[int, 2, 500],
        mentions: app_commands.Range[int, 0, 11],
        slot_per_group: app_commands.Range[int, 2, 25],
        event_name: str = "New Tournament"
    ):
        await ctx.response.defer(ephemeral=True)

        if len(ctx.guild.categories) > 50:
            await ctx.followup.send(
                embed=EmbedBuilder.warning(self.utils.constants.Messages.TOO_MANY_CATEGORIES),
                ephemeral=True
            )
            return
        
        if len(ctx.guild.channels) > 500:
            await ctx.followup.send(
                embed=EmbedBuilder.warning(self.utils.constants.Messages.TOO_MANY_CHANNELS),
                ephemeral=True
            )
            return
        
        if len(event_name) > 30:
            await ctx.followup.send(
                embed=EmbedBuilder.warning("Event name is too long. Please keep it under 30 characters."),
                ephemeral=True
            )
            return


        _event_prefix = self.bot.helper.get_event_prefix(event_name)
        
        _category = await ctx.guild.create_category(
            name=event_name,
            reason=f"Created by {ctx.user} for tournament setup",
            overwrites={
                ctx.guild.default_role: self.utils.permissions.MEMBER_LOCKED_PERMS,
                ctx.guild.me: self.utils.permissions.BOT_PERMS,
                ctx.user: self.utils.permissions.BOT_PERMS
            }
        )

        _channel_names: dict[str, TextChannel] = {
            "info" : None, "updates": None, "how-to-register": None, "register-here": None, "confirmed-teams": None, "groups": None, "queries": None
        }


        for channel_name in _channel_names.keys():
            try:
                _channel = await ctx.guild.create_text_channel(
                    name=f"{_event_prefix}-{channel_name}",
                    category=_category,
                    overwrites={
                        ctx.guild.default_role: self.utils.permissions.MEMBER_LOCKED_PERMS,
                        ctx.guild.me: self.utils.permissions.BOT_PERMS,
                        ctx.user: self.utils.permissions.BOT_PERMS
                    },
                    reason=f"Created by {ctx.user} for tournament setup"
                )
                _channel_names[channel_name] = _channel
                await self.bot.sleep(0.5)  # Avoid rate limits

            except Exception as e:
                await ctx.followup.send(
                    embed=EmbedBuilder.alert(f"Failed to create {channel_name} channel.\nCould you please check my permissions? {str(e)}"),
                    ephemeral=True
                )
                return

        try:

            tournament = TourneyModel(
                guild=ctx.guild.id,
                name=event_name,
                tslot=total_slot,
                mentions=mentions,
                spg=slot_per_group,
                rch= _channel_names.get("register-here").id,
                cch= _channel_names.get("confirmed-teams").id,
                gch= _channel_names.get("groups").id,
                #crole=0,  # Will be set later when confirm role is created
            )
            await tournament.save()  # Save the tournament model to the database
            
            how_to_register_content = ""
            for i in range(1, mentions+1): how_to_register_content+=f"\nPLAYER {i}:\nUID: PLAYER ID\nIGN : PLAYER NAME\n"
            how_to_register_channel = _channel_names["how-to-register"]

            how_to_register_message = await how_to_register_channel.send(
                "**REGISTRATION FORM**", 
                embed= EmbedBuilder(
                    color=self.bot.color.cyan, 
                    description=f"**TEAM NAME : YOUR TEAM NAME\n{how_to_register_content}\nSUBSTITUTE PLAYER IF EXIST\nMENTION YOUR {mentions} TEAMMATES**"
                )

            ) if how_to_register_channel else None
            await self.bot.sleep(0.5)  # Avoid rate limits
            await how_to_register_message.pin(reason="Pinned by tournament setup command for reference.")
            await self.bot.sleep(0.5)  # Avoid rate limits
            await how_to_register_message.add_reaction(self.bot.emoji.tick)


            await ctx.followup.send(
                embed=EmbedBuilder.success(f"Successfully created tournament **{event_name}** with {total_slot} slots and {slot_per_group} slots per group."),
                ephemeral=True
            )
            
            # Send initial setup message in the updates channel
            updates_channel = _channel_names["updates"]
            if updates_channel:
                embed=EmbedBuilder(
                    f"**{event_name}** Registration is now open! ",
                    description= f"Total Slot is : {total_slot}\n"
                                f"If you want to register your team, please use the registration form <#{_channel_names.get('how-to-register').id}>.\n fill it and send while mentioning your {mentions} teammates in the <#{_channel_names.get('register-here').id}> channel.",
                    color=self.bot.base_color
                )
                if ctx.guild.icon:
                    embed.set_thumbnail(url=ctx.guild.icon.url)

                await updates_channel.send(
                    embed=embed,
                    allowed_mentions=discord.AllowedMentions.none()
                )

        except Exception as e:
            await ctx.followup.send(
                embed=EmbedBuilder.warning(f"Failed to create tournament: {str(e)}"),
                ephemeral=True
            )
            logger.error(f"Error during tournament setup: {traceback.format_exc()}")
            return

            
    @app_commands.command(name="pause", description="Pause the tournament registration")
    @app_commands.guild_only()
    @checks.tourney_mod(True)
    async def pause_tournament(self, ctx: Interaction, reg_channel: TextChannel):
        await ctx.response.defer(ephemeral=True)

        _tourney = await self.model.get(reg_channel.id)
        if not _tourney:
            await ctx.followup.send(
                embed=EmbedBuilder.warning(self.utils.constants.Messages.NO_ACTIVE_TOURNAMENT),
                ephemeral=True
            )
            return
        
        reg_channel.set_permissions(
            ctx.guild.default_role,
            overwrite=self.utils.permissions.MEMBER_LOCKED_PERMS
        )
        await self.bot.sleep()

        await self.utils.log(ctx.guild, f"Tournament registration for **{_tourney.name}** has been paused by {ctx.user.mention}.", "info")
        await self.bot.sleep()

        await reg_channel.send(
            embed=EmbedBuilder.success(self.utils.constants.Messages.TOURNEY_PAUSED),
            allowed_mentions=discord.AllowedMentions.none()
        )
        
        _tourney.status = False  # Set tournament status to inactive
        await _tourney.save()  # Save changes to database
        await ctx.followup.send(
            embed=EmbedBuilder.success("Tournament registration has been paused."),
            ephemeral=True
        )



    @app_commands.command(name="start", description="Start the tournament registration")
    @app_commands.guild_only()
    @checks.tourney_mod(True)
    async def start_tournament(self, ctx: Interaction, reg_channel: TextChannel):
        await ctx.response.defer(ephemeral=True)

        _tourney = await self.model.get(reg_channel.id)
        if not _tourney:
            await ctx.followup.send(
                embed=EmbedBuilder.warning(self.utils.constants.Messages.NO_ACTIVE_TOURNAMENT),
                ephemeral=True
            )
            return
        
        reg_channel.set_permissions(
            ctx.guild.default_role,
            overwrite=self.utils.permissions.MEMBER_UNLOCKED_PERMS
        )

        await self.utils.log(ctx.guild, f"Tournament registration for **{_tourney.name}** has been resumed by {ctx.user.mention}.", "info")
        await self.bot.sleep()

        await reg_channel.send(
            embed=EmbedBuilder.success(self.utils.constants.Messages.TOURNEY_RESUMED),
            allowed_mentions=discord.AllowedMentions.none()
        )

        _tourney.status = True  # Set tournament status to active
        await _tourney.save()  # Save changes to database
        await ctx.followup.send(
            embed=EmbedBuilder.success("Tournament registration has been started."),
            ephemeral=True
        )

    @app_commands.command(name="delete", description="Delete a tournament and all associated channels")
    @app_commands.guild_only()
    @app_commands.describe(
        reg_channel="The registration channel of the tournament to delete",
        confirm="Type 'DELETE' to confirm deletion"
    )
    @checks.tourney_mod(True)
    async def delete_tournament(self, ctx: Interaction, reg_channel: TextChannel, confirm: str):
        await ctx.response.defer(ephemeral=True)

        if confirm.upper() != "DELETE":
            await ctx.followup.send(
                embed=EmbedBuilder.warning("Please type 'DELETE' to confirm tournament deletion."),
                ephemeral=True
            )
            return
        
        _deleted = await self.model.delete(reg_channel.id)
        if not _deleted:
            await ctx.followup.send(
                embed=EmbedBuilder.warning("No active tournament found for the specified registration channel."),
                ephemeral=True
            )
            return

        await ctx.followup.send(
            embed=EmbedBuilder.success(f"Successfully deleted tournament **{_deleted}** and all associated channels."),
            ephemeral=True
        )


    @app_commands.command(name="info", description="Get information about the current tournament")
    @app_commands.guild_only()
    @checks.tourney_mod(True)
    async def tournament_info(self, ctx: Interaction, reg_channel: TextChannel):
        await ctx.response.defer(ephemeral=True)

        _tourney = await self.model.get(reg_channel.id)
        if not _tourney:
            await ctx.followup.send(
                embed=EmbedBuilder.warning(self.utils.constants.Messages.NO_ACTIVE_TOURNAMENT),
                ephemeral=True
            )
            return
        
        embed = EmbedBuilder(
            title=f"{_tourney.name}",
            description=f"**Guild ID:** {ctx.guild.id}\n"
                        f"**Status:** {'Active' if _tourney.status else 'Inactive'}\n"
                        f"**Total Slots:** {_tourney.total_slots}\n"
                        f"**Registered Teams:** {_tourney.team_count}\n"
                        f"**Slots per Group:** {_tourney.slot_per_group}\n"
                        f"**Current Group:** {_tourney.current_group}\n"
                        f"**Created At:** <t:{_tourney.created_at}:F>",
            color=self.bot.color.cyan
        )

        await ctx.followup.send(embed=embed, ephemeral=True)


    @app_commands.command(name="list", description="List all active tournaments in the server")
    @app_commands.guild_only()
    @checks.tourney_mod(True)
    async def list_tournaments(self, ctx: Interaction):
        await ctx.response.defer(ephemeral=True)

        _tournaments = await self.model.get_by_guild(ctx.guild.id)

        if not _tournaments:
            await ctx.followup.send(
                embed=EmbedBuilder.warning("No active tournaments found in this server."),
                ephemeral=True
            )
            return
        _embeds : list[EmbedBuilder] = []
        

        for _tourney in _tournaments:
            _embeds.append( EmbedBuilder(
                title=_tourney.name,
                description=f"**Guild ID:** {ctx.guild.id}\n"
                            f"**Status:** {'Active' if _tourney.status else 'Inactive'}\n"
                            f"**Total Slots:** {_tourney.total_slots}\n"
                            f"**Registered Teams:** {_tourney.team_count}\n"
                            f"**Slots per Group:** {_tourney.slot_per_group}\n"
                            f"**Current Group:** {_tourney.current_group}\n"
                            f"**Created At:** <t:{_tourney.created_at}:F>",
                color=self.bot.color.cyan
            ))

        paginator = EmbedPaginator(pages=_embeds, author=ctx.user, delete_on_timeout=True)
        await paginator.start(await self.bot.get_context(ctx))
