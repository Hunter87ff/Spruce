import discord
from discord.ext import commands
from asyncio import sleep
cmd = commands
from discord.ui import Button, View














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
	async def delete_category(self, ctx, category: discord.CategoryChannel):
		if ctx.author.bot:
			return
		bt11 = Button(label="Confirm", style=discord.ButtonStyle.danger, custom_id="dcd_btn")
		bt12 = Button(label="Cancel", style=discord.ButtonStyle.green, custom_id="dcc_btn")
		view = View()
		for i in [bt11, bt12]:
			view.add_item(i)
		del_t_con = await ctx.reply("**Are You Sure To Delete The Category?**", view=view)

		async def dc_confirmed(interaction):
		    if not interaction.user.bot:
		        await interaction.message.edit(content="<a:loading:969894982024568856>**Processing...**", view=None)
		        for channel in category.channels:
		            await channel.delete(reason=f'Deleted by {ctx.author.name}')

		            if len(category.channels) == 1:
		                await category.delete()
		                return await interaction.message.edit(content=f'**<:vf:947194381172084767>Successfully Deleted**')
		async def del_msg(interaction):
			await interaction.message.delete()

		bt11.callback = dc_confirmed
		bt12.callback = del_msg



	@cmd.command(aliases=['cch'])
	@commands.has_permissions(manage_channels=True)
	@commands.bot_has_permissions(manage_channels=True, send_messages=True)
	async def create_channel(self, ctx, category, *names):
	  for name in names:
	    category = await discord.utils.get(ctx.guild.categories, category)
	    await ctx.guild.create_text_channel(name, category=category, reason=f"{ctx.author} created")
	    await ctx.send("Done", delete_after=5)





async def setup(bot):
	await bot.add_cog(Channel(bot))
