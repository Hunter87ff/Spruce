import discord
from discord.ext import commands
cmd = commands
import random
import datetime
import json
import os
import pymongo
from pymongo import MongoClient
from modules import config
from discord.ui import Button, View


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


whois = ["Noob","Unknown Person","kya pata mai nehi janta","bohot piro", "Bohot E-smart","Dusro Ko Jan Ne Se Pehle Khud Ko Jan Lo","Nalla", "Bohot achha","bohooooooooot badaaaaa Bot","Nehi bolunga kya kar loge", "insan", "bhoot", "bhagwan", "e-smart ultra pro max"]
coin = ["975413333291335702", "975413366493413476"]
maindb = config.maindb
nitrodbc = maindb["nitrodb"]["nitrodbc"]






class Utility(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.counter = 0


	@cmd.command()
	async def uptime(self, ctx):
		try:
			sch = self.bot.get_channel(1020027121231462400)
		except:
			return
		messages = [message async for message in sch.history(limit=3)]
		uptime = ctx.message.created_at - messages[0].created_at
		upt = str(uptime).split(".")[0]
		try:
			await ctx.send(f"**Current Uptime Is - `{upt} h`**")
		except:
			return





	@cmd.command(aliases=['av', "pfp"])
	@commands.bot_has_permissions(send_messages=True, embed_links=True)
	async def avatar(self, ctx, user: discord.User = None):


		if user == None:
			user = ctx.author
			
		if "a_" in str(user.avatar):
			eemb = discord.Embed(title=user, description=f"[JPG]({user.display_avatar.with_format('jpg')}) | [PNG]({user.display_avatar.with_format('png')}) | [GIF]({user.display_avatar})", color=0xfff00f)			#eemb.timestamp = datetime.datetime.utcnow()
			eemb.set_image(url=user.avatar)
			eemb.set_footer(text=f"Requested By {ctx.author}")
			return await ctx.send(embed=eemb)

			
		else:
			eemb = discord.Embed(title=user, description=f"[JPG]({user.display_avatar.with_format('jpg')}) | [PNG]({user.display_avatar.with_format('png')})", color=0x00fff0)
			#eemb.timestamp = datetime.datetime.utcnow()
			eemb.set_image(url=user.display_avatar)
			eemb.set_footer(text=f"Requested By {ctx.author}")
			return await ctx.send(embed=eemb)
			



	@cmd.command(aliases=['sav'])
	@commands.bot_has_permissions(embed_links=True)
	async def server_av(self, ctx, guild:discord.Guild=None):
		if guild == None:
			guild = ctx.guild

		if guild.icon != None:
			enm = discord.Embed(title=guild.name, url=guild.icon, color=0xff0000)
			enm.set_image(url=guild.icon)
			await ctx.send(embed=enm)

		if guild.icon == None:
			return await ctx.reply("**Server Don't Have A Logo XD**", delete_after=10)



	@cmd.command(aliases=["bnr"])
	async def banner(self, ctx, user:discord.User=None):
		if ctx.author.bot:
			return
		if user == None:
			user = ctx.author
		usr = await self.bot.fetch_user(user.id)
		banner = usr.banner
		if not banner:
		    return await ctx.reply("User Don't Have A Banner", delete_after=20)
		banner_url = banner.url
		emb = discord.Embed(colour=0xff0000, description=f"**[BANNER URL]({banner_url})**")
		emb.set_image(url=banner_url)
		await ctx.send(embed=emb)


	@cmd.command(aliases=['emb'])
	@commands.bot_has_permissions(send_messages=True, manage_messages=True)
	@commands.cooldown(2, 20, commands.BucketType.user)
	async def embed(self, ctx, *, message):
		embed = discord.Embed(description=message, color=blue)
		await ctx.channel.purge(limit=1)
		await ctx.send(embed=embed)


	@cmd.command(aliases=['text2speech'])
	async def tts(self, ctx, *, message):
		output = gTTS(text=message, lang="en", tld="co.in")
		output.save(f"tts.mp3")
		#fl = open("tts.mp3", r).read()
		await ctx.send(ctx.author.mention, file=discord.File("tts.mp3"))
		os.remove("tts.mp3")


	@cmd.command(aliases=['steal'])
	@commands.guild_only()
	@commands.bot_has_permissions(manage_emojis=True)
	@commands.has_permissions(manage_emojis=True)
	async def addemoji(self, ctx, emoji: discord.PartialEmoji):
		emoji_bytes = await emoji.read()
		new = await ctx.guild.create_custom_emoji(name=emoji.name, image=emoji_bytes, reason=f'Emoji Added By {ctx.author}')
		return await ctx.send(f"{new} added", delete_after=10)

	
	@cmd.command()
	@commands.cooldown(2, 20, commands.BucketType.user)
	async def whoiss(self, ctx, user:discord.Member=None):
		if user == None:
			user = ctx.author
			msg = random.choice(whois)

		if user.bot == True:
			return await ctx.send("**Bot is always awesome**")


		elif user.id == 885193210455011369:
			owneremb = discord.Embed(description=f"{user.mention} **Best Friend :heart:**", color=blue)
			return await ctx.send(embed=owneremb)

		else:
			msg = random.choice(whois)
			emb = discord.Embed(description=f"{user.mention}  {msg}", color=blurple)
			return await ctx.send(embed=emb)



	@cmd.command()
	@commands.bot_has_permissions(send_messages=True)
	@commands.cooldown(2, 8, commands.BucketType.user)
	async def toss(self, ctx):
		msg = f"https://cdn.discordapp.com/emojis/{random.choice(coin)}.png"
		emb = discord.Embed(color=yellow)
		emb.set_image(url=msg)
		await ctx.send(embed=emb)



	@cmd.command()
	@commands.bot_has_permissions(send_messages=True)
	@commands.cooldown(2, 8, commands.BucketType.user)
	async def invite(self, ctx):
		invbtn = Button(label="Invite Now", url="https://discord.com/api/oauth2/authorize?client_id=931202912888164474&permissions=8&redirect_uri=https%3A%2F%2Fdiscord.gg%2FvMnhpAyFZm&response_type=code&scope=bot%20identify")
		view = View()
		view.add_item(invbtn)
		try:
			await ctx.send("**Click On The Button To Invite Me:**", view=view)
		except:
			return


	@cmd.command()
	@commands.bot_has_permissions(send_messages=True)
	@commands.cooldown(2, 8, commands.BucketType.user)
	async def vote(self, ctx):
		invbtn = Button(label="Vote Now", url="https://top.gg/bot/931202912888164474/vote")
		view = View()
		view.add_item(invbtn)
		try:
			await ctx.send("**Click On The Button To Vote Me ^_^**", view=view)
		except:
			return


	@cmd.command()
	@commands.bot_has_permissions(send_messages=True)
	@commands.cooldown(2, 8, commands.BucketType.user)
	async def support(self, ctx):
		invbtn = Button(label="Support", url="https://discord.gg/vMnhpAyFZm")
		view = View()
		view.add_item(invbtn)
		try:
			await ctx.send("**Click On The Button To Join Our Support Server For Any Issue**", view=view)
		except:
			return


	@cmd.command(aliases=['em'])
	@commands.has_permissions(manage_messages=True)
	@commands.bot_has_permissions(send_messages=True, manage_messages=True, embed_links=True)
	@commands.cooldown(2, 10, commands.BucketType.user)
	async def embed_img(self, ctx, image, *, message):
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
	@commands.bot_has_permissions(send_messages=True)
	@commands.cooldown(2, 60, commands.BucketType.user)
	async def prefix(self, ctx):
		await ctx.send(config.prefix)



	@cmd.command(aliases=['mc'])
	@commands.bot_has_permissions(send_messages=True)
	@commands.cooldown(2, 10, commands.BucketType.user)
	async def member_count(self, ctx):
		emb = discord.Embed(title="Members", description=f"{ctx.guild.member_count}", color=teal)
		emb.set_footer(text=f'Requested by - {ctx.author}', icon_url=ctx.author.avatar)
		await ctx.send(embed=emb)

		
	@cmd.command(aliases=['ui'])
	@commands.bot_has_permissions(send_messages=True)
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
	@commands.bot_has_permissions(send_messages=True, manage_nicknames=True)
	async def nick(self, ctx, user:discord.Member,  *, Nick):
		bt = ctx.guild.get_member(self.bot.user.id)

		if ctx.author.top_role < user.top_role:
			return await ctx.send("You don't have enough permission")

		if bt.top_role < user.top_role:
			return await ctx.send("I don't have enough permission")

		else:
			return await user.edit(nick=Nick)

	@cmd.command()
	@commands.has_permissions(manage_webhooks=True)
	@commands.bot_has_permissions(manage_webhooks=True)
	async def nitro(self, ctx):
		gnitro = nitrodbc.find_one({"guild" : ctx.guild.id})
		if gnitro == None:
			nitrodbc.insert_one({"guild":ctx.guild.id, "nitro" : "enabled"})
		if gnitro != None and gnitro["nitro"] == "enabled":
			nitrodbc.update_one({"guild":ctx.guild.id}, {"$set":{"nitro" : "disabled"}})
			return await ctx.send("Disabled")
		if gnitro != None and gnitro["nitro"] == "disabled":
			nitrodbc.update_one({"guild":ctx.guild.id}, {"$set":{"nitro" : "enabled"}})
			return await ctx.send("Enabled")


		
		
		
	@cmd.command(aliases=['si'])
	@commands.cooldown(2, 10, commands.BucketType.user)
	@commands.bot_has_permissions(send_messages=True, embed_links=True)
	async def serverinfo(self, ctx, user: discord.Member=None):
		if user == None:
			user = ctx.author
			
		guild = ctx.guild
		emb = discord.Embed(title=f"{ctx.guild.name}'s Information",
                        description=f"**__About__**\n**Name** : {ctx.guild.name}\n**Id** : {ctx.guild.id}\n**Owner** : <@{ctx.guild.owner_id}>\n**Members** : {ctx.guild.member_count}\n**Verification Level** : {guild.verification_level}\n**Upload Limit** : {(guild.filesize_limit)/1024/1024} MB\n**Created At** : {guild.created_at.strftime('%a, %#d %B %Y, %I:%M %p')}\n\n**__Channels__**\n**Category Channels** : {len(guild.categories)}\n**Voice Channels** : {len(guild.voice_channels)}\n**Text Channels** : {len(guild.text_channels)}",
                       color=0xf1c40f)
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
