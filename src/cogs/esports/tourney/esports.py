"""
Tournament Management System for Discord Esports
A comprehensive module for managing esports tournaments in Discord servers.

:author: hunter87
:copyright: (c) 2022-present hunter87.dev@gmail.com
:license: GPL-3, see LICENSE for more details.
"""


import os
import logging
import aiofiles
from click import INT
import discord
import traceback
from typing import TYPE_CHECKING
from cogs.esports.ext.utils import TourneyUtils
from core.abstract import EmbedPaginator, GroupCog, Cog
from models import TeamModel
from models.tourney import TourneyModel

from ext import ( checks, EmbedBuilder)
from events.esports import handle_tourney_registration
from events.esports.tourney.interaction import slot_manager_interaction
from discord import Enum, File, Interaction, Member, TextChannel, app_commands


if TYPE_CHECKING:
    from core.bot import Spruce

logger = logging.getLogger(__name__)


class InteractionIds:
    CANCEL_SLOT = "v1_tourney_slot_remove"
    CHECK_SLOT = "v1_tourney_slot_check"
    RENAME_SLOT = "v1_tourney_slot_rename"
    TRANSFER_SLOT = "v1_tourney_slot_transfer"

    ALL = {
        CANCEL_SLOT,
        CHECK_SLOT,
        RENAME_SLOT,
        TRANSFER_SLOT
    }

class Esports(GroupCog, name="esports", group_name="esports"):
    """
    Tournament Management Cog
    """
    
    # Constants
    MAX_EVENT_PER_GUILD = 5
    MAX_TOTAL_SLOTS = 500
    MAX_SLOTS_PER_GROUP = 25
    MAX_MENTIONS_COUNT = 11
    MAX_EVENT_NAME_LENGTH = 30

    INTERACTION_IDS = InteractionIds
    MANAGER_PREFIXES = {"Cslot", "Mslot", "Tname", "Cancel"}
    model : TourneyModel = TourneyModel
    
    def __init__(self, bot: 'Spruce'):
        TourneyUtils.bot = bot
        self.model.bot = bot
        self.bot: 'Spruce' = bot
        self.utils = TourneyUtils
        self.TOURNEY_LOG_CHANNEL_NAME = f"{self.bot.user.name.lower()}-tourney-log"
        self.HIGHER_ROLE_POSITION = "{role.mention} has a higher role position than me. Please move it below my role and try again."
       
    # App command groups
    app_set = app_commands.Group(name="set", description="Tournament configuration commands")
    app_add = app_commands.Group(name="add", description="Tournament management commands")
    app_remove = app_commands.Group(name="remove", description="Tournament removal commands")
    app_setup = app_commands.Group(name="setup", description="Tournament setup commands")

    

    async def migrate_slot_manager(self, ctx: Interaction):
        _tourney: TourneyModel = await self.model.find_one(mch=ctx.channel.id)

        if not _tourney:
            return
        
        _view = discord.ui.View(timeout=None) 
        _buttons = [
            discord.ui.Button(label="Cancel Slot", style=discord.ButtonStyle.red, custom_id=self.INTERACTION_IDS.CANCEL_SLOT),
            discord.ui.Button(label="Check Slot", style=discord.ButtonStyle.blurple, custom_id=self.INTERACTION_IDS.CHECK_SLOT),
            discord.ui.Button(label="Rename Slot", style=discord.ButtonStyle.green, custom_id=self.INTERACTION_IDS.RENAME_SLOT),
            discord.ui.Button(label="Transfer Slot", style=discord.ButtonStyle.grey, custom_id=self.INTERACTION_IDS.TRANSFER_SLOT),
        ]
        for button in _buttons:
            _view.add_item(button)
        
        _embed = EmbedBuilder(
            title=_tourney.name.upper(),
            description=f"{self.bot.emoji.arow} **Cancel Slot** : to cancel your slot\n"
                        f"{self.bot.emoji.arow} **Check Slot** : to check your slot\n"
                        f"{self.bot.emoji.arow} **Rename Slot** : to rename your slot\n"
                        f"{self.bot.emoji.arow} **Transfer Slot** : to transfer your slot",
            color=self.bot.base_color
        )
        _embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        await ctx.message.edit(embed=_embed, view=_view)



    @app_commands.command(name="create", description="Setup a new tournament")
    @checks.testers_only(True)
    @checks.tourney_mod(True)
    @app_commands.guild_only()
    @app_commands.describe(
        total_slot="Total number of slots available for the tournament (2-500)",
        mentions="Number of players to mention in the registration form (0-11)",
        slot_per_group="Number of slots per group (1-25)",
        event_name="Name of the tournament event (default: 'New Tournament')"
    )
    async def setup_tourney(
        self,
        ctx: Interaction,
        total_slot:  app_commands.Range[int, 2, MAX_TOTAL_SLOTS],
        mentions: app_commands.Range[int, 0, MAX_MENTIONS_COUNT],
        slot_per_group: app_commands.Range[int, 2, MAX_SLOTS_PER_GROUP],
        event_name: app_commands.Range[str, 1, MAX_EVENT_NAME_LENGTH] = "New Tournament"
    ):
        await ctx.response.defer(ephemeral=True)

        if len(ctx.guild.categories) > 50:
            await ctx.followup.send(
                embed=EmbedBuilder.warning(self.utils.constants.Messages.TOO_MANY_CATEGORIES),
                ephemeral=True
            )
            return
        
        if len(ctx.guild.channels) >= 490:
            await ctx.followup.send(
                embed=EmbedBuilder.warning(self.utils.constants.Messages.TOO_MANY_CHANNELS),
                ephemeral=True
            )
            return

        if len(event_name) > self.MAX_EVENT_NAME_LENGTH:
            await ctx.followup.send(
                embed=EmbedBuilder.warning(f"Event name is too long. Please keep it under {self.MAX_EVENT_NAME_LENGTH} characters."),
                ephemeral=True
            )
            return
        
        _all_events = await self.model.get_by_guild(ctx.guild.id)
        if len(_all_events) >= self.MAX_EVENT_PER_GUILD:
            await ctx.followup.send(
                embed=EmbedBuilder.warning(f"Maximum of {self.MAX_EVENT_PER_GUILD} events reached for this guild."),
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
            _confirm_role = await ctx.guild.create_role(
                name=f"{_event_prefix}-confirm",
                color=self.bot.color.random(),
            )

            tournament = TourneyModel(
                guild=ctx.guild.id,
                name=event_name,
                tslot=total_slot,
                mentions=mentions,
                spg=slot_per_group,
                rch= _channel_names.get("register-here").id,
                cch= _channel_names.get("confirmed-teams").id,
                gch= _channel_names.get("groups").id,
                crole=_confirm_role.id,
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

            if how_to_register_message:
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

        await ctx.followup.send(embed=self.utils.tourney_info_embed(_tourney), ephemeral=True)


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
            _embeds.append( self.utils.tourney_info_embed(_tourney) )

        paginator = EmbedPaginator(pages=_embeds, author=ctx.user, delete_on_timeout=True)
        await paginator.start(await self.bot.get_context(ctx))



    @app_commands.command(name="export", description="Export the entire tournament in CSV")
    @app_commands.guild_only()
    @checks.tourney_mod(True)
    @app_commands.checks.cooldown(rate=2, per=60.0, key=lambda i: i.user.id)
    @app_commands.describe(
        reg_channel="The registration channel of the tournament to export"
    )
    async def export_tournament(self, ctx: Interaction, reg_channel: TextChannel):
        await ctx.response.defer(ephemeral=True)

        _tourney = await self.model.get(reg_channel.id)
        
        if not _tourney:
            await ctx.followup.send(
                embed=EmbedBuilder.warning(self.utils.constants.Messages.NO_ACTIVE_TOURNAMENT),
                ephemeral=True
            )
            return

        # Generate CSV data
        event_csv_data = "name, slots, registered, slot per group, reg channel, slot channel, confirm role, duplicate tag filter\n"
        event_csv_data += f"{_tourney.name}, {_tourney.total_slots}, {_tourney.team_count}, {_tourney.slot_per_group}, {reg_channel.id}, {str(_tourney.slot_channel)}, {str(_tourney.confirm_role)}, {str(_tourney.tag_filter)}\n"

        event_csv_data += "Teams:\n"
        event_csv_data += "name, captain, members\n"

        for team in await _tourney.get_teams():
            event_csv_data += f"{team.name}, {str(team.captain)}, {team.members}\n"

        _fp = f"exports/tournament_{_tourney.reg_channel}.csv"
        async with aiofiles.open(_fp, "w") as f:
            await f.write(event_csv_data)

        # Send CSV file
        await ctx.followup.send(
            file=File(fp=_fp, filename=f"tournament_{_tourney.reg_channel}.csv"),
            embed=EmbedBuilder.success(f"Successfully exported tournament **{_tourney.name}**.")
        )
        os.remove(_fp)


    class TourneyStatus(Enum):
        OPEN = 1
        CLOSED = 0


    @app_set.command(name="status", description="set status for a specific tournament")
    @app_commands.guild_only()
    @checks.tourney_mod(interaction=True)
    @app_commands.describe(
        reg_channel="registration channel for the tournament",
        status="current status for the tournament")
    async def change_status(self, ctx: Interaction, reg_channel: TextChannel, status: TourneyStatus):
        await ctx.response.defer(ephemeral=True)

        _tourney = await TourneyModel.get(reg_channel.id)
        if not _tourney:
            return await ctx.followup.send("No tournament found in this channel")

        _tourney.status = bool(status.value)
        await _tourney.save()
        await ctx.followup.send(embed=EmbedBuilder.success(f"Tournament status updated to {status.name}"))


    @app_set.command(name="total_slots", description="Set the total number of slots for the tournament")
    @app_commands.guild_only()
    @checks.tourney_mod(True)
    @app_commands.checks.cooldown(rate=2, per=60.0, key=lambda i: i.user.id)
    @app_commands.describe(
        total_slots="Total number of slots available for the tournament (2-500)"
    )
    async def set_total_slots(
        self,
        ctx: Interaction,
        reg_channel: TextChannel,
        total_slots: app_commands.Range[int, 2, MAX_TOTAL_SLOTS]
    ):
        await ctx.response.defer(ephemeral=True)
        
        _tourney = await self.model.get(reg_channel.id)
        if not _tourney:
            await ctx.followup.send(
                embed=EmbedBuilder.warning(self.utils.constants.Messages.NO_ACTIVE_TOURNAMENT),
                ephemeral=True
            )
            return

        _tourney.total_slots = total_slots
        await _tourney.save()
        
        await ctx.followup.send(
            embed=EmbedBuilder.success(f"Successfully updated total slots to {total_slots} for tournament **{_tourney.name}**."),
            ephemeral=True
        )


    @app_set.command(name="slots_per_group", description="Set the number of slots per group for the tournament")
    @app_commands.guild_only()
    @checks.tourney_mod(True)
    @app_commands.checks.cooldown(rate=2, per=60.0, key=lambda i: i.user.id)
    @app_commands.describe(
        slots_per_group="Number of slots per group (2-25)"
    )
    async def set_slots_per_group(
        self,
        ctx: Interaction,
        reg_channel: TextChannel,
        slots_per_group: app_commands.Range[int, 2, MAX_SLOTS_PER_GROUP]
    ):
        await ctx.response.defer(ephemeral=True)

        _tourney = await self.model.get(reg_channel.id)
        if not _tourney:
            await ctx.followup.send(
                embed=EmbedBuilder.warning(self.utils.constants.Messages.NO_ACTIVE_TOURNAMENT),
                ephemeral=True
            )
            return

        _tourney.slot_per_group = slots_per_group
        await _tourney.save()

        await ctx.followup.send(
            embed=EmbedBuilder.success(f"Successfully updated slots per group to {slots_per_group} for tournament **{_tourney.name}**."),
            ephemeral=True
        )


    @app_set.command(name="event_name", description="Set the name of the tournament event")
    @app_commands.guild_only()
    @checks.tourney_mod(True)
    @app_commands.checks.cooldown(rate=2, per=60.0, key=lambda i: i.user.id)
    @app_commands.describe(
        event_name="Name of the tournament event (default: 'New Tournament')"
    )
    async def set_event_name(
        self,
        ctx: Interaction,
        reg_channel: TextChannel,
        event_name: app_commands.Range[str, 1, MAX_EVENT_NAME_LENGTH]
    ):
        await ctx.response.defer(ephemeral=True)

        _tourney = await self.model.get(reg_channel.id)
        if not _tourney:
            await ctx.followup.send(
                embed=EmbedBuilder.warning(self.utils.constants.Messages.NO_ACTIVE_TOURNAMENT),
                ephemeral=True
            )
            return

        _tourney.name = event_name
        await _tourney.save()

        await ctx.followup.send(
            embed=EmbedBuilder.success(f"Successfully updated event name to '{event_name}' for tournament **{_tourney.name}**."),
            ephemeral=True
        )

    @app_set.command(name="mentions", description="Set the number of players to mention in the registration form")
    @app_commands.guild_only()
    @checks.tourney_mod(True)
    @app_commands.checks.cooldown(rate=2, per=60.0, key=lambda i: i.user.id)
    @app_commands.describe(
        mentions="Number of players to mention in the registration form (0-11)"
    )
    async def set_mentions(
        self,
        ctx: Interaction,
        reg_channel: TextChannel,
        mentions: app_commands.Range[int, 0, MAX_MENTIONS_COUNT]
    ):
        await ctx.response.defer(ephemeral=True)

        _tourney = await self.model.get(reg_channel.id)
        if not _tourney:
            await ctx.followup.send(
                embed=EmbedBuilder.warning(self.utils.constants.Messages.NO_ACTIVE_TOURNAMENT),
                ephemeral=True
            )
            return

        _tourney.mentions = mentions
        await _tourney.save()

        await ctx.followup.send(
            embed=EmbedBuilder.success(f"Successfully updated mentions to {mentions} for tournament **{_tourney.name}**."),
            ephemeral=True
        )


    class DuplicateTagFilter(Enum):
        ENABLE=1
        DISABLE=0

    @app_set.command(name="duplicate_tag_filter", description="Toggle duplicate tag filter")
    @app_commands.guild_only()
    @checks.tourney_mod(True)
    @app_commands.checks.cooldown(rate=2, per=60.0, key=lambda i: i.user.id)
    @app_commands.describe(
        reg_channel="The registration channel of the tournament",
        filter="Whether to enable or disable the duplicate tag filter"
    )
    async def set_duplicate_tag_filter(
        self,
        ctx: Interaction,
        reg_channel: TextChannel,
        filter: DuplicateTagFilter
    ):
        await ctx.response.defer(ephemeral=True)

        _tourney = await self.model.get(reg_channel.id)
        if not _tourney:
            await ctx.followup.send(
                embed=EmbedBuilder.warning(self.utils.constants.Messages.NO_ACTIVE_TOURNAMENT),
                ephemeral=True
            )
            return

        _tourney.tag_filter = bool(filter.value)
        await _tourney.save()

        await ctx.followup.send(
            embed=EmbedBuilder.success(f"Successfully updated duplicate tag filter to {filter.name} for tournament **{_tourney.name}**."),
            ephemeral=True
        )

    @app_set.command(name="confirm_role", description="Set the confirmation role for the tournament")
    @app_commands.guild_only()
    @checks.tourney_mod(True)
    @app_commands.checks.cooldown(rate=2, per=60.0, key=lambda i: i.user.id)
    @app_commands.describe(
        reg_channel ="The registration channel of the tournament",
        role="Role to be used for confirming team registrations")
    async def set_confirm_role(
        self,
        ctx: Interaction,
        reg_channel: TextChannel,
        role: discord.Role
    ):
        await ctx.response.defer(ephemeral=True)
        _tourney = await self.model.get(reg_channel.id)

        if not _tourney:
            await ctx.followup.send(
                embed=EmbedBuilder.warning(self.utils.constants.Messages.NO_ACTIVE_TOURNAMENT),
                ephemeral=True
            )
            return
        
        if role.position >= ctx.guild.me.top_role.position:
            await ctx.followup.send(
                embed=EmbedBuilder.warning(self.HIGHER_ROLE_POSITION),
                ephemeral=True
            )
            return
        
        _tourney.confirm_role = role.id
        await _tourney.save()
        await ctx.followup.send(
            embed=EmbedBuilder.success(f"Successfully set confirmation role to {role.mention} for tournament **{_tourney.name}**."),
            ephemeral=True
        )

    
    @app_set.command(name="group_channel", description="Set the group channel for the tournament")
    @app_commands.guild_only()
    @checks.tourney_mod(True)
    @app_commands.checks.cooldown(rate=2, per=60.0, key=lambda i: i.user.id)
    @app_commands.describe(
        reg_channel="The registration channel of the tournament",
        group_channel="Channel to be used for displaying tournament groups"
    )
    async def set_group_channel(
        self,
        ctx: Interaction,
        reg_channel: TextChannel,
        group_channel: TextChannel
    ):
        await ctx.response.defer(ephemeral=True)
        _tourney = await self.model.get(reg_channel.id)
        if not _tourney:
            await ctx.followup.send(
                embed=EmbedBuilder.warning(self.utils.constants.Messages.NO_ACTIVE_TOURNAMENT),
                ephemeral=True
            )
            return
        
        if group_channel.category and group_channel.category.id != reg_channel.category_id:
            await ctx.followup.send(
                embed=EmbedBuilder.warning("Group channel must be in the same category as the registration channel."),
                ephemeral=True
            )
            return

        _tourney.group_channel = group_channel.id
        await _tourney.save()
        await ctx.followup.send(
            embed=EmbedBuilder.success(f"Successfully set group channel to {group_channel.mention} for tournament **{_tourney.name}**."),
            ephemeral=True
        )

    @app_set.command(name="slot_channel", description="Set the slot manager channel for the tournament")
    @app_commands.guild_only()
    @checks.tourney_mod(True)
    @app_commands.checks.cooldown(rate=2, per=60.0, key=lambda i: i.user.id)
    @app_commands.describe(
        reg_channel="The registration channel of the tournament",
        slot_channel="Channel to be used for managing team slots"
    )
    async def set_slot_channel(
        self,
        ctx: Interaction,
        reg_channel: TextChannel,
        slot_channel: TextChannel
    ):
        await ctx.response.defer(ephemeral=True)
        _tourney = await self.model.get(reg_channel.id)
        if not _tourney:
            await ctx.followup.send(
                embed=EmbedBuilder.warning(self.utils.constants.Messages.NO_ACTIVE_TOURNAMENT),
                ephemeral=True
            )
            return
        
        if slot_channel.category and slot_channel.category.id != reg_channel.category_id:
            await ctx.followup.send(
                embed=EmbedBuilder.warning("Slot channel must be in the same category as the registration channel."),
                ephemeral=True
            )
            return
        
        _tourney.slot_channel = slot_channel.id
        await _tourney.save()
        await ctx.followup.send(
            embed=EmbedBuilder.success(f"Successfully set slot channel to {slot_channel.mention} for tournament **{_tourney.name}**."),
            ephemeral=True
        )

    @app_add.command(name="team", description="Add a team to the tournament")
    @app_commands.guild_only()
    @checks.tourney_mod(True)
    async def add_team(
        self,
        ctx: Interaction,
        reg_channel: TextChannel,
        team_name: str,
        captain: Member
    ):
        await ctx.response.defer(ephemeral=True)
        _tourney = await self.model.get(reg_channel.id)
        if not _tourney:
            await ctx.followup.send(
                embed=EmbedBuilder.warning(self.utils.constants.Messages.NO_ACTIVE_TOURNAMENT),
                ephemeral=True
            )
            return
        
        if not _tourney.status:
            await ctx.followup.send(
                embed=EmbedBuilder.warning("Tournament registration is currently paused. Please resume it before adding teams."),
                ephemeral=True
            )
            return
        
        if _tourney.total_slots <= _tourney.team_count:
            await ctx.followup.send(
                embed=EmbedBuilder.warning("All slots are already filled. Cannot add more teams."),
                ephemeral=True
            )
            return
        
        _slot_channel = ctx.guild.get_channel(_tourney.slot_channel)
        if not _slot_channel:
            await ctx.followup.send(
                embed=EmbedBuilder.warning("Slot channel not found. Please check the tournament configuration."),
                ephemeral=True
            )
            return
        _team = TeamModel(name=team_name, tid=_tourney.reg_channel, capt=captain.id, members={captain.id})
        _embed = self.utils.confirm_message_embed(
            team=_team,
            tourney=_tourney
        )
        try:
            await _tourney.validate_team(_team)
            _confirm_message = await _slot_channel.send(embed=_embed)
            await _confirm_message.add_reaction(self.bot.emoji.tick)
            _team._id = _confirm_message.id  # Set the message ID for the team
            await _tourney.add_team(_team)
            await ctx.followup.send(
                content=f"{_team.name} {captain.mention}",
                embed=EmbedBuilder.success(f"Successfully added team **{team_name}** to tournament **{_tourney.name}**."),
                ephemeral=True
            )

        except Exception as e:
            await ctx.followup.send(
                embed=EmbedBuilder.warning(f"Failed to add team: {str(e)}"),
                ephemeral=True
            )
            await self.utils.log(
                guild=ctx.guild,
                message=f"Failed to add team in tournament **{_tourney.name}**: {str(e)}",
                level="warning"
            )
            return
            

    @app_remove.command(name="team", description="Remove a team from the tournament")
    @app_commands.guild_only()
    @checks.tourney_mod(True)
    async def remove_team(
        self,
        ctx: Interaction,
        reg_channel: TextChannel,
        captain: Member
    ):
        await ctx.response.defer(ephemeral=True)
        _tourney = await self.model.get(reg_channel.id)
        if not _tourney:
            await ctx.followup.send(
                embed=EmbedBuilder.warning(self.utils.constants.Messages.NO_ACTIVE_TOURNAMENT),
                ephemeral=True
            )
            return
        

        _teams = await _tourney.get_team_by_player_id(captain.id)
        if not _teams:
            await ctx.followup.send(
                embed=EmbedBuilder.warning(f"No teams found for {captain.mention} in tournament **{_tourney.name}**."),
                ephemeral=True
            )
            return
        
        _options = []
        for team in _teams:
            _options.append(discord.SelectOption(label=f"{team.name}", value=team._id))

        _view = discord.ui.View(timeout=60.0)
        _select = discord.ui.Select(
            placeholder="Select a team to remove",
            options=_options,
            min_values=1,
            max_values=1
        )
        _view.add_item(_select)

        async def select_callback(interaction: Interaction):
            if interaction.user.id != ctx.user.id:
                await interaction.response.send_message(
                    embed=EmbedBuilder.warning("You are not allowed to remove teams from this tournament."),
                    ephemeral=True
                )
                return
            
            selected_team_id = int(_select.values[0])
            _team = await _tourney.get_team_by_id(selected_team_id)
            if not _team:
                await interaction.response.send_message(
                    embed=EmbedBuilder.warning("Selected team not found."),
                    ephemeral=True
                )
                return
            
            await _tourney.remove_team(_team)
            await interaction.response.send_message(
                embed=EmbedBuilder.success(f"Successfully removed team **{_team.name}** from tournament **{_tourney.name}**."),
                ephemeral=True
            )
            await self.utils.log(
                guild=ctx.guild,
                message=f"Team **{_team.name}** has been removed from tournament **{_tourney.name}** by {ctx.user.mention}.",
                level="info"
            )

        _select.callback = select_callback

        await ctx.followup.send(
            content=f"Please select a team to remove from tournament **{_tourney.name}**:",
            view=_view,
            ephemeral=True
        )


    @app_setup.command(name="group", description="Set up a tournament group")
    @app_commands.guild_only()
    @checks.tourney_mod(True)
    async def setup_group(self, ctx: Interaction, reg_channel: TextChannel):
        await ctx.response.defer(ephemeral=True)

        _tourney = await self.model.get(reg_channel.id)
        if not _tourney:
            await ctx.followup.send(
                embed=EmbedBuilder.warning(self.utils.constants.Messages.NO_ACTIVE_TOURNAMENT),
                ephemeral=True
            )
            return

        # implement Create the group
        await ctx.followup.send(
            embed=EmbedBuilder.warning(f"Not Implemented Yet !! "),
            ephemeral=True
        )


    @Cog.listener()
    async def on_ready(self):
        await self.model.load_all()

    
    @Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        await handle_tourney_registration(self, message)


    @Cog.listener()
    async def on_interaction(self, interaction: Interaction):
            await slot_manager_interaction(self, interaction)