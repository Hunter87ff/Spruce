import discord
from discord.ext import commands


class Utility(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.counter = 0




	

















def setup(bot):
	bot.add_cog(Utility(bot))