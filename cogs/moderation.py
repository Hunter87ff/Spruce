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
			if m.top_role > ctx.author.top_role:
				await ctx.send("You don't have enough permission")
			elif m.top_role < ctx.author.top_role:
				await m.remove_roles(role)
				await m.send(f"`{role.name}` role is removed in `{ctx.guild.name}`")
				await ctx.send("Done")


			








def setup(bot):
    bot.add_cog(Moderation(bot))