import discord
from discord.ext import commands
cmd = commands

class Utility(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.counter = 0


	@cmd.command(aliases=['av'])
	async def avatar(self, ctx, user:discord.Member = None):
		if user == None:
			user = ctx.author
			return await ctx.send(user.avatar_url)

		else:
			return await ctx.send(user.avatar_url)


	@cmd.command(aliases=['sav'])
	async def server_av(self, ctx):
		await ctx.send(ctx.guild.icon_url)



	@cmd.command(aliases=['bnr'])
	async def banner(self, ctx, user:discord.Member = None ):
		if user == None:
			user = ctx.author
		req = await bot.http.request(discord.http.Route("GET", "/users/{uid}", uid=user.id))
		banner_id = req["banner"]

		if banner_id:
			banner_url = f"https://cdn.discordapp.com/banners/{user.id}/{banner_id}.gif?size=1024"
		await ctx.send(f"{banner_url}")




	

















def setup(bot):
	bot.add_cog(Utility(bot))