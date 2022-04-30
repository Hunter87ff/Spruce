import discord
from discord.ext import commands
hg = commands
gbr = "https://raw.githubusercontent.com/Hunter87ff/atomic-8/main/Game_roles/star_border.gif"



# Raw
ffemb = discord.Embed(title="FREE FIRE", description="**Garena Free Fire is a battle royal game. Played by millions of people. Developed by 111 dots studio and published by Garena. React on the emoji to access this game!**", color=discord.Color.blurple())
ffemb.set_thumbnail(url="https://raw.githubusercontent.com/Hunter87ff/atomic-8/main/Game_roles/freefire.png")
bgmiemb = discord.Embed(title="BGMI", description="**Battlegrounds Mobile India(BGMI), Made for players in India. It is an online multiplayer battle royale game developed and published by Krafton. React on the emoji to access this game**", color=discord.Color.blurple())
bgmiemb.set_thumbnail(url="https://raw.githubusercontent.com/Hunter87ff/atomic-8/main/Game_roles/bgmi.png")
codemb = discord.Embed(title="CALL OF DUTY", description="**Call Of Duty is a multiplayer online battle royal game, developed by TiMi Studio Group and published by Activision.react on the emoji to access this game**", color=discord.Color.blurple())
codemb.set_thumbnail(url="https://raw.githubusercontent.com/Hunter87ff/atomic-8/main/Game_roles/codm.png")
valoemb = discord.Embed(title="VALORANT", description="**Valorant is a multiplayer online battle royal game made for pc, developed and published by Riot Games. react on the emoji to access this game**", color=discord.Color.blurple())
valoemb.set_thumbnail(url="https://raw.githubusercontent.com/Hunter87ff/atomic-8/main/Game_roles/valorant.png")



class Templates(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.counter = 0

	@hg.command(aliases=["grole"])
	@commands.cooldown(1, 10, commands.BucketType.user)
	@commands.has_permissions(manage_messages=True)
	async def game_role(self, ctx, channel:discord.TextChannel=None):
		if channel == None:
			channel = ctx.channel

			await channel.send(gbr)
			await channel.send(embed=ffemb)
			await channel.send(gbr)
			await channel.send(embed=bgmiemb)
			await channel.send(gbr)
			await channel.send(embed=codemb)
			await channel.send(gbr)
			await channel.send(embed=valoemb)
			await channel.send(gbr)










def setup(bot):
    bot.add_cog(Templates(bot))
