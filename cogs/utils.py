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
import random
import datetime
import json

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
yellow = 0xffff00

pref = "&"

whois = ["Noob","kya pata mai nehi janta","bohot piro", "Bohot E-smart",
"Good boy/girl : mujhe gender pata nehi ","Nalla", "Bohot achha","bohooooooooot badaaaaa Bot",
 "1 number ka noob","Nehi bolunga kya kar loge", "insan"]

coin = ["<:coin_tell:975413333291335702> ", "<:coin_head:975413366493413476>"]


class Utility(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.counter = 0



	@cmd.command(aliases=['av'])
	async def avatar(self, ctx, user: discord.User = None):


		if user == None:
			user = ctx.author
			emb = discord.Embed(title=ctx.author, description=f"[JPG](https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.jpg?size=1024) | [PNG](https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.png?size=1024) | [GIF](https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.gif?size=1024)", color=blurple)
			emb.timestamp = datetime.datetime.utcnow()
			emb.set_image(url=user.avatar_url)
			return await ctx.send(embed=emb)
			
		else:
			eemb = discord.Embed(title=user, description=f"[JPG](https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.jpg?size=1024) | [PNG](https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.png?size=1024) | [GIF](https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.gif?size=1024)", color=blurple)
			eemb.timestamp = datetime.datetime.utcnow()
			eemb.set_image(url=user.avatar_url)
			return await ctx.send(embed=eemb)



	@cmd.command(aliases=['sav'])
	async def server_av(self, ctx):
		await ctx.send(ctx.guild.icon_url)



	@cmd.command(aliases=['bnr'])
	async def banner(self, ctx, user:discord.User = None ):
		if user == None:
			user = ctx.author
		req = await self.bot.http.request(discord.http.Route("GET", "/users/{uid}", uid=user.id))
		banner_id = req["banner"]

		if banner_id:
			banner_url = f"https://cdn.discordapp.com/banners/{user.id}/{banner_id}.gif?size=1024"
		await ctx.send(f"{banner_url}")

	@cmd.command(aliases=['emb'])
	@commands.cooldown(2, 20, commands.BucketType.user)
	async def embed(self, ctx, *, message):
		embed = discord.Embed(description=message, color=blue)
		await ctx.channel.purge(limit=1)
		await ctx.send(embed=embed)

	@cmd.command()
	@commands.cooldown(2, 12, commands.BucketType.user)
	async def say(self, ctx, *, message):
		await ctx.channel.purge(limit=1)
		await ctx.send(message)



	
	@cmd.command()
	@commands.cooldown(2, 20, commands.BucketType.user)
	async def whoiss(self, ctx, user:discord.Member=None):
		if user == None:
			user = ctx.author
			msg = random.choice(whois)

		if user.bot == True:
			return await ctx.send("**Dude it's bot. And bot is always awesome**")


		elif user.id == 885193210455011369:
			owneremb = discord.Embed(description=f"{user.mention} is My Owner :heart: ", color=blue)
			return await ctx.send(embed=owneremb)

		else:
			msg = random.choice(whois)
			emb = discord.Embed(description=f"{user.mention}  {msg}", color=blurple)
			return await ctx.send(embed=emb)

	@cmd.command()
	@commands.cooldown(2, 8, commands.BucketType.user)
	async def toss(self, ctx):
		msg = random.choice(coin)
		emb = discord.Embed(title=msg, color=yellow)
		await ctx.send(embed=emb)



	@cmd.command()
	@commands.cooldown(2, 10, commands.BucketType.user)
	async def em(self, ctx, image, *, message):
		emb = discord.Embed(desctiption=message, color=blue)
		emb.set_image(url=image)
		await ctx.channel.purge(limit=1)
		await ctx.send(embed=emb) 


	@cmd.command()
	@commands.cooldown(2, 360, commands.BucketType.user)
	async def react(self, ctx, msg_id, *emojis):
		for emoji in emojis:
			msg = await ctx.channel.fetch_message(msg_id)
			await ctx.channel.purge(limit=1)
			await msg.add_reaction(emoji)



	@cmd.command()
	@commands.has_permissions(administrator=True)
	@commands.cooldown(2, 60, commands.BucketType.user)
	async def prefix(self, ctx, prefix):
		with open(r"data/prefixes.json" , "r") as f:
		    prefixes = json.load(f)
         
		prefixes[int(ctx.guild.id)] = prefix
		
		with open(r"data/prefixes.json", "w") as f:
		    json.dump(prefixes, f, indent=4)
		    await ctx.send(f"Prefix set to `{prefix}`")





	@cmd.command()
	@commands.cooldown(2, 10, commands.BucketType.user)
	async def join(self, ctx):
		channel = ctx.author.voice.channel
		await channel.connect()




	@cmd.command()
	async def leave(self, ctx):
		await ctx.voice_client.disconnect()



	@cmd.command(aliases=['mc'])
	@commands.cooldown(2, 10, commands.BucketType.user)
	async def member_count(self, ctx):
	  
		emb = discord.Embed(title="Members", description=f"{ctx.guild.member_count}", color=teal)
		emb.set_footer(text=f'Requested by - {ctx.author}', icon_url=ctx.author.avatar_url)
		
		await ctx.channel.purge(limit=1)
		await ctx.send(embed=emb)



	@cmd.command()
	async def say(self, ctx, *, message):
		for w in await ctx.channel.webhooks():
			wurl = w.url 


		data = {"content" : "", "avatar_url" : f"{ctx.author.avatar_url}", "username" : f"{ctx.author.name}" }

		data["embeds"] = [ { "description" : f"{message}", "title" : "", "color" : 0xffff00 }]

		try:
			await ctx.channel.purge(limit=1)
			requests.post(wurl, json = data)


		except:
			await ctx.reply("**I think this channel has no any webhooks, don't worry i've created one! now you can try**")
			await ctx.channel.create_webhooks(name=bot.name)










	@cmd.command()
	@commands.has_permissions(manage_messages=True)
	@commands.cooldown(2, 15, commands.BucketType.user)
	async def dm(self, ctx, user : discord.User, *, message):
		if ctx.author.id == 885193210455011369:
			emb = discord.Embed(description=message, color=blue)
			return await user.send(embed=emb)
			await ctx.channel.purge(limit=1)
			return await ctx.send("Sent", delete_after=10)

		else:
			return await ctx.send("You aren't a  pime member", delete_after=5)
			return await ctx.channel.purge(limit=1)


	@cmd.command()
	@commands.cooldown(2, 10, commands.BucketType.user)
	async def nick(self, ctx, user:discord.Member,  *, Nick):
		if ctx.author.top_role < user.top_role:
			return await ctx.send("You don't have enough permission")

		if self.bot.top_role < user.top_role:
			return await ctx.send("I don't have enough permission")

		else:
			return await user.edit(nick=Nick)





	@cmd.command()
	@commands.cooldown(2, 10, commands.BucketType.user)
	async def invites(self, ctx, user:discord.Member=None):
		totalInvites = 0

		if user == None:
			user = ctx.author

			for i in await ctx.guild.invites():
				if i.inviter == user:
					totalInvites += i.uses

					emb = discord.Embed(description=f"** <:invites:968901936327848016> Currently has {totalInvites} invites **", color=discord.Color.blurple())
					emb.set_author(name=f"{user}", icon_url=user.avatar_url)
					emb.set_footer(text="Spruce", icon_url="https://sprucebot.ml/resources/manifest/icon-310x310.png")

					return await ctx.send(embed=emb)




def setup(bot):
	bot.add_cog(Utility(bot))
