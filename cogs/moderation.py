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
			return await channel.set_permissions(muted, send_messages=False, add_reactions=False)
			return await ctx.channel.purge(limit=1)
			return await ctx.send("Done", delete_after=5)





	@cmd.command(help=" Use this command to lock a channel")
	@commands.has_permissions(manage_channels=True)
	async def lock(self, ctx):
		await ctx.channel.set_permissions(ctx.guild.default_role,send_messages=False, add_reactions=False)
		await ctx.channel.purge(limit=1)
		await ctx.send('**<:vf:947194381172084767> Channel has been locked**', delete_after=5)


	@cmd.command(help=" Use this command to unlock a channel")
	@commands.has_permissions(manage_channels=True)
	async def unlock(self, ctx):
		await ctx.channel.set_permissions(ctx.guild.default_role,send_messages=True, add_reactions=True)
		await ctx.channel.purge(limit=1)
		await ctx.send('**<:vf:947194381172084767> Channel has been unlocked**', delete_after=5)



	@cmd.command(help=" Use this command to hide a channel")
	@commands.has_permissions(manage_channels=True)
	async def hide(self, ctx):
		await ctx.channel.set_permissions(ctx.guild.default_role,view_channel=False)
		await ctx.channel.purge(limit=1)
		await ctx.send('**<:vf:947194381172084767>This channel is hidden from everyone**',delete_after=5)





	@cmd.command(help=" Use this command to unhide a channel")
	@commands.has_permissions(manage_channels=True)
	async def unhide(self, ctx):
		await ctx.channel.set_permissions(ctx.guild.default_role,view_channel=False)
		await ctx.channel.purge(limit=1)
		await ctx.send('**<:vf:947194381172084767>This channel is visible to everyone**',delete_after=5)


	@cmd.command(aliases=['lc'])
	@commands.has_permissions(administrator=True)
	async def lock_category(self, ctx,category: discord.CategoryChannel):
		channels = category.channels
		for channel in channels:
			await channel.set_permissions(ctx.guild.default_role,send_messages=False)
			await ctx.send(f'**<:vf:947194381172084767>Successfully Locked**', delete_after=5)


	@cmd.command(aliases=['ulc'])
	@commands.has_permissions(administrator=True)
	async def unlock_category(self, ctx,category: discord.CategoryChannel):
		channels = category.channels
		for channel in channels:
			await channel.set_permissions(ctx.guild.default_role,send_messages=True)
			await ctx.send(f'**<:vf:947194381172084767>Successfully Unlocked**', delete_after=5)


	@cmd.command(aliases=['hc'])
	@commands.has_permissions(administrator=True)
	async def hide_category(self, ctx,category: discord.CategoryChannel):
		channels = category.channels
		for channel in channels:
			await channel.set_permissions(ctx.guild.default_role,view_channel=False)
			await ctx.send(f'**<:vf:947194381172084767> {channel.name} is Hidden from everyone**', delete_after=5)


	@cmd.command(aliases=['uhc'])
	@commands.has_permissions(administrator=True)
	async def unhide_category(self, ctx,category: discord.CategoryChannel):
		channels = category.channels
		for channel in channels:
			await channel.set_permissions(ctx.guild.default_role,view_channel=True)
			await ctx.send(f'**<:vf:947194381172084767> {channel.name} is Visible to everyone**', delete_after=5)


	@cmd.command(aliases=['cch'])
	@commands.has_permissions(manage_channels=True)
	async def create_channel(ctx,category,name):
		category = await bot.fetch_channel(category)
		await ctx.guild.create_text_channel(name, category=category, reason=f"{ctx.author} created")
		await ctx.send("Done", delete_after=5)




	#clear command
	@cmd.command(help="Use this command to clear messages in a text channel\nExample : &clear 10")
	@commands.has_permissions(manage_messages=True)
	async def clear(self, ctx, amount:int):
		await ctx.channel.purge(limit=amount)
		return await ctx.send(f'**<:vf:947194381172084767> Successfully cleared {amount} messages**',delete_after=5)




	#Mute Command
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