"""
MIT License

Copyright (c) 2022 Spruce

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""


import discord
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
	async def setup(self, ctx):
		muted = discord.utils.get(ctx.guild.roles, name="Muted")
		for channel in ctx.guild.channels:
			return await channel.set_permissions(muted, send_messages=False, add_reactions=False)
			return await ctx.channel.purge(limit=1)
			return await ctx.send("Done", delete_after=5)





	@cmd.command(help=" Use this command to lock a channel")
	@commands.cooldown(2, 20, commands.BucketType.user)
	@commands.has_permissions(manage_channels=True)
	async def lock(self, ctx):
		await ctx.channel.set_permissions(ctx.guild.default_role,send_messages=False, add_reactions=False)
		await ctx.channel.purge(limit=1)
		await ctx.send('**<:vf:947194381172084767> Channel has been locked**', delete_after=5)


	@cmd.command(help=" Use this command to unlock a channel")
	@commands.cooldown(2, 20, commands.BucketType.user)
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
			await channel.set_permissions(ctx.guild.default_role,send_messages=False,add_reactions=False)
			await ctx.send(f'**<:vf:947194381172084767>Successfully Locked**', delete_after=5)


	@cmd.command(aliases=['ulc'])
	@commands.has_permissions(administrator=True)
	async def unlock_category(self, ctx,category: discord.CategoryChannel):
		channels = category.channels
		for channel in channels:
			await channel.set_permissions(ctx.guild.default_role,send_messages=True,add_reactions=True)
			await ctx.send(f'**<:vf:947194381172084767>Successfully Unlocked**', delete_after=5)


	@cmd.command(aliases=['hc'])
	@commands.has_permissions(administrator=True)
	async def hide_category(self, ctx,category: discord.CategoryChannel, role :discord.Role = None):
		if role == None:
			role = ctx.guild.default_role
		channels = category.channels
		for channel in channels:
			await channel.set_permissions(role, view_channel=False)
			await ctx.send(f'**<:vf:947194381172084767> {channel.mention} is Hidden from {role.name}**', delete_after=5)


	@cmd.command(aliases=['uhc'])
	@commands.has_permissions(administrator=True)
	async def unhide_category(self, ctx,category: discord.CategoryChannel, role :discord.Role = None):
		if role == None:
			role = ctx.guild.default_role
		channels = category.channels
		for channel in channels:
			await channel.set_permissions(role, view_channel=True)
			await ctx.send(f'**<:vf:947194381172084767> {channel.mention} is Visible to {role.name}**', delete_after=5)





	#clear command
	@cmd.command(help="Use this command to clear messages in a text channel\nExample : &clear 10")
	@commands.has_permissions(manage_messages=True)
	@commands.cooldown(2, 20, commands.BucketType.user)
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

		if member == ctx.author:
			return await ctx.send("**You cant mute your self**", delete_after=5)

		if ctx.author.top_role < member.top_role:
			return await ctx.send("**You can't Mute Him**", delete_after=5)

		if self.bot.top_role < member.top_role:
			return await ctx.send("**I can't Mute Him**", delete_after=5)

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
	@commands.has_permissions(ban_members=True)
	async def ban(self, ctx, member: discord.Member, reason=None):
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




def setup(bot):
    bot.add_cog(Moderation(bot))
