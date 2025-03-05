import asyncio
from discord import TextChannel
from discord.ext import commands
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.bot import Spruce


class EventScrim(commands.Cog):
    def __init__(self, bot:Spruce):
        self.bot:Spruce = bot
        self._task = bot.loop.create_task(self.scrim_scheduler())
        

    @commands.Cog.listener()
    async def start_scrim(self, channel:TextChannel):
        """Starts the scrim in the provided channel"""
        await channel.send("Scrim started!!")


    async def scrim_scheduler(self):
        """Scheduler for the scrims"""
        while not self.bot.is_closed():
            print("Scheduler running")
            await asyncio.sleep(10)
            # Do something
  
        