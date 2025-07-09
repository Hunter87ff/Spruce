import asyncio
from discord.ext import commands
from ext import checks
from ext.modals import Tourney
from typing import TYPE_CHECKING
from ext import color
from discord import Embed, TextChannel, Member, Message, app_commands, Interaction, utils, Guild, CategoryChannel

if TYPE_CHECKING:
    from core.bot import Spruce



class GroupConfig:
    def __init__(self, current_group:int, messages:list[Message], total_messages:int, event:Tourney, group_channel:TextChannel, group_category:CategoryChannel=None):
        self.current_group = current_group
        self.messages = messages
        self.total_messages = total_messages
        self.event = event
        self.group_channel = group_channel
        self.group_category = group_category


class TestTourney(commands.GroupCog, name="test_tourney", description="Test Tourney Commands"):
    bot: "Spruce" = None

    def __init__(self, bot : "Spruce"):
        self.bot = bot
        self._tnotfound = "Tournament Not Found"


    async def log(self, guild:Guild, message:str, color:int=color.cyan):
        channel = utils.get(guild.text_channels, name=self.bot.config.LOG_CHANNEL_NAME)
        if not channel:
            return 
        
        embed =  Embed(description=message, color=color)
        embed.set_author(name=guild.me.name, icon_url=guild.me.avatar)
        await channel.send(embed=embed)
