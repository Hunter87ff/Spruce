import discord
from discord.ext import commands
cmd = commands
import random
import os
from modules import config
from discord.ui import Button, View
import gtts
from gtts import gTTS




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



	@cmd.hybrid_command(with_app_command = True)
	@commands.cooldown(2, 60, commands.BucketType.user)
	async def uptime(self, ctx):
		if ctx.author.bot:
			return
		if not await config.voted(ctx, bot=self.bot):
			return await config.vtm(ctx)
		await ctx.defer(ephemeral=True)
		try:
			sch = self.bot.get_channel(config.stl)
		except:
			return
		messages = [message async for message in sch.history(limit=3)]
		uptime = ctx.message.created_at - messages[0].created_at
		upt = str(uptime).split(".")[0]
		msg = f"**Current Uptime Is : `{upt}`**"
		emb = discord.Embed(title="Uptime", color=0x00ff00, description=msg, timestamp=ctx.message.created_at)
		emb.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar)
		try:
			await ctx.send(embed=emb)
		except:
			return


	@cmd.command()
	@commands.bot_has_permissions(send_messages=True)
	@commands.cooldown(2, 60, commands.BucketType.user)
	async def ping(self, ctx):
	    if ctx.author.id == config.owner_id:
	        await ctx.reply(f'**Current ping is `{round(self.bot.latency*1000)} ms`**')
	    else:
	        await ctx.reply(f'**Current ping is `{random.choice(range(19,48))} ms`**')
	
	

	@cmd.hybrid_command(with_app_command = True, aliases=['av', "pfp"])
	@commands.bot_has_permissions(send_messages=True, embed_links=True)
	async def avatar(self, ctx, user: discord.User = None):
		if ctx.author.bot:
			return
		if not await config.voted(ctx, bot=self.bot):
			return await config.vtm(ctx)
		await ctx.defer(ephemeral=True)
		if user == None:
			user = ctx.author
			
		if "a_" in str(user.avatar):
			eemb = discord.Embed(title=user, description=f"[JPG]({user.display_avatar.with_format('jpg')}) | [PNG]({user.display_avatar.with_format('png')}) | [GIF]({user.display_avatar})", color=0xfff00f)			
			eemb.set_image(url=user.avatar)
			eemb.set_footer(text=f"Requested By {ctx.author}")
			return await ctx.send(embed=eemb)
		else:
			eemb = discord.Embed(title=user, description=f"[JPG]({user.display_avatar.with_format('jpg')}) | [PNG]({user.display_avatar.with_format('png')})", color=0x00fff0)
			eemb.set_image(url=user.display_avatar)
			eemb.set_footer(text=f"Requested By {ctx.author}")
			return await ctx.send(embed=eemb)
			



	@cmd.hybrid_command(with_app_command = True, aliases=['sav'])
	@commands.bot_has_permissions(embed_links=True)
	async def server_av(self, ctx, guild:discord.Guild=None):
		await ctx.defer(ephemeral=True)
		if not await config.voted(ctx, bot=self.bot):
			return await config.vtm(ctx)
		if guild == None:
			guild = ctx.guild

		if guild.icon != None:
			enm = discord.Embed(title=guild.name, url=guild.icon, color=0xff0000)
			enm.set_image(url=guild.icon)
			await ctx.send(embed=enm)

		if guild.icon == None:
			return await ctx.reply("**Server Don't Have A Logo XD**", delete_after=10)



	@cmd.hybrid_command(with_app_command = True, aliases=["bnr"])
	async def banner(self, ctx, user:discord.User=None):
		if ctx.author.bot:
			return
		if not await config.voted(ctx, bot=self.bot):
			return await config.vtm(ctx)
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
	@commands.cooldown(2, 60, commands.BucketType.user)
	async def embed(self, ctx, *, message):
		await ctx.defer()
		if ctx.author.bot:
			return
		if not await config.voted(ctx, bot=self.bot):
			return await config.vtm(ctx)
		embed = discord.Embed(description=message, color=blue)
		await ctx.channel.purge(limit=1)
		await ctx.send(embed=embed)


	@cmd.hybrid_command(with_app_command = True)
	@commands.cooldown(2, 60, commands.BucketType.user)
	async def tts(self, ctx, *, message):
		await ctx.defer(ephemeral=True)
		if ctx.author.bot:
			return
		if not await config.voted(ctx, bot=self.bot):
			return await config.vtm(ctx)
		if len(message.split()) > 100:
			return await ctx.reply("**Up to 100 words allowed**", delete_after=30)
		output = gTTS(text=message, lang="en", tld="co.in")
		output.save("tts.mp3")
		#fl = open("tts.mp3", r).read()
		await ctx.send(ctx.author.mention, file=discord.File("tts.mp3"))
		os.remove("tts.mp3")


	@cmd.hybrid_command(with_app_command = True)
	@commands.guild_only()
	@commands.bot_has_permissions(manage_emojis=True)
	@commands.has_permissions(manage_emojis=True)
	async def addemoji(self, ctx, emoji: discord.PartialEmoji):
		await ctx.defer(ephemeral=True)
		emoji_bytes = await emoji.read()
		new = await ctx.guild.create_custom_emoji(name=emoji.name, image=emoji_bytes, reason=f'Emoji Added By {ctx.author}')
		return await ctx.send(f"{new} added", delete_after=10)

	
	@cmd.hybrid_command(with_app_command = True)
	@commands.cooldown(2, 20, commands.BucketType.user)
	async def whoiss(self, ctx, user:discord.Member=None):
		await ctx.defer(ephemeral=True)
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

	@cmd.hybrid_command(with_app_command = True)
	@commands.bot_has_permissions(send_messages=True)
	@commands.cooldown(2, 8, commands.BucketType.user)
	async def toss(self, ctx):
		await ctx.defer(ephemeral=True)
		msg = f"https://cdn.discordapp.com/emojis/{random.choice(coin)}.png"
		emb = discord.Embed(color=yellow)
		emb.set_image(url=msg)
		await ctx.send(embed=emb)



	@cmd.hybrid_command(with_app_command = True)
	@commands.bot_has_permissions(send_messages=True)
	@commands.cooldown(2, 8, commands.BucketType.user)
	async def invite(self, ctx):
		await ctx.defer(ephemeral=True)
		invbtn = Button(label="Invite Now", url="https://discord.com/api/oauth2/authorize?client_id=931202912888164474&permissions=8&redirect_uri=https%3A%2F%2Fdiscord.gg%2FvMnhpAyFZm&response_type=code&scope=bot%20identify")
		view = View()
		view.add_item(invbtn)
		try:
			await ctx.send("**Click On The Button To Invite Me:**", view=view)
		except:
			return


	@cmd.hybrid_command(with_app_command = True)
	@commands.bot_has_permissions(send_messages=True)
	@commands.cooldown(2, 8, commands.BucketType.user)
	async def vote(self, ctx):
		await ctx.defer(ephemeral=True)
		invbtn = Button(label="Vote Now", url="https://top.gg/bot/931202912888164474/vote")
		view = View()
		view.add_item(invbtn)
		try:
			await ctx.send("**Click On The Button To Vote Me ^_^**", view=view)
		except:
			return


	@cmd.hybrid_command(with_app_command = True)
	@commands.bot_has_permissions(send_messages=True)
	@commands.cooldown(2, 8, commands.BucketType.user)
	async def support(self, ctx):
		await ctx.defer(ephemeral=True)
		invbtn = Button(label="Support", url="https://discord.gg/vMnhpAyFZm")
		view = View()
		view.add_item(invbtn)
		try:
			await ctx.send("**Click On The Button To Join Our Support Server For Any Issue**", view=view)
		except:
			return


	@cmd.hybrid_command(with_app_command=True, aliases=["em"])
	@commands.has_permissions(manage_messages=True)
	@commands.bot_has_permissions(send_messages=True, manage_messages=True, embed_links=True)
	@commands.cooldown(2, 10, commands.BucketType.user)
	async def embed_img(self, ctx, image, *, message):
		await ctx.defer(ephemeral=True)
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



	@cmd.hybrid_command(with_app_command = True)
	@commands.has_permissions(administrator=True)
	@commands.bot_has_permissions(send_messages=True)
	@commands.cooldown(2, 60, commands.BucketType.user)
	async def prefix(self, ctx):
		await ctx.defer(ephemeral=True)
		await ctx.send(config.prefix)



	@cmd.hybrid_command(with_app_command = True, aliases=["mc"])
	@commands.bot_has_permissions(send_messages=True)
	@commands.cooldown(2, 10, commands.BucketType.user)
	async def member_count(self, ctx):
		await ctx.defer(ephemeral=True)
		if not await config.voted(ctx, bot=self.bot):
			return await config.vtm(ctx)
		emb = discord.Embed(title="Members", description=f"{ctx.guild.member_count}", color=teal)
		emb.set_footer(text=f'Requested by - {ctx.author}', icon_url=ctx.author.avatar)
		await ctx.send(embed=emb)

		
	@cmd.hybrid_command(with_app_command = True, aliases=["ui"])
	@commands.bot_has_permissions(send_messages=True)
	async def userinfo(self, ctx, member : discord.Member = None):
		await ctx.defer(ephemeral=True)
		if member == None:
		    member = ctx.author
		roles = ", ".join([role.mention for role in member.roles][0:10])
		if len(member.roles) > 10:
			roles = "Too Many Roles To Show"
		user = await self.bot.fetch_user(member.id)
		desc = f'**User Name**: {member}\n**User ID:** {member.id}\n**Nick Name:** {member.display_name}\n**Color :** {member.color.value}\n**Status:** {member.status}\n**Bot?:** {member.bot}\n**Top role:** {member.top_role.mention}\n**Created at:** {member.created_at.strftime("%a, %#d %B %Y")}\n**Joined at:** {member.joined_at.strftime("%a, %#d %B %Y")}\n**Roles:**\n{roles} '
		embed = discord.Embed(description=desc, colour=0x00ff00, timestamp=ctx.message.created_at)
		embed.set_author(name=member, icon_url=member.avatar)
		embed.set_thumbnail(url=member.avatar)
		if user.banner:
		    embed.set_image(url=str(user.banner))
		embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)
		await ctx.send(embed=embed)


	def mmbrs(self):
	    i = 0
	    for guild in self.bot.guilds:
	        i = i + guild.member_count
	    return i

	@cmd.hybrid_command(with_app_command = True, aliases=["bi","stats", "about", "info", "status", "botstats"])
	@commands.cooldown(2, 60, commands.BucketType.user)
	@commands.bot_has_permissions(send_messages=True, embed_links=True)
	async def botinfo(self, ctx):
	    await ctx.defer(ephemeral=True)
	    emb = discord.Embed(title="Spruce Bot", description="Welcome To Spruce", color=discord.Color.blurple())
	    mmbs = self.mmbrs()
	    emb.add_field(name=f"{config.servers}__Servers Info__", value=f"Total server : {len(self.bot.guilds)}\nTotal Members : {mmbs}", inline=False)
	    emb.add_field(name=f"{config.developer} __Developer__", value="[Hunter#6967](https://discord.com/users/885193210455011369)", inline=False)
	    emb.add_field(name=f"{config.ping} __Current Ping__", value=random.choice(range(19,28)), inline=False)
	    emb.add_field(name=f"{config.setting} __Command Prefix__", value=f"command: {config.prefix}help, prefix: {config.prefix}  ", inline=False)
	    emb.set_footer(text="Made with ❤️ | By hunter#6967")
	    return await ctx.send(embed=emb)
	


	@cmd.command()
	@commands.cooldown(2, 10, commands.BucketType.user)
	@commands.bot_has_permissions(send_messages=True, manage_nicknames=True)
	async def nick(self, ctx, user:discord.Member,  *, Nick:str):
		if ctx.author.bot:
			return
		bt = ctx.guild.get_member(self.bot.user.id)
		if ctx.author.top_role < user.top_role:
			return await ctx.send("You don't have enough permission")
		if bt.top_role < user.top_role:
			return await ctx.send("I don't have enough permission")
		else:
			await user.edit(nick=Nick)
			await ctx.send("Done")


	@cmd.command(enabled=False)
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

	
	@cmd.hybrid_command(with_app_command = True, aliases=["si", "server_info"])
	@commands.cooldown(2, 10, commands.BucketType.user)
	@commands.bot_has_permissions(send_messages=True, embed_links=True)
	async def serverinfo(self, ctx):
		await ctx.defer(ephemeral=True)
		user = ctx.author
		guild = ctx.guild
		roles = ', '.join([role.mention for role in guild.roles[0:8]])
		if len(roles) > 12:
			roles = "Too Many Role To Show Here"
		emb = discord.Embed(title=f"{ctx.guild.name}'s Information",
                        description=f"**__About__**\n**Name** : {guild.name}\n**Id** : {guild.id}\n**Owner** : <@{guild.owner_id}>\n**Members** : {guild.member_count}\n**Verification Level** : {guild.verification_level}\n**Upload Limit** : {(guild.filesize_limit)/1024/1024} MB\n**Created At** : {guild.created_at.strftime('%a, %#d %B %Y, %I:%M %p')}\n\n**__Channels__**\n**Category Channels** : {len(guild.categories)}\n**Voice Channels** : {len(guild.voice_channels)}\n**Text Channels** : {len(guild.text_channels)}\n\n**__Extras__**\n**Boost Lv.** : {guild.premium_tier}\n**Emojis** : {len(guild.emojis)}/{guild.emoji_limit}\n**Stickers** : {len(guild.stickers)}/{guild.sticker_limit}\n\n**__Server Roles__ [{len(guild.roles)}]** :\n{roles}\n\n**__Description__**\n{guild.description}",
                       color=0xf1c40f)
		emb.set_thumbnail(url=guild.icon.url)
		if ctx.guild.banner:
			emb.set_image(url=ctx.guild.banner.url)
		emb.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)
		await ctx.send(embed=emb)



	
	
	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		try:
		    support_server = self.bot.get_guild(config.support_server_id)
		    ch = self.bot.get_channel(config.gjoin)
		    channel = random.choice(guild.channels)
		    orole = discord.utils.get(support_server.roles, id=1043134410029019176)
		    link = await channel.create_invite(reason=None, max_age=0, max_uses=0, temporary=False, unique=False, target_type=None, target_user=None, target_application_id=None)
		    msg= f"```py\nGuild Name : {guild.name}\nGuild Id : {guild.id}\nGuild Owner : {guild.owner}\nOwner_id : {guild.owner.id}\nMembers : {guild.member_count}```\nInvite Link : {link}"
		    if guild.member_count >= 100 and guild.owner in support_server.members:
		        m = discord.utils.get(support_server.members, id=guild.owner.id)
		        await m.add_roles(orole)
		    await ch.send(msg)
		except Exception as e:
			print(f"on_guild_join : {e}")
		
	@commands.Cog.listener()
	async def on_guild_remove(self, guild): 
	    support_server = self.bot.get_guild(config.support_server_id)
	    ch = self.bot.get_channel(config.gleave)
	    orole = discord.utils.get(support_server.roles, id=1043134410029019176)
	    msg= f"```py\nGuild Name : {guild.name}\nGuild Id : {guild.id}\nGuild Owner : {guild.owner}\nOwner_id : {guild.owner.id}\n Members : {guild.member_count}```"
	    for i in support_server.members:
	        if i.id == guild.owner.id:
	            if orole in i.roles:
	                await i.remove_roles(orole, reason="Kicked Spruce")
	    return await ch.send(msg)
	

async def setup(bot):
	await bot.add_cog(Utility(bot))