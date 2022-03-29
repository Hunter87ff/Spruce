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
				return await ctx.send("You don't have enough permission")
			elif m.top_role < ctx.author.top_role:
				return await m.remove_roles(role)
				return await m.send(f"`{role.name}` role is removed in `{ctx.guild.name}`")
				return await ctx.send("Done")
			else:
				return await ctx.send("Something went wrong")

				
'''
	@commands.command(aliases=['rolea'], pass_context=True,help="Use this command to give role to someone \nExample : &role  @family @hunter")
	async def role_add(ctx, role: discord.Role, user: discord.Member):
		if ctx.author.top_role < role:
			return await ctx.send("you don't have enough permission")
		if ctx.author.top_role > role:
			return await user.add_roles(role)
		else:
			return await ctx.send("Something went wrong")

'''
			








def setup(bot):
    bot.add_cog(Moderation(bot))