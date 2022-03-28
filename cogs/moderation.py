# hunter bot
import discord
from discord.ext import commands


class Moderation(commands.Cog):
	def __init__(self, ctx):
		self.bot = bot
		self.counter = 0

	#start commands


	@commands.command()
	@commands.has_permissions(administrator=True)
	async def remove_role(self, ctx, role:discord.Role):
		for member in ctx.guild.members:
			if role in member.roles:
				await member.remove_roles(role)
				await ctx.send("Done")
				await member.send(f"{role.name} removed in {ctx.guild.name}")


def setup(bot):
    bot.add_cog(TestCog(bot))