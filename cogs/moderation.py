import discord
from discord.ext import commands
cmd = commands


class Moderation(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.counter = 0

	#start commands

	@cmd.command(help="to setup muted role perms")
	@commands.has_permissions(administrator=True)
	async def setup(self, ctx):
		muted = discord.utils.get(ctx.guild.roles, name="Muted")
		for channel in ctx.guild.channels:
			await channel.set_permissions(muted, send_messages=False, add_reactions=False)
			await ctx.channel.purge(limit=1)
			await ctx.send("Done", delete_after=5)





	@cmd.command(help="Make sure you've created a role named 'Muted' and then run the command '&setup' ")
	@commands.has_permissions(administrator=True)
	async def mute(self, ctx, member: discord.Member,*,reason=None):
		muted = discord.utils.get(ctx.guild.roles, name="Muted")
		if reason == None:
			reason = f"{member} Muted By {ctx.author}"

		if ctx.author.top_role < member.top_role:
			return await ctx.send("You can't Mute Him", delete_after=5)

		if self.bot.top_role < member.top_role:
			return await ctx.send(f"I can't Mute Him", delete_after=5)

		else:
			return await member.add_roles(muted, reason=reason)
			return await ctx.channel.purge(limit=1)
			return await ctx.send(f"{member} Muted", delete_after=5)






	@cmd.command()
	@commands.has_permissions(administrator=True)
	async def unmute(self, ctx, member: discord.Member,*,reason=None):
		muted = discord.utils.get(ctx.guild.roles, name="Muted")
		if reason == None:
			reason = f"{member} Unmuted By {ctx.author}"

		if ctx.author.top_role < member.top_role:
			return await ctx.send("You can't Mute Him", delete_after=5)

		if self.bot.top_role < member.top_role:
			return await ctx.send("I can't Mute Him", delete_after=5)

		else:
			return await member.remove_roles(muted, reason=reason)
			return await ctx.send(f"{member} Unmuted", delete_after=5)


	









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