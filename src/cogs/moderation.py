

import discord
from asyncio import sleep
from discord.ext import commands
cmd = commands


class Moderation(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.counter = 0

	#start commands

	@cmd.command(help="to setup muted role perms")
	@commands.cooldown(2, 20, commands.BucketType.user)
	@commands.has_permissions(administrator=True)
	@commands.bot_has_permissions(manage_roles=True, send_messages=True, manage_messages=True)
	async def setup(self, ctx):
		if ctx.author.bot:
			return

		snd = await ctx.send("<a:loading:969894982024568856>**Processing...**")
		muted = discord.utils.get(ctx.guild.roles, name="Muted")

		if muted == None:
			muted = await ctx.guild.create_role(name="Muted", color=0xff0000)


		if muted.position > self.bot.top_role:
			return await snd.edit("`Muted` role is higher than  my top role, I can't manage it")

		overwrite = ctx.channel.overwrites_for(muted)
		overwrite.update(send_messages=False, add_reactions=False, connect=False, speak=False)
		

		for channel in ctx.guild.channels:
			await channel.set_permissions(muted, overwrite=overwrite)
			
		await snd.edit(content=f'**<:vf:947194381172084767>Setuped Successfully**')




	@cmd.command(help=" Use this command to lock a channel")
	@commands.cooldown(2, 20, commands.BucketType.user)
	@commands.has_permissions(manage_channels=True)
	@commands.bot_has_permissions(manage_roles=True, send_messages=True, manage_messages=True)
	async def lock(self, ctx, role: discord.Role=None):
		if ctx.author.bot:
			return

		if role == None:
			role = ctx.guild.default_role
		overwrite = ctx.channel.overwrites_for(role)
		overwrite.update(send_messages=False, add_reactions=False)
		await ctx.channel.set_permissions(role, overwrite=overwrite)
		await ctx.channel.purge(limit=1)
		return await ctx.send('**<:vf:947194381172084767> Channel has been locked**', delete_after=5)


	@cmd.command(help=" Use this command to unlock a channel")
	@commands.cooldown(2, 20, commands.BucketType.user)
	@commands.has_permissions(manage_channels=True)
	@commands.bot_has_permissions(manage_roles=True, send_messages=True, manage_messages=True)
	async def unlock(self, ctx, role: discord.Role=None):
		if ctx.author.bot:
			return

		if role == None:
			role = ctx.guild.default_role
		overwrite = ctx.channel.overwrites_for(role)
		overwrite.update(send_messages=True, add_reactions=True)
		await ctx.channel.set_permissions(role, overwrite=overwrite)
		await ctx.channel.purge(limit=1)
		return await ctx.send('**<:vf:947194381172084767> Channel has been unlocked**', delete_after=5)



	@cmd.command(help=" Use this command to hide a channel")
	@commands.has_permissions(manage_channels=True)
	@commands.bot_has_permissions(manage_roles=True, send_messages=True, manage_messages=True)
	async def hide(self, ctx, role: discord.Role=None):
		if ctx.author.bot:
			return

		if role == None:
			role = ctx.guild.default_role
		overwrite = ctx.channel.overwrites_for(role)
		overwrite.update(view_channel=False)
		await ctx.channel.set_permissions(role, overwrite=overwrite)
		await ctx.channel.purge(limit=1)
		return await ctx.send('**<:vf:947194381172084767>This channel is hidden from everyone**',delete_after=5)





	@cmd.command(help=" Use this command to unhide a channel")
	@commands.has_permissions(manage_channels=True)
	@commands.bot_has_permissions(manage_roles=True, send_messages=True, manage_messages=True)
	async def unhide(self, ctx, role:discord.Role=None):
		if ctx.author.bot:
			return

		if role == None:
			role = ctx.guild.default_role
		overwrite = ctx.channel.overwrites_for(role)
		overwrite.update(view_channel=True)
		await ctx.channel.set_permissions(role, overwrite=overwrite)
		await ctx.channel.purge(limit=1)
		return await ctx.send('**<:vf:947194381172084767>This channel is visible to everyone**',delete_after=5)


	@cmd.command(aliases=['lc'])
	@commands.has_permissions(administrator=True)
	@commands.bot_has_permissions(manage_roles=True, send_messages=True, manage_messages=True)
	async def lock_category(self, ctx,category: discord.CategoryChannel, role:discord.Role=None):
		if ctx.author.bot:
			return

		if role == None:
			role = ctx.guild.default_role

		channels = category.channels
		for channel in channels:
			overwrite = channel.overwrites_for(role)
			overwrite.update(send_messages=False,add_reactions=False)
			await ctx.channel.set_permissions(role, overwrite=overwrite)
			await ctx.send(f'**<:vf:947194381172084767>Successfully Locked**', delete_after=5)
			await sleep(1)


	@cmd.command(aliases=['ulc'])
	@commands.has_permissions(administrator=True)
	@commands.bot_has_permissions(manage_roles=True, send_messages=True, manage_messages=True)
	async def unlock_category(self, ctx,category: discord.CategoryChannel, role:discord.Role=None):
		if ctx.author.bot:
			return

		if role == None:
			role = ctx.guild.default_role

		channels = category.channels
		for channel in channels:
			overwrite = channel.overwrites_for(role)
			overwrite.update(send_messages=True,add_reactions=True)
			await ctx.channel.set_permissions(role, overwrite=overwrite)
			await ctx.send(f'**<:vf:947194381172084767>Successfully Unlocked**', delete_after=5)
			await sleep(1)


	@cmd.command(aliases=['hc'])
	@commands.has_permissions(administrator=True)
	@commands.bot_has_permissions(manage_roles=True, send_messages=True, manage_messages=True)
	async def hide_category(self, ctx,category: discord.CategoryChannel, role:discord.Role=None):
		if ctx.author.bot:
			return

		if role == None:
			role = ctx.guild.default_role

		channels = category.channels
		for channel in channels:
			overwrite = channel.overwrites_for(role)
			overwrite.update(view_channel=False)
			await ctx.channel.set_permissions(role, overwrite=overwrite)
			await ctx.send(f'**<:vf:947194381172084767> {channel.mention} is Hidden from {role.name}**', delete_after=5)
			await sleep(1)


	@cmd.command(aliases=['uhc'])
	@commands.has_permissions(administrator=True)
	@commands.bot_has_permissions(manage_channels=True)
	async def unhide_category(self, ctx,category: discord.CategoryChannel, role :discord.Role = None):
		if ctx.author.bot:
			return

		if role == None:
			role = ctx.guild.default_role

		channels = category.channels
		for channel in channels:
			overwrite = channel.overwrites_for(role)
			overwrite.update(view_channel=True)
			await ctx.channel.set_permissions(role, overwrite=overwrite)
			await ctx.send(f'**<:vf:947194381172084767> {channel.mention} is Visible to {role.name}**', delete_after=5)





	#clear command
	@cmd.command(help="Use this command to clear messages in a text channel\nExample : &clear 10")
	@commands.has_permissions(manage_messages=True)
	@commands.bot_has_permissions(manage_messages=True, send_messages=True)
	@commands.cooldown(2, 20, commands.BucketType.user)
	async def clear(self, ctx, amount:int):
		if ctx.author.bot:
			return
		if amount == None:
			amount = 10

		await ctx.channel.purge(limit=amount)
		return await ctx.send(f'**<:vf:947194381172084767> Successfully cleared {amount} messages**',delete_after=5)




	#Mute Command
	@cmd.command(help="Make sure you've created a role named 'Muted' and then run the command '&setup' ")
	@commands.has_permissions(manage_roles=True, manage_messages=True, mute_members=True)
	@commands.bot_has_permissions(manage_roles=True, manage_messages=True)
	async def mute(self, ctx, member: discord.Member,*,reason=None):
		if ctx.author.bot:
			return

		muted = discord.utils.get(ctx.guild.roles, name="Muted")
		if muted == None:
			muted = await ctx.guild.create_role(name="Muted", color=0xff0000)

		if reason == None:
			reason = f"{member} Muted By {ctx.author}"

		if muted.position > self.bot.top_role:
			return await ctx.reply("`Muted` role is higher than  my top role, I can't manage it")

		if member == ctx.author:
			return await ctx.send("**You cant mute your self**", delete_after=5)

		if ctx.author.top_role < member.top_role:
			return await ctx.send("**You can't Mute Him**", delete_after=5)

		if self.bot.user.top_role < member.top_role:
			return await ctx.send("**I can't Mute Him**", delete_after=5)

		else:
			await member.add_roles(muted, reason=reason)
			await ctx.message.delete()
			return await ctx.send(f"{member} Muted", delete_after=5)






	@cmd.command()
	@commands.has_permissions(administrator=True)
	@commands.bot_has_permissions(manage_roles=True)
	async def unmute(self, ctx, member: discord.Member,*,reason=None):
		muted = discord.utils.get(ctx.guild.roles, name="Muted")
		if ctx.author.bot:
			return 

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
	@commands.bot_has_permissions(kick_members=True)
	async def kick(self, ctx, member: discord.Member, reason=None):
		if ctx.author.bot:
			return

		if reason == None:
			reason = f"{member} kicked by {ctx.author}"

		if ctx.author.top_role < member.top_role:
			return await ctx.send("You don't have enough permission", delete_after=5)

		elif member == ctx.author:
			return await ctx.send("**You can't kick your self**", delete_after=5)

		elif ctx.guild.me.top_role < member.top_role:
			return await ctx.send("**I can't kick him**", delete_after=5)

		else:
			return await ctx.guild.kick(member, reason=reason)
			return await ctx.send(f"{member} kicked", delete_after=5)


	@commands.command()
	@commands.bot_has_permissions(ban_members=True)
	@commands.has_permissions(ban_members=True)
	async def ban(self, ctx, member: discord.Member, reason=None):
		if ctx.author.bot:
			return

		if reason == None:
			reason = f"{member} banned by {ctx.author}"

		if ctx.author.top_role < member.top_role:
			return await ctx.send("You don't have enough permission", delete_after=5)

		elif member == ctx.author:
			return await ctx.send("**You can't ban your self**", delete_after=5)

		elif ctx.guild.me.top_role < member.top_role:
			return await ctx.send("**I can't ban him**", delete_after=5)

		else:
			return await ctx.guild.ban(member, reason=reason)
			return await ctx.send(f"{member} banned", delete_after=5)




async def setup(bot):
    await bot.add_cog(Moderation(bot))
