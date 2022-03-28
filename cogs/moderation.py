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
		for m in ctx.guild.members:
			try:
				if m.top_role > ctx.author.top_role:
					await ctx.send("You don't have enough permission")
				if m.top_role < ctx.author.top_role:
					await member.remove_roles(role)
					await ctx.send("Done")
				if bot.top_role < m.top_role:
					await ctx.send("I don't have enough permission")
			except:
				await ctx.send("Something went wrong")
					

			








def setup(bot):
    bot.add_cog(Moderation(bot))