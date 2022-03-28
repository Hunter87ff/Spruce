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
			await member.remove_roles(role)
			await ctx.send("Done")
			await member.send(f"**A role named `{role.name}` in the server {ctx.guild.name}**")
					

			








def setup(bot):
    bot.add_cog(Moderation(bot))