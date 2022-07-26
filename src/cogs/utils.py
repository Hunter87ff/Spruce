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
 "1 number ka noob","Nehi bolunga kya kar loge", "insan", "bhoot", "bhagwan", "e-smart ultra pro max"]

coin = ["<:coin_tell:975413333291335702> ", "<:coin_head:975413366493413476>"]


class Utility(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.counter = 0



	@cmd.command(aliases=['av'])
	@commands.bot_has_permissions(send_messages=True, embed_links=True)
	async def avatar(self, ctx, user: discord.User = None):


		if user == None:
			user = ctx.author
			emb = discord.Embed(title=ctx.author, description=f"[JPG](https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.jpg?size=1024) | [PNG](https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.png?size=1024) | [GIF](https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.gif?size=1024)", color=blurple)
			emb.timestamp = datetime.datetime.utcnow()
			emb.set_image(url=user.avatar)
			return await ctx.send(embed=emb)
			
		else:
			eemb = discord.Embed(title=user, description=f"[JPG](https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.jpg?size=1024) | [PNG](https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.png?size=1024) | [GIF](https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.gif?size=1024)", color=blurple)
			eemb.timestamp = datetime.datetime.utcnow()
			eemb.set_image(url=user.avatar)
			return await ctx.send(embed=eemb)



	@cmd.command(aliases=['sav'])
	@commands.bot_has_permissions(send_messages=True, embed_links=True)
	async def server_av(self, ctx):
		await ctx.send(ctx.guild.avatar)



	@cmd.command(aliases=['bnr'])
	@commands.bot_has_permissions(send_messages=True, manage_messages=True, embed_links=True)
	async def banner(self, ctx, user:discord.User = None ):
		if user == None:
			user = ctx.author
		req = await self.bot.http.request(discord.http.Route("GET", "/users/{uid}", uid=user.id))
		banner_id = req["banner"]

		if banner_id:
			banner_url = f"https://cdn.discordapp.com/banners/{user.id}/{banner_id}.gif?size=1024"
		await ctx.send(f"{banner_url}")

	@cmd.command(aliases=['emb'])
	@commands.bot_has_permissions(send_messages=True, manage_messages=True)
	@commands.cooldown(2, 20, commands.BucketType.user)
	async def embed(self, ctx, *, message):
		embed = discord.Embed(description=message, color=blue)
		await ctx.channel.purge(limit=1)
		await ctx.send(embed=embed)

	
	@cmd.command()
	@commands.cooldown(2, 20, commands.BucketType.user)
	@commands.bot_has_permissions(send_messages=True, manage_messages=True)
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
	@commands.bot_has_permissions(send_messages=True, manage_messages=True)
	@commands.cooldown(2, 8, commands.BucketType.user)
	async def toss(self, ctx):
		msg = random.choice(coin)
		emb = discord.Embed(title=msg, color=yellow)
		await ctx.send(embed=emb)



	@cmd.command()
	@commands.has_permissions(manage_messages=True)
	@commands.bot_has_permissions(send_messages=True, manage_messages=True, embed_links=True)
	@commands.cooldown(2, 10, commands.BucketType.user)
	async def em(self, ctx, image, *, message):
		emb = discord.Embed(description=message, color=blue)
		emb.set_image(url=image)
		await ctx.channel.purge(limit=1)
		await ctx.send(embed=emb) 


	@cmd.command()
	@commands.cooldown(2, 360, commands.BucketType.user)
	@commands.has_permissions(add_reactions=True)
	@commands.bot_has_permissions(add_reactions=True)
	async def react(self, ctx, msg_id, *emojis):
		for emoji in emojis:
			msg = await ctx.channel.fetch_message(msg_id)
			await ctx.channel.purge(limit=1)
			await msg.add_reaction(emoji)



	@cmd.command()
	@commands.has_permissions(administrator=True)
	@commands.bot_has_permissions(send_messages=True, manage_messages=True)
	@commands.cooldown(2, 60, commands.BucketType.user)
	async def prefix(self, ctx, prefix):
		with open(r"data/prefixes.json" , "r") as f:
		    prefixes = json.load(f)
         
		prefixes[int(ctx.guild.id)] = prefix
		
		with open(r"data/prefixes.json", "w") as f:
		    json.dump(prefixes, f, indent=4)
		    await ctx.send(f"Prefix set to `{prefix}`")



	@cmd.command(aliases=['mc'])
	@commands.bot_has_permissions(manage_messages=True, send_messages=True)
	@commands.cooldown(2, 10, commands.BucketType.user)
	async def member_count(self, ctx):
	  
		emb = discord.Embed(title="Members", description=f"{ctx.guild.member_count}", color=teal)
		emb.set_footer(text=f'Requested by - {ctx.author}', icon_url=ctx.author.avatar)
		
		await ctx.channel.purge(limit=1)
		await ctx.send(embed=emb)

		
	@cmd.command(aliases=['ui'])
	@commands.bot_has_permissions(manage_messages=True, send_messages=True)
	async def userinfo(self, ctx, member : discord.Member = None):
		if member == None:
			member = ctx.author
		else:
			member = member
			
		roles = list(sorted(member.roles, key=lambda role: role.position))
		embed = discord.Embed(colour=member.colour.purple(), timestamp=ctx.message.created_at)
		embed.set_author(name=f"{member}")
		embed.set_thumbnail(url=member.avatar)
		embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)
		embed.add_field(name="User Name:", value=f"{member.name}")
		embed.add_field(name="ID:", value=member.id)
		embed.add_field(name="Server name:", value=member.display_name)
		embed.add_field(name="Created at:", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p"))
		embed.add_field(name="Joined at:", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p"))
		embed.add_field(name=f"Roles ({len(roles)})", value=" ".join([role.mention for role in roles][1:]))
		embed.add_field(name="Top role:", value=member.top_role.mention)
		embed.add_field(name="Bot?", value=member.bot)
		await ctx.send(embed=embed)
		

	@cmd.command()
	@commands.cooldown(2, 10, commands.BucketType.user)
	@commands.bot_has_permissions(manage_messages=True, send_messages=True, manage_nicknames=True)
	async def nick(self, ctx, user:discord.Member,  *, Nick):
		if ctx.author.top_role < user.top_role:
			return await ctx.send("You don't have enough permission")

		if self.bot.top_role < user.top_role:
			return await ctx.send("I don't have enough permission")

		else:
			return await user.edit(nick=Nick)
		
		
		
	@cmd.command(aliases=['si'])
	@commands.cooldown(2, 10, commands.BucketType.user)
	@commands.bot_has_permissions(manage_messages=True, send_messages=True, embed_links=True)
	async def serverinfo(self, ctx, user: discord.Member=None):
		if user == None:
			user = ctx.author
			
		guild = ctx.guild
		emb = discord.Embed(title=f"{ctx.guild.name}'s Information",
                        description=f"**__About__**\n**Name** : {ctx.guild.name}\n**Id** : {ctx.guild.id}\n**Owner** : {ctx.guild.owner.mention}\n**Members** : {len(guild.members)}\n**Verification Level** : {guild.verification_level}\n**Upload Limit** : {(guild.filesize_limit)/1024/1024} MB\n**Created At** : {guild.created_at.strftime('%a, %#d %B %Y, %I:%M %p')}\n\n**__Channels__**\n**Category Channels** : {len(guild.categories)}\n**Voice Channels** : {len(guild.voice_channels)}\n**Text Channels** : {len(guild.text_channels)}",
                       color=0xf1c40f)
		await ctx.channel.purge(limit=1)
		await ctx.send(embed=emb)



"""

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
					emb.set_author(name=f"{user}", icon_url=user.avatar)
					emb.set_footer(text="Spruce", icon_url="https://sprucebot.ml/resources/manifest/icon-310x310.png")

					return await ctx.send(embed=emb)

"""


async def setup(bot):
	await bot.add_cog(Utility(bot))
