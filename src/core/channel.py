import discord
from discord.ext import commands
from asyncio import sleep
from discord.ui import Button, View
from modules import config




class Channel(commands.Cog):
	def __init__(self, bot):
		self.bot:commands.Bot = bot
		

	@commands.command(aliases=['chm'])
	@commands.has_permissions(manage_channels=True)
	@commands.bot_has_permissions(manage_channels=True)
	async def channel_make(self, ctx:commands.Context,  *names):
		if ctx.author.bot:return
		if not await config.voted(ctx, bot=self.bot):return await config.vtm(ctx)
		ms = await ctx.send("Processing...")
		for name in names:
			await ctx.guild.create_text_channel(name, reason=f"created by : {ctx.author}")
			await sleep(1)
		await ms.edit(content=f'**{config.tick} | All channels Created.**')
		

	@commands.command(aliases=['chd'])
	@commands.has_permissions(manage_channels=True)
	@commands.bot_has_permissions(manage_channels=True, send_messages=True)
	async def channel_del(self, ctx:commands.Context,  *channels: discord.TextChannel):
		ms =await ctx.send("Processing...")
		for ch in channels:
			await ch.delete(reason=f"deleted by: {ctx.author}")
			await sleep(1)
		await ms.edit(content=f'**{config.tick} | Channels deleted Successfully**')
		

	@commands.hybrid_command(with_app_commands=True, aliases=['dc'])
	@commands.has_permissions(administrator=True)
	@commands.bot_has_permissions(manage_channels=True)
	async def delete_category(self, ctx:commands.Context,  category: discord.CategoryChannel):
		await ctx.defer()
		if ctx.author.bot:return
		if not await config.voted(ctx, bot=self.bot):
			return await config.vtm(ctx)
		bt11 = Button(label="Confirm", style=discord.ButtonStyle.danger, custom_id="dcd_btn")
		bt12 = Button(label="Cancel", style=discord.ButtonStyle.green, custom_id="dcc_btn")
		view = View()
		for i in [bt11, bt12]:
			view.add_item(i)
		del_t_con = await ctx.reply(f"**Are You Sure To Delete `{category.name}`?**", view=view)
		async def dc_confirmed(interaction:discord.Interaction):
			if not interaction.user.bot:
				emb = discord.Embed(color=0x00ff00, description=f"**{config.loading} | Deleting `{category.name}` Category**")
				await del_t_con.edit(content=None, embed=emb, view=None)
				for channel in category.channels:
					await channel.delete(reason=f'Deleted by {ctx.author.name}')
					await sleep(1)
					if len(category.channels) == 0:
						await category.delete()
						return await del_t_con.edit(embed=discord.Embed(description=f"**{config.tick} | Successfully Deleted ~~{category.name}~~ Category**"))
		async def del_msg(interaction):
			await interaction.message.delete()
		bt11.callback = dc_confirmed
		bt12.callback = del_msg
		

	@commands.command(aliases=["cch"])
	@commands.has_permissions(manage_channels=True)
	@commands.bot_has_permissions(manage_channels=True)
	async def create_channel(self, ctx:commands.Context,  category:discord.CategoryChannel, *names:str):
		if ctx.author.bot:return
		ms = await ctx.send(embed=discord.Embed(description=f"**{config.loading} | Creating Channels...**"))
		for name in names:await ctx.guild.create_text_channel(name, category=category, reason=f"{ctx.author} created")
		await ms.edit(embed=discord.Embed(description=f"**{config.default_tick} | All Channels Created**", color=0x00ff00))
		




async def setup(bot):
	await bot.add_cog(Channel(bot))