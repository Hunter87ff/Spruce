import discord
from discord.ext import commands
cmd = commands

blurple = 0x7289da
greyple = 0x99aab5
d_grey = 0x546e7a
d_theme = 0x36393F
l_grey = 0x979c9f
d_red = 0x992d22
red = 0xe74c3c
d_orange = 0xa84300
orange= 0xe67e22
d_gold = 0xc27c0e
gold = 0xf1c40f
magenta = 0xe91e63
purple = 0x9b59b6
d_blue = 0x206694 
blue = 0x3498db
green = 0x2ecc71
d_green = 0x1f8b4c
teal = 0x1abc9c
d_teal = 0x11806a


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
		req = await self.bot.http.request(discord.http.Route("GET", "/users/{uid}", uid=user.id))
		banner_id = req["banner"]

		if banner_id:
			banner_url = f"https://cdn.discordapp.com/banners/{user.id}/{banner_id}.gif?size=1024"
		await ctx.send(f"{banner_url}")

	@cmd.command(aliases=['emb'])
	async def embed(self, ctx, clr:str, *, message):
		embed = discord.Embed(description=message, color=blue)
		await ctx.send(embed=embed)




	

















def setup(bot):
	bot.add_cog(Utility(bot))