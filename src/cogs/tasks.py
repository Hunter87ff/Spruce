import datetime
import discord
from typing import TYPE_CHECKING
from discord.ext import tasks, commands

if TYPE_CHECKING:
    from modules.bot import Spruce

class TaskCog(commands.Cog):
    def __init__(self, bot: "Spruce"):
        self.bot = bot
        self.update_prime.start()
        self.paylog:discord.TextChannel = self.bot.get_channel(self.bot.config.paylog)
        # self.primes:list[dict[str:str]] = self.bot.config.primedbc.find()

    @tasks.loop(seconds=3600)
    async def update_prime(self):
        """Delete all the documents from the database where the expiry time is less than the current time. with inbuild features of pymongo"""
        self.bot.db.primedbc.delete_many({"end_time": {"$lt": datetime.datetime.now()}})

