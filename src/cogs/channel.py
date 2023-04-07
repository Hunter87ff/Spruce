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
	@commands.bot_has_permissions(manage_channels=True)
	async def channel_make(self, ctx, *names):
		try:
			ms = await ctx.send("Processing...")
		except:
			pass
		for name in names:
			await ctx.guild.create_text_channel(name)

		if ms:
			try:
				await ms.edit(content=f'**<:vf:947194381172084767>All channels Created.**')
			except:
				return



	@cmd.command(aliases=['chd'])
	@commands.has_permissions(manage_channels=True)
	@commands.bot_has_permissions(manage_channels=True)
	async def channel_del(self, ctx, *channels: discord.TextChannel):
		try:
			ms = await ctx.send("Processing...")
		except:
			pass
		for ch in channels:
			await ch.delete()
		if ms:
			try:
				await ms.edit(content=f'**<:vf:947194381172084767>`Channels deleted Successfully**')
			except:
				return




	@cmd.hybrid_command(with_app_command = True)
	@commands.has_permissions(administrator=True)
	@commands.bot_has_permissions(manage_channels=True)
	async def delete_category(self, ctx, category: discord.CategoryChannel):
		await ctx.defer(ephemeral=True)
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
		        await interaction.response.send_message("<a:loading:969894982024568856>**Processing...**", ephemeral=True)
		        await interaction.message.delete()
		        for channel in category.channels:
		            await channel.delete(reason=f'Deleted by {ctx.author.name}')

		            if len(category.channels) == 0:
		                await category.delete()
		                return await interaction.edit_original_response(content=f'**<:vf:947194381172084767>Successfully Deleted**')
		async def del_msg(interaction):
			await interaction.message.delete()

		bt11.callback = dc_confirmed
		bt12.callback = del_msg



	@cmd.hybrid_command(with_app_command=True, description="Enter Names With ',' to separate them")
	@commands.has_permissions(manage_channels=True)
	@commands.bot_has_permissions(manage_channels=True)
	async def create_channel(self, ctx, category:discord.CategoryChannel, names:str):
		await ctx.defer(ephemeral=True)
		if ctx.author.bot:
			return
		if "," not in names:
			return await ctx.reply("Please separate names with ',' ")
		try:
			ms = await ctx.send("Processing...")
		except:
			return
		for name in names.split(","):
			category = await discord.utils.get(ctx.guild.categories, category)
			await ctx.guild.create_text_channel(name, category=category, reason=f"{ctx.author} created")
		try:
			await ms.edit(content="Channels Created.")
		except:
			return





async def setup(bot):
	await bot.add_cog(Channel(bot))
