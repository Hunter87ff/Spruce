import discord
from discord.ext import commands
from asyncio import sleep

pref = "&"
cmd = commands

class Channel(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.counter = 0





	@cmd.command(aliases=['chm'])
	@commands.has_permissions(manage_channels=True)
	@commands.bot_has_permissions(manage_channels=True, send_messages=True, manage_messages=True)
	async def channel_make(self, ctx, *names):
		for name in names:
			await ctx.guild.create_text_channel(name)
			await ctx.send(f'**<:vf:947194381172084767>`{name}` has been created**',delete_after=5)
			await sleep(1)


	@cmd.command(aliases=['chd'])
	@commands.has_permissions(manage_channels=True, send_messages=True)
	@commands.bot_has_permissions(manage_channels=True, send_messages=True, manage_messages=True)
	async def channel_del(self, ctx, *channels: discord.TextChannel):
		for ch in channels:
			await ch.delete()
			await ctx.send(f'**<:vf:947194381172084767>`{ch.name}` has been deleted**',delete_after=5)
			await sleep(1)



	@cmd.command(aliases=['dc'])
	@commands.has_permissions(administrator=True)
	@commands.bot_has_permissions(manage_channels=True, send_messages=True, manage_messages=True)
	async def delete_category(self, ctx,category: discord.CategoryChannel):
		channels = category.channels
		for channel in channels:
			await channel.delete(reason=f'Deleted by {ctx.author.name}')
			await ctx.send(f'**<:vf:947194381172084767>Successfully deleted  by {ctx.author.name}**', delete_after=5)




	@cmd.command(aliases=['cch'])
	@commands.has_permissions(manage_channels=True)
	@commands.bot_has_permissions(manage_channels=True, send_messages=True)
	async def create_channel(self, ctx, category, *names):
	  for name in names:
	    category = await discord.utils.get(ctx.guild.category_channels, category)
	    await ctx.guild.create_text_channel(name, category=category, reason=f"{ctx.author} created")
	    await ctx.send("Done", delete_after=5)





def setup(bot):
	bot.add_cog(Channel(bot))
