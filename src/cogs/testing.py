
import discord
from discord.ext import commands
from ext.modals import Tourney
from typing import TYPE_CHECKING
from discord import TextChannel, Message, CategoryChannel
from core.abstract import Cog

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

class BaseRound:
    def __init__(self) -> None:
        pass
        

class TestingCog(Cog):
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


    @commands.command("members")
    async def get_members(self, ctx: commands.Context, message_id : str):
        message = await ctx.fetch_message(int(message_id))
        if not message:
            return await ctx.send("Message not found.")

        members : list[discord.Member] = []
        for member in message.mentions:
            member = await self.get_member(ctx.guild, member.id)
            print(type(member))
            if isinstance(member, discord.Member):
                members.append(member)

        if not members:
            return await ctx.send("No members found in the message mentions.")
        
        await ctx.send(f"Members found: {', '.join(member.mention for member in members)}")
        