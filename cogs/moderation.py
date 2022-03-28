import discord
from discord.ext import commands


class Moderation(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.counter = 0

	#start commands


	@commands.command()
	@commands.has_permissions(administrator=True)
	async def ra_role(self, ctx, role:discord.Role):
		for member in ctx.guild.members:
			if member.role > ctx.author.role:
				await ctx.send("You can't do this for some people")
			if member.role < ctx.author.role:
				if member.has_roles(role):
					await member.remove_roles(role)
			if bot.role < member.role:
				await ctx.send("I do not have enough permission")
					

			








def setup(bot):
    bot.add_cog(Moderation(bot))