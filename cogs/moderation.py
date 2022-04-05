import discord
from discord.ext import commands
cmd = commands


class Moderation(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.counter = 0

	#start commands






	@commands.command()
	@commands.has_permissions(kick_members=True)
	async def kick(self, ctx, member: discord.Member, reason=None):
		if reason == None:
			reason = f"{member} kicked by {ctx.author}"

		if ctx.author.top_role > member.top_role:
			return await ctx.guild.kick(member, reason=reason)
			return await ctx.send(f"{member} kicked", delete_after=5)

		if ctx.author.top_role < member.top_role:
			return await ctx.send("You don't have enough permission", delete_after=5)


	@commands.command()
	@commands.has_permissions(ban_members=True)
	async def ban(self, ctx, member: discord.Member, reason=None):
		if reason == None:
			reason = f"{member} banned by {ctx.author}"

		if ctx.author.top_role > member.top_role:
			return await ctx.guild.ban(member, reason=reason)
			return await ctx.send(f"{member} banned")

		if ctx.author.top_role < member.top_role:
			return await ctx.send("You don't have enough permission", delete_after=5)
























def setup(bot):
    bot.add_cog(Moderation(bot))