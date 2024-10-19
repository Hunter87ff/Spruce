import datetime
import discord
from discord.ext import tasks, commands
from modules import config

class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot:commands.Bot = bot
        self.update_prime.start()
        self.paylog:discord.TextChannel = self.bot.get_channel(config.paylog)
        # self.primes:list[dict[str:str]] = config.primedbc.find()

    @tasks.loop(seconds=60)
    async def update_prime(self):
        """Delete all the documents from the database where the expiry time is less than the current time. with inbuild features of pymongo"""
        config.primedbc.delete_many({"end_time": {"$lt": datetime.datetime.now()}})

async def setup(bot:commands.Bot):
    await bot.add_cog(Tasks(bot))