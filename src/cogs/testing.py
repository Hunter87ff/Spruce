
from discord.ext import commands
from ext.modals import Tourney
from typing import TYPE_CHECKING
from discord import TextChannel, Message, CategoryChannel

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


class TestingCog(commands.GroupCog, name="test", description="Tester only commands."):
    bot: "Spruce" = None

    def __init__(self, bot : "Spruce"):
        self.bot = bot
        self._tnotfound = "Tournament Not Found"

    
    @commands.command(name="inv")
    async def get_invite(self, ctx: commands.Context):
        self.bot.application.edit(
            tags=["dead"]
        )
        await ctx.send(self.bot.application.custom_install_url)
