from __future__ import annotations
import re
from typing import TYPE_CHECKING, Literal
from ext import EmbedBuilder, constants
from discord import  Message, utils, PermissionOverwrite


if TYPE_CHECKING:
    from core.bot import Spruce
    from models import TourneyModel
    from models import TeamModel
    from discord import Guild, TextChannel


class PermsOverwrite:
    BOT_PERMS = PermissionOverwrite(
        read_messages=True,
        send_messages=True,
        embed_links=True,
        attach_files=True,
        read_message_history=True,
        external_emojis=True,
        add_reactions=True
    )

    MEMBER_LOCKED_PERMS = PermissionOverwrite(
        read_messages=True,
        send_messages=False,
        read_message_history=True,
        create_public_threads=False,
        create_private_threads=False,
        add_reactions=False,
        external_emojis=False,
    )

    MEMBER_UNLOCKED_PERMS = PermissionOverwrite(
        read_messages=True,
        send_messages=True,
        read_message_history=True,
    )


class BaseEsportsUtils:
    bot: "Spruce" = None

    def __init__(self, bot: "Spruce") -> None:
        BaseEsportsUtils.bot = bot


    @classmethod
    def parse_team_name(cls, message: Message, strict: bool = False) -> str | None:
        content = message.content.lower()
        teamname = re.search(r"team.*", content)
        if teamname is None:
            return f"{message.author}'s team"
        teamname = re.sub(r"<@*#*!*&*\d+>|team|name|[^\w\s]", "", teamname.group()).strip()
        if strict and not teamname:
            return None
        teamname = teamname if teamname else f"{message.author}'s team"
        return teamname.lower().strip()[0:20]




class TourneyUtils(BaseEsportsUtils):
    bot : "Spruce" = None
    log_channel_cache : dict[int, int] = {}
    permissions = PermsOverwrite
    constants = constants

    def __init__(self, bot: "Spruce") -> None:
        super().__init__(bot)
        self.bot = bot


    @classmethod
    async def log(cls, guild : "Guild", message: str, level: Literal["info", "warning", "error"]= "info"):
        if cls.bot is None:
            return
        
        _color  = {
            "info": cls.bot.color.cyan,
            "warning": cls.bot.color.yellow,
            "error": cls.bot.color.red
        }

        log_channel: "TextChannel" = guild.get_channel(cls.log_channel_cache.get(guild.id)) 

        if not log_channel:
            log_channel = utils.get(guild.text_channels, name=cls.bot.config.LOG_CHANNEL_NAME)

        if log_channel is None:
            return
        
        cls.log_channel_cache[guild.id] = log_channel.id

        embed = EmbedBuilder(
            title=f"Tournament Log - {level.capitalize()}",
            description=message,
            color=_color.get(level, cls.bot.color.green)
        )

        await log_channel.send(embed=embed)



    @classmethod
    def tourney_info_embed(cls, tournament: "TourneyModel") -> EmbedBuilder: 
        embed = EmbedBuilder(
            title=f"{tournament.name.upper()}",
            description=f"Details for tournament in {tournament.guild_id}",
            color=cls.bot.color.blue,
            short_desc=f"ID: {tournament.reg_channel}",
            emoji="🏆"
        )
        embed.add_field(name="Status", value="`Active`" if tournament.status else "`Inactive`")
        embed.add_field(name="Registered Teams", value=tournament.team_count)
        embed.add_field(name="Total Slots", value=tournament.total_slots)
        embed.add_field(name="Mentions Required", value=tournament.mentions)
        embed.add_field(name="Slots per Group", value=tournament.slot_per_group)
        embed.add_field(name="Registration Channel", value=f"<#{tournament.reg_channel}>")
        embed.add_field(name="Confirm Channel", value=f"<#{tournament.slot_channel or 45245245}>")
        embed.add_field(name="Group Channel", value=f"<#{tournament.group_channel or 45245245}>")
        embed.add_field(name="Slot Manager Channel", value=f"<#{tournament.slot_manager or 45245245}>")
        embed.add_field(name="Confirmation Role", value=f"<@&{tournament.confirm_role or 45245245}>")
        embed.add_field(name="Created At", value=f"<t:{tournament.created_at}:R>")
        return embed


    @classmethod
    def confirm_message_embed(cls, team: "TeamModel", tourney: "TourneyModel") -> EmbedBuilder:
        _guild = cls.bot.get_guild(tourney.guild_id)
        embed = EmbedBuilder(
            color=cls.bot.color.cyan, 
            description=f"**{tourney.team_count+1}) TEAM NAME: {team.name.upper()}**"
            f"\n**Players: **{', '.join([f'<@{member}>' for member in team.members or [team.captain]])}\n\n"
        )
        embed.set_author(name=_guild.name, icon_url=_guild.icon if _guild.icon else None)
        embed.timestamp = utils.utcnow()
        return embed
