"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2022 hunter87.dev@gmail.com
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.
 """


import datetime
import os, random, requests, enum, uuid, psutil
from discord.ext import commands
from modules import config
from discord.ui import Button, View 
from gtts import gTTS
from discord import (
    Embed,
    User, 
    File, 
    PartialEmoji, 
    Guild, 
    Member, 
    app_commands, 
    Interaction, 
    utils, 
    PermissionOverwrite, 
    ButtonStyle, 
    Role, 
    Emoji
)




whois = ["Noob","Unknown Person","kya pata mai nehi janta","bohot piro", "Bohot E-smart","Dusro Ko Jan Ne Se Pehle Khud Ko Jan Lo","Nalla", "Bohot achha","bohooooooooot badaaaaa Bot","Nehi bolunga kya kar loge", "insan", "bhoot", "bhagwan", "e-smart ultra pro max"]
coin = ["975413333291335702", "975413366493413476"]
maindb = config.maindb
nitrodbc = maindb["nitrodb"]["nitrodbc"]
def trn(token, fr:str, to:str, text:str):
	print({"api-version":"3.0", "from":fr, "to":to})
	api = "https://api.cognitive.microsofttranslator.com/translate"
	headers = {
				'Ocp-Apim-Subscription-Key': token,
				'Ocp-Apim-Subscription-Region': 'centralindia',
				'Content-type': 'application/json',
				'X-ClientTraceId': str(uuid.uuid4()),
			}
	res = requests.post(api, params={"api-version":"3.0", "from":fr, "to":to}, headers=headers, json=[{"text":text}])
	if res.status_code==200: return res.json()[0]["translations"][0]["text"]
	else: return "Something went wrong! please try again later."
	
class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot:commands.Bot = bot
        self.counter = 0

    class NaturalLang(enum.Enum):
        Afrikaans = "af"
        Arabic = "ar"
        Assamese = "as"
        Bengali = "bn"
        Chinese = "zh-Hans"
        English = "en"
        French = "fr"
        Greek = "el"
        Gujarati = "gu"
        Hindi = "hi"
        Japanese = "ja"
        Kannada = "kn"
        Marathi = "mr"
        Nepali = "ne"
        Odia = "or"
        Polish = "pl"
        Portuguese = "pt"
        Punjabi = "pa"
        Russian = "ru"
        Spanish = "es"
        Vietnamese = "vi"

    @app_commands.command()
    async def translate(self, interaction:Interaction, fr:NaturalLang, to:NaturalLang, *, message:str):
        return await interaction.response.send_message(embed=Embed(description=trn(config.cfdata["trnsl"], fr.value, to.value, message), color=config.blurple), ephemeral=True)



    @commands.hybrid_command(with_app_command = True)
    @commands.cooldown(2, 60, commands.BucketType.user)
    async def uptime(self, ctx:commands.Context):
        if ctx.author.bot:return
        if not await config.voted(ctx, bot=self.bot):
            return await config.vtm(ctx)
        await ctx.defer(ephemeral=True)
        try:sch = self.bot.get_channel(config.stl)
        except Exception:return
        messages = [message async for message in sch.history(limit=3)]
        uptime = ctx.message.created_at - messages[0].created_at
        upt = str(uptime).split(".")[0]
        msg = f"**Current Uptime Is : `{upt}`**"
        emb = Embed(title="Uptime", color=config.green, description=msg, timestamp=ctx.message.created_at)
        emb.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar)
        try:await ctx.send(embed=emb)
        except Exception:return


    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    @commands.cooldown(2, 60, commands.BucketType.user)
    async def ping(self, ctx):
        await ctx.reply(embed=Embed(description=f'**{config.dot_green} Current Response Time : `{round(self.bot.latency*1000)}ms`**', color=config.green))
        # else:await ctx.reply(embed=Embed(description=f'**{config.ping}Current Response Time : `{round(self.bot.latency*1000)}MS`**'))



    @commands.hybrid_command(with_app_command = True, aliases=['av', "pfp"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def avatar(self, ctx:commands.Context, user: User = None):
        if ctx.author.bot:return
        if not await config.voted(ctx, bot=self.bot):
            return await config.vtm(ctx)
        await ctx.defer(ephemeral=True)
        user = user or ctx.author
        if "a_" in str(user.avatar):
            eemb = Embed(title=user, description=f"[JPG]({user.display_avatar.with_format('jpg')}) | [PNG]({user.display_avatar.with_format('png')}) | [GIF]({user.display_avatar})", color=0xfff00f)			
            eemb.set_image(url=user.avatar)
            eemb.set_footer(text=f"Requested By {ctx.author}")
            return await ctx.send(embed=eemb)
        else:
            eemb = Embed(title=user, description=f"[JPG]({user.display_avatar.with_format('jpg')}) | [PNG]({user.display_avatar.with_format('png')})", color=0x00fff0)
            eemb.set_image(url=user.display_avatar)
            eemb.set_footer(text=f"Requested By {ctx.author}")
            return await ctx.send(embed=eemb)
            



    @commands.hybrid_command(with_app_command = True, aliases=['sav'])
    @commands.bot_has_permissions(embed_links=True)
    async def server_av(self, ctx:commands.Context, guild:Guild=None):
        await ctx.defer(ephemeral=True)
        if not await config.voted(ctx, bot=self.bot):
            return await config.vtm(ctx)
        guild = guild or ctx.guild
        if guild.icon != None:
            enm = Embed(title=guild.name, url=guild.icon, color=config.red)
            enm.set_image(url=guild.icon)
            await ctx.send(embed=enm)

        if guild.icon == None:
            return await ctx.reply("**Server Don't Have A Logo XD**", delete_after=10)



    @commands.hybrid_command(with_app_command = True, aliases=["bnr"])
    async def banner(self, ctx:commands.Context, user:User=None):
        if ctx.author.bot:return
        if not await config.voted(ctx, bot=self.bot):
            return await config.vtm(ctx)
        if user == None:user = ctx.author
        usr = await self.bot.fetch_user(user.id)
        banner = usr.banner
        if not banner:return await ctx.reply("User Don't Have A Banner", delete_after=20)
        banner_url = banner.url
        emb = Embed(colour=0xff0000, description=f"**[BANNER URL]({banner_url})**")
        emb.set_image(url=banner_url)
        await ctx.send(embed=emb)


    @commands.command(aliases=['emb'])
    @commands.bot_has_permissions(send_messages=True, manage_messages=True)
    @commands.cooldown(2, 60, commands.BucketType.user)
    async def embed(self, ctx:commands.Context, *, message):
        await ctx.defer()
        if ctx.author.bot:return
        if not await config.voted(ctx, bot=self.bot):
            return await config.vtm(ctx)
        embed = Embed(description=message, color=config.blue)
        await ctx.channel.purge(limit=1)
        await ctx.send(embed=embed)


    @commands.hybrid_command(with_app_command = True)
    @commands.cooldown(2, 60, commands.BucketType.user)
    async def tts(self, ctx:commands.Context, *, message:str):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:return
        if not await config.voted(ctx, bot=self.bot):return await config.vtm(ctx)
        if len(message.split()) > 150 and len(message)<=1000:
            return await ctx.reply("**Up to 100 words allowed**", delete_after=30)
        output = gTTS(text=message, lang="en", tld="co.in")
        file_name = f"tts_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.ogg"
        output.save(file_name)
        await ctx.send(ctx.author.mention, file=File(file_name))
        os.remove(file_name)


    @commands.hybrid_command(with_app_command = True)
    @commands.guild_only()
    @commands.bot_has_permissions(manage_emojis=True)
    @commands.has_permissions(manage_emojis=True)
    async def addemoji(self, ctx:commands.Context, emoji: PartialEmoji):
        await ctx.defer(ephemeral=True)
        emoji_bytes = await emoji.read()
        new = await ctx.guild.create_custom_emoji(name=emoji.name, image=emoji_bytes, reason=f'Emoji Added By {ctx.author}')
        return await ctx.send(f"{new} added", delete_after=10)


    @commands.hybrid_command(with_app_command = True)
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def whoiss(self, ctx:commands.Context, user:Member=None):
        await ctx.defer(ephemeral=True)
        if not user:
            user = ctx.author
            msg = random.choice(whois)
        if user.bot == True:
            return await ctx.send("**Bot is always awesome**")
        elif user.id == 885193210455011369:
            owneremb = Embed(description=f"{user.mention} **Best Friend :heart:**", color=config.blue)
            return await ctx.send(embed=owneremb)
        else:
            msg = random.choice(whois)
            emb = Embed(description=f"{user.mention}  {msg}", color=config.blurple)
            await ctx.send(embed=emb)

    @commands.hybrid_command(with_app_command = True)
    @commands.bot_has_permissions(send_messages=True)
    @commands.cooldown(2, 8, commands.BucketType.user)
    async def toss(self, ctx):
        await ctx.defer(ephemeral=True)
        msg = f"https://cdn.discordapp.com/emojis/{random.choice(coin)}.png"
        emb = Embed(color=config.yellow)
        emb.set_image(url=msg)
        await ctx.send(embed=emb)



    @commands.hybrid_command(with_app_command = True)
    @commands.bot_has_permissions(send_messages=True)
    @commands.cooldown(2, 8, commands.BucketType.user)
    async def invite(self, ctx):
        await ctx.defer(ephemeral=True)
        invbtn = Button(label="Invite Now", url=config.invite_url2)
        view = View()
        view.add_item(invbtn)
        try:await ctx.send("**Click On The Button To Invite Me:**", view=view)
        except Exception:return

    @commands.hybrid_command(with_app_command = True)
    @commands.bot_has_permissions(send_messages=True)
    @commands.cooldown(2, 8, commands.BucketType.user)
    async def vote(self, ctx):
        await ctx.defer(ephemeral=True)
        invbtn = Button(label="Vote Now", url="https://top.gg/bot/931202912888164474/vote")
        view = View()
        view.add_item(invbtn)
        try:await ctx.send("**Click On The Button To Vote Me ^_^**", view=view)
        except Exception:return

    @commands.hybrid_command(with_app_command = True)
    @commands.bot_has_permissions(send_messages=True)
    @commands.cooldown(2, 8, commands.BucketType.user)
    async def support(self, ctx):
        await ctx.defer(ephemeral=True)
        invbtn = Button(label="Support", url="https://discord.gg/vMnhpAyFZm")
        view = View()
        view.add_item(invbtn)
        try:await ctx.send("**Click On The Button To Join Our Support Server For Any Issue**", view=view)
        except Exception:return

    @commands.hybrid_command(with_app_command=True, aliases=["em"])
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(send_messages=True, manage_messages=True, embed_links=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def embed_img(self, ctx:commands.Context, image, *, message):
        await ctx.defer(ephemeral=True)
        emb = Embed(description=message, color=config.blue)
        emb.set_image(url=image)
        await ctx.channel.purge(limit=1)
        await ctx.send(embed=emb) 


    @commands.command()
    @commands.cooldown(2, 360, commands.BucketType.user)
    @commands.has_permissions(add_reactions=True)
    @commands.bot_has_permissions(add_reactions=True)
    async def react(self, ctx:commands.Context, msg_id, *emojis):
        for emoji in emojis:
            msg = await ctx.channel.fetch_message(msg_id)
            await ctx.channel.purge(limit=1)
            await msg.add_reaction(emoji)



    @commands.hybrid_command(with_app_command = True)
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(send_messages=True)
    @commands.cooldown(2, 60, commands.BucketType.user)
    async def prefix(self, ctx):
        await ctx.defer(ephemeral=True)
        await ctx.send(f"My prefix is : {config.prefix}")

    @commands.hybrid_command(with_app_command = True, aliases=["mc"])
    @commands.bot_has_permissions(send_messages=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def member_count(self, ctx):
        await ctx.defer(ephemeral=True)
        if not await config.voted(ctx, bot=self.bot):return await config.vtm(ctx)
        emb = Embed(title="Members", description=f"{ctx.guild.member_count}", color=config.teal)
        emb.set_footer(text=f'Requested by - {ctx.author}', icon_url=ctx.author.avatar)
        await ctx.send(embed=emb)

        
    @commands.hybrid_command(with_app_command = True, aliases=["ui"])
    @commands.bot_has_permissions(send_messages=True)
    async def userinfo(self, ctx:commands.Context, member : Member = None):
        await ctx.defer(ephemeral=True)
        if member == None:member = ctx.author
        roles = ", ".join([role.mention for role in member.roles][0:10])
        if len(member.roles) > 15:roles = "Too Many Roles To Show"
        user = await self.bot.fetch_user(member.id)
        desc = f'**User Name**: {member}\n**User ID:** {member.id}\n**Nick Name:** {member.display_name}\n**Color :** {member.color.value}\n**Status:** {member.status}\n**Bot?:** {member.bot}\n**Top role:** {member.top_role.mention}\n**Created at:** {member.created_at.strftime("%a, %#d %B %Y")}\n**Joined at:** {member.joined_at.strftime("%a, %#d %B %Y")}\n**Roles:**\n{roles} '
        embed = Embed(description=desc, colour=0x00ff00, timestamp=ctx.message.created_at)
        embed.set_author(name=member, icon_url=member.avatar)
        embed.set_thumbnail(url=member.avatar)
        if user.banner:embed.set_image(url=str(user.banner))
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)
        await ctx.send(embed=embed)
 
    def mmbrs(self):
        return sum(guild.member_count for guild in self.bot.guilds)    

    @commands.hybrid_command(with_app_command = True, aliases=["bi","stats", "about", "info", "status", "botstats"])
    @commands.cooldown(2, 60, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def botinfo(self, ctx:commands.Context):
        if ctx.author.bot:return
        await ctx.defer(ephemeral=True)
        memory = psutil.virtual_memory()
        # cpu_usage = psutil.cpu_percent()
        # disk = psutil.disk_usage('/')
        #\nCPU Cores : {psutil.cpu_count(logical=False)+psutil.cpu_count(logical=True)}\nCPU Usage : {cpu_usage}%\nTotal Disk: {disk.total//10**9} GB
        mem_percent = f"{(psutil.Process(os.getpid()).memory_percent()):.2f}"
        system_info = f"`{memory.total / (1024**3):.2f} GB`/ `{psutil.Process(os.getpid()).memory_info().rss//2**20} MB`/ `{mem_percent}%`"
        emb = Embed(title="Spruce Bot", color=config.green)
        emb.add_field(name=f"{config.servers} __Servers__", value=f"`{len(self.bot.guilds)}`", inline=True)
        emb.add_field(name=f"{config.invite} __Members__", value=f"`{'{:,}'.format(self.mmbrs())}`", inline=True)
        emb.add_field(name=f"{config.wifi} __Latency__", value=f"`{round(self.bot.latency*1000)}ms`", inline=True)
        # emb.add_field(name=f"{config.developer} __Developer__", value="[hunter87ff](https://discord.com/users/885193210455011369)", inline=False)
        # emb.add_field(name=f"{config.setting} __Command Prefix__", value=f"Command: {config.prefix}help, prefix: {config.prefix}  ", inline=False)
        emb.add_field(name=f"{config.ram} __Memory(Total/Usage/Percent)__", value=f"{system_info}", inline=False)
        emb.set_footer(text="Made with ❤️ | By hunter87ff")
        return await ctx.send(embed=emb)
    
    @commands.command()
    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True, manage_nicknames=True)
    async def nick(self, ctx:commands.Context, user:Member,  *, Nick:str):
        if ctx.author.bot:return
        bt = ctx.guild.get_member(self.bot.user.id)
        if ctx.author.top_role < user.top_role:return await ctx.send("You don't have enough permission")
        if bt.top_role < user.top_role:return await ctx.send("I don't have enough permission")
        else:
            await user.edit(nick=Nick)
            await ctx.send("Done")


    @commands.command(enabled=False)
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


    @commands.hybrid_command(with_app_command = True, aliases=["si", "server_info"])
    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def serverinfo(self, ctx:commands.Context):
        await ctx.defer(ephemeral=True)
        guild = ctx.guild
        roles = ', '.join([role.mention for role in guild.roles[::-1][:20]])
        if len(roles) > 20:roles += "..."
        emb = Embed(title=f"{ctx.guild.name}'s Information",description=f"**__About__**\n**Name** : {guild.name}\n**Id** : {guild.id}\n**Owner** : <@{guild.owner_id}>\n**Members** : {guild.member_count}\n**Verification Level** : {guild.verification_level}\n**Upload Limit** : {(guild.filesize_limit)/1024/1024} MB\n**Created At** : {guild.created_at.strftime('%a, %#d %B %Y, %I:%M %p')}\n\n**__Channels__**\n**Category Channels** : {len(guild.categories)}\n**Voice Channels** : {len(guild.voice_channels)}\n**Text Channels** : {len(guild.text_channels)}\n\n**__Extras__**\n**Boost Lv.** : {guild.premium_tier}\n**Emojis** : {len(guild.emojis)}/{guild.emoji_limit}\n**Stickers** : {len(guild.stickers)}/{guild.sticker_limit}\n\n**__Server Roles__ [{len(guild.roles)}]** :\n{roles}\n\n**__Description__**\n{guild.description}",color=0xf1c40f)
        emb.set_thumbnail(url=guild.icon.url)
        if ctx.guild.banner:emb.set_image(url=ctx.guild.banner.url)
        emb.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)
        await ctx.send(embed=emb)




    class Buttons(enum.Enum):
        green = ButtonStyle.green
        red = ButtonStyle.red
        grey = ButtonStyle.grey
        blurple = ButtonStyle.blurple


    @commands.hybrid_command(with_app_command = True)
    @commands.cooldown(2, 60, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True, embed_links=True, manage_messages=True, manage_channels=True, manage_roles=True)
    async def setup_ticket(self, ctx:commands.Context, mod_role:Role=None, button_label:str=None, button_emoji:Emoji=None, button_color:Buttons=None, *, message:str=None):
        if ctx.author.bot:return
        if config.prefix in ctx.message.content:return await ctx.reply("Use Slash Command to manage other properties!!", delete_after=10)
        await ctx.defer(ephemeral=True)
        ms = await ctx.send("Creating Ticket Category...")
        overwrites = {
            ctx.guild.default_role: PermissionOverwrite(read_messages=False),
            ctx.guild.me: PermissionOverwrite(read_messages=True),
        }
        if mod_role:overwrites[mod_role] = PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True)
        category = await ctx.guild.create_category("Tickets", overwrites=overwrites)
        ticketChannel = await category.create_text_channel("create-ticket")
        await ms.edit(content="Creating Ticket Channel...")
        await ticketChannel.set_permissions(ctx.guild.default_role, read_messages=True, send_messages=False)
        await ms.edit(content="Creating Ticket Message...")
        embed = Embed(title="Create Ticket", description="Click on the button to create a ticket!!", color=config.green)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url)
        if not button_color:button_color = ButtonStyle.blurple
        else:button_color = button_color.value
        view = View().add_item(Button(emoji=button_emoji or config.default_ticket, label=button_label or "Create Ticket", style=button_color, custom_id=f"{self.bot.user.id}SPticket"))
        await ms.edit(content="Sending Ticket Message...")
        await ticketChannel.send(embed=embed, view=view)
        await ms.edit(content="Ticket System Setup Done")



    @commands.Cog.listener()
    async def on_interaction(self, interaction:Interaction):
        if interaction.user.bot:return
        if "custom_id" not in interaction.data or interaction.message.author.id != self.bot.user.id: return
        if interaction.data["custom_id"] == f"{self.bot.user.id}SPticket":
            if not interaction.channel.category: return await interaction.response.send_message("**Please move this channel to a category. to create tickets**", delete_after=10)
            channel = await interaction.channel.category.create_text_channel(f"ticket-{interaction.user}", reason="Ticket Created")
            await channel.set_permissions(interaction.user, read_messages=True, send_messages=True, attach_files=True, embed_links=True, read_message_history=True, add_reactions=True)
            embed = Embed(title="Ticket Created", description=f"**{config.arow}Thanks for contacting\n{config.arow}Feel free to communicate**", color=config.green)
            view = View().add_item(Button(label="Close Ticket", style=ButtonStyle.red, custom_id=f"{self.bot.user.id}SPTcancel"))
            await channel.send(f"<@{interaction.user.id}>", embed=embed, view=view)
            await interaction.response.send_message(f"**Ticket <#{channel.id}> Created Successfully**", ephemeral=True, delete_after=10)

        if interaction.data["custom_id"] == f"{self.bot.user.id}SPTcancel":
            closeConfirm = Button(label="Confirm", style=ButtonStyle.red)
            closeCancel = Button(label="Cancel", style=ButtonStyle.green)
            view = View()
            view.add_item(closeConfirm); view.add_item(closeCancel)
            await interaction.response.send_message(embed=Embed(description="Are You Sure?", color=config.red), view=view, delete_after=10)

            async def closeTicket(interaction:Interaction):
                await interaction.response.send_message(embed=Embed(description="Closing Ticket...", color=config.red), ephemeral=True)
                await interaction.channel.delete(reason="Ticket Closed")

            async def cancelClose(interaction:Interaction):
                await interaction.message.delete()

            closeConfirm.callback = closeTicket
            closeCancel.callback = cancelClose


    @commands.Cog.listener()
    async def on_guild_join(self, guild:Guild):
        try:
            support_server = self.bot.get_guild(config.support_server_id)
            ch = self.bot.get_channel(config.gjoin)
            channel = random.choice(guild.channels)
            orole = utils.get(support_server.roles, id=1043134410029019176)
            link = await channel.create_invite(reason=None, max_age=0, max_uses=0, temporary=False, unique=False, target_type=None, target_user=None, target_application_id=None)
            msg= f"```py\nGuild Name : {guild.name}\nGuild Id : {guild.id}\nGuild Owner : {guild.owner}\nOwner_id : {guild.owner.id}\nMembers : {guild.member_count}```\nInvite Link : {link}"
            if guild.member_count >= 100 and guild.owner in support_server.members:
                m = utils.get(support_server.members, id=guild.owner.id)
                await m.add_roles(orole)
            await ch.send(msg)
        except Exception as e:print(f"on_guild_join : {e}")
        

    @commands.Cog.listener()
    async def on_guild_remove(self, guild): 
        support_server = self.bot.get_guild(config.support_server_id)
        ch = self.bot.get_channel(config.gleave)
        orole = utils.get(support_server.roles, id=1043134410029019176)
        msg= f"```py\nGuild Name : {guild.name}\nGuild Id : {guild.id}\nGuild Owner : {guild.owner}\nOwner_id : {guild.owner.id}\n Members : {guild.member_count}```"
        for i in support_server.members:
            if i.id == guild.owner.id and orole in i.roles:await i.remove_roles(orole, reason="Kicked Spruce")
        return await ch.send(msg)


async def setup(bot):
	await bot.add_cog(Utility(bot))
