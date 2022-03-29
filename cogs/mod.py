import discord
from discord.ext import commands



class Moderation(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.counter = 0

	#start commands



	@commands.command( help="Use to remove a role from everyone")
	@commands.has_permissions(administrator=True)
	async def ra_role(self, ctx, role:discord.Role):
		for member in ctx.guild.members:
			if role in member.roles:
				if member.top_role < ctx.author.top_role:
					await member.remove_roles(role)
					return await ctx.send("Done", delete_after=5)

				if member.top_role > ctx.author.top_role:
					return await ctx.send("You don't have enough permission")



	@commands.command(aliases=['rolea'], pass_context=True,help="Use this command to give role to someone \nExample : &role  @family @hunter")
	async def role_add(ctx, role: discord.Role, user: discord.Member):
		if ctx.author.top_role < role:
			return await ctx.send("you don't have enough permission")
		if ctx.author.top_role > role:
			return await user.add_roles(role)
			return await ctx.send('Done')
		else:
			return await ctx.send("Something went wrong")


			








def setup(bot):
    bot.add_cog(Moderation(bot))