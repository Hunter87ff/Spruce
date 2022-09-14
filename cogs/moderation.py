import discord
from asyncio import sleep
from discord.ext import commands
cmd = commands
import datetime
import humanfriendly

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
		bt = ctx.guild.get_member(self.bot.user.id)
		if ctx.author.bot:
			return

		muted = discord.utils.get(ctx.guild.roles, name="Muted")
		if muted == None:
			muted = await ctx.guild.create_role(name="Muted", color=0xff0000)

		if muted.position > bt.top_role.position:
			return await ctx.reply("`Muted` role is higher than  my top role, I can't manage it")

		snd = await ctx.send("<a:loading:969894982024568856>**Processing...**")

		overwrite = ctx.channel.overwrites_for(muted)
		overwrite.update(send_messages=False, add_reactions=False, connect=False, speak=False)
		for channel in ctx.guild.channels:
			await channel.set_permissions(muted, overwrite=overwrite)
			
		try:
			await snd.edit(content=f'**<:vf:947194381172084767>Setuped Successfully**')
			
		except:
			return



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







	@cmd.command(help=" Use this command to remove all permissions permission from all roles")
	@commands.has_permissions(administrator=True)
	@commands.bot_has_permissions(manage_roles=True, send_messages=True, manage_messages=True)
	async def clear_perms(self, ctx, role: discord.Role=None):
		bt = ctx.guild.get_member(self.bot.user.id)

		if ctx.author.bot:
			return

		if role == None:
			for role in ctx.guild.roles:
				if role.position < bt.top_role.position:
					await role.edit(permissions=discord.Permissions(permissions=0))

		if role != None:
			if role.position < bt.top_role.position:
				await role.edit(permissions=discord.Permissions(permissions=0))


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

		
		for hchannel in category.channels:
		  overwrite = hchannel.overwrites_for(role)
		  overwrite.update(view_channel=False)
		  await hchannel.set_permissions(role, overwrite=overwrite)
		em = discord.Embed(description=f'**<:vf:947194381172084767> {category.name} is Hidden from {role.name}**', color=0x00ff00)
		await ctx.send(embed=em, delete_after=5)
			#await sleep(1)


	@cmd.command(aliases=['uhc'])
	@commands.has_permissions(administrator=True)
	@commands.bot_has_permissions(manage_channels=True)
	async def unhide_category(self, ctx, category: discord.CategoryChannel, role :discord.Role = None):
		if ctx.author.bot:
			return

		if role == None:
			role = ctx.guild.default_role
			

		
		for uhchannel in category.channels:
		  overwrite = uhchannel.overwrites_for(role)
		  overwrite.update(view_channel=True)
		  await uhchannel.set_permissions(role, overwrite=overwrite)
		em = discord.Embed(description=f'**<:vf:947194381172084767> {category.name} is Visible to {role.name}**', color=0x00ff00)
		await ctx.send(embed=em, delete_after=5)





	#clear command
	@cmd.command(aliases=["purge"], help="Use this command to clear messages in a text channel\nExample : &clear 10")
	@commands.has_permissions(manage_messages=True)
	@commands.bot_has_permissions(manage_messages=True, send_messages=True)
	@commands.cooldown(2, 20, commands.BucketType.user)
	async def clear(self, ctx, amount:int=None):

		if ctx.author.bot:
			return

		if amount == None:
			amount = 10

		await ctx.channel.purge(limit=amount)
		return await ctx.send(f'**<:vf:947194381172084767> Successfully cleared {amount} messages**',delete_after=5)




	#Mute Command
	@cmd.command()
	@commands.has_permissions(moderate_members=True)
	@commands.bot_has_permissions(moderate_members=True)
	async def unmute(self, ctx, member: discord.Member, *, reason=None):
		bt = ctx.guild.get_member(self.bot.user.id)
		if reason == None:
			reason = 'No reason provided'
		if not ctx.author.top_role.position > member.top_role.position:
			return await ctx.reply("You Can Not Manage Him")

		if not bt.top_role.position > member.top_role.position:
		    return await ctx.reply("I can't manage him")

		else:
		    time = humanfriendly.parse_timespan("0")
		    await member.edit(timed_out_until=discord.utils.utcnow() + datetime.timedelta(seconds=time), reason=reason)
		    await ctx.send(f"{member} has been unmuted")		


	@cmd.command()
	@commands.has_permissions(moderate_members=True)
	@commands.bot_has_permissions(moderate_members=True)
	async def mute(self, ctx, member: discord.Member, time=None, *, reason=None):
		bt = ctx.guild.get_member(self.bot.user.id)
		if time == None:
			time = "5m"

		if reason == None:
			reason = 'No reason provided'

		if not ctx.author.top_role.position > member.top_role.position:
			return await ctx.reply("You Can Not Manage Him")

		if not bt.top_role.position > member.top_role.position:
		    return await ctx.reply("I can't manage him")

		else:
		    timee = humanfriendly.parse_timespan(time)
		    await member.edit(timed_out_until=discord.utils.utcnow() + datetime.timedelta(seconds=timee), reason=reason)
		    await ctx.send(f"{member} has been muted for {time}.\nReason: {reason}")		



	@commands.command()
	@commands.has_permissions(kick_members=True)
	@commands.bot_has_permissions(kick_members=True)
	async def kick(self, ctx, member: discord.Member, reason=None):
		if ctx.author.bot:
			return

		if reason == None:
			reason = f"{member} kicked by {ctx.author}"

		if ctx.author.top_role.position < member.top_role.position:
			return await ctx.send("You don't have enough permission", delete_after=5)

		elif member == ctx.author:
			return await ctx.send("**You can't kick your self**", delete_after=5)

		elif ctx.guild.me.top_role.position < member.top_role.position:
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

		if ctx.author.top_role.position < member.top_role.position:
			return await ctx.send("You don't have enough permission", delete_after=5)

		elif member == ctx.author:
			return await ctx.send("**You can't ban your self**", delete_after=5)

		elif ctx.guild.me.top_role.position < member.top_role.position:
			return await ctx.send("**I can't ban him**", delete_after=5)

		else:
			await ctx.guild.ban(member, reason=reason)
			return await ctx.send(f"{member} banned", delete_after=5)




async def setup(bot):
    await bot.add_cog(Moderation(bot))
