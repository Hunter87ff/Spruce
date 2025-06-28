"""
A module for utility commands in the Spruce bot.
    :author: hunter87
    :copyright: (c) 2022-present hunter87.dev@gmail.com
    :license: GPL-3, see LICENSE for more details.
"""


import discord
import os, random, enum, psutil
from discord.ext import commands
from typing import TYPE_CHECKING
from discord.ui import Button, View 
from gtts import gTTS
from ext import constants, emoji, color, ColorOptions


if TYPE_CHECKING:
    from modules.bot import Spruce

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


	

class UtilityCog(commands.Cog):
    def __init__(self, bot:"Spruce"):
        self.bot = bot
       


    @app_commands.command(name="translate", description="Translate a message from one language to another")
    @app_commands.describe(
        from_lang="Language to translate from",
        to_lang="Language to translate to",
        message="Message to translate"
    )
    @app_commands.checks.cooldown(2, 50, key=lambda i: i.user.id)
    async def translate(self, interaction:Interaction, from_lang:constants.NaturalLang, to_lang:constants.NaturalLang, *, message:str):
        return await interaction.response.send_message(
            embed=Embed(
                description=await self.bot.helper.translate(self.bot.config.TRANSLATE_KEY, from_lang.value, to_lang.value, message), 
                color=color.blurple
            ), ephemeral=True
        )



    @commands.hybrid_command(description="Get the current uptime of the bot")
    @commands.guild_only()
    @commands.cooldown(2, 60, commands.BucketType.user)
    async def uptime(self, ctx:commands.Context):
        if ctx.author.bot:return
        
        await ctx.defer(ephemeral=True)
        try:sch = self.bot.get_channel(self.bot.config.client_start_log)
        except Exception:return
        messages = [message async for message in sch.history(limit=3)]
        uptime = ctx.message.created_at - messages[0].created_at
        upt = str(uptime).split(".")[0]
        msg = f"**Current Uptime Is : `{upt}`**"
        emb = Embed(title="Uptime", color=color.green, description=msg, timestamp=ctx.message.created_at)
        emb.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar)
        try:await ctx.send(embed=emb)
        except Exception:return


    @commands.hybrid_command(name="sync", description="Syncs the commands to the server")
    @commands.cooldown(1, 15, commands.BucketType.guild)
    async def sync(self, ctx: commands.Context):
        await ctx.defer()
        if ctx.author.bot:return
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)
        
        await ctx.send("Syncing commands...")
        try:
            await self.bot.tree.sync(guild=ctx.guild)
            await ctx.send("Commands synced successfully!")
        except Exception as e:
            await ctx.send(f"Failed to sync commands: {e}")
            self.bot.logger.error(f"Failed to sync commands: {e}")


    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    @commands.cooldown(2, 60, commands.BucketType.user)
    async def ping(self, ctx:commands.Context):
        await ctx.reply(
            embed=Embed(
                description=f'**{emoji.dot_green} Latency : `{round(self.bot.latency*1000)}ms`**', 
                color=color.green
            )
        )



    @commands.hybrid_command(description="Get the avatar of a user", aliases=['av', "pfp"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def avatar(self, ctx:commands.Context, user: User = None):
        if ctx.author.bot:return
        
        await ctx.defer(ephemeral=True)
        user = user or ctx.author
        if "a_" in str(user.avatar):
            eemb = Embed(
                title=user, 
                description=f"[JPG]({user.display_avatar.with_format('jpg')}) | [PNG]({user.display_avatar.with_format('png')}) | [GIF]({user.display_avatar})", 
                color=0xfff00f
            )			
            eemb.set_image(url=user.avatar)
            eemb.set_footer(text=f"Requested By {ctx.author}")
            return await ctx.send(embed=eemb)
        else:
            eemb = Embed(
                title=user, 
                description=f"[JPG]({user.display_avatar.with_format('jpg')}) | [PNG]({user.display_avatar.with_format('png')})",
                color=0x00fff0
            )
            eemb.set_image(url=user.display_avatar)
            eemb.set_footer(text=f"Requested By {ctx.author}")
            return await ctx.send(embed=eemb)
            



    @commands.hybrid_command(description="Get the server avatar", aliases=['sav'])
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def server_av(self, ctx:commands.Context, guild:Guild=None):
        await ctx.defer(ephemeral=True)
        
        guild = guild or ctx.guild
        if guild.icon != None:
            enm = Embed(title=guild.name, url=guild.icon, color=color.red)
            enm.set_image(url=guild.icon)
            await ctx.send(embed=enm)

        if guild.icon == None:
            return await ctx.reply("**Server Don't Have A Logo XD**", delete_after=10)



    @commands.hybrid_command(description="Get the banner of a user", aliases=["bnr"])
    async def banner(self, ctx:commands.Context, user:User=None):
        if ctx.author.bot:return
        
        if user == None:user = ctx.author
        usr = await self.bot.fetch_user(user.id)
        banner = usr.banner
        if not banner:return await ctx.reply("User Don't Have A Banner", delete_after=20)
        banner_url = banner.url
        emb = Embed(colour=0xff0000, description=f"**[BANNER URL]({banner_url})**")
        emb.set_image(url=banner_url)
        await ctx.send(embed=emb)



    @app_commands.command(name="embed", description="Create an embed message")
    @app_commands.describe(
        title="Title of the embed",
        description="Description of the embed",
        color="Color of the embed (hex code or color name)",
        footer="Footer text for the embed",
        thumbnail="Thumbnail image URL",
        image="Main image URL"

    )
    @app_commands.checks.cooldown(2, 60, key=lambda i: i.user.id)
    async def embed_command(
        self, 
        interaction: Interaction, 
        title: str="Title", 
        description: str="Description", 
        color:ColorOptions = ColorOptions.teal, 
        footer: str="Footer",
        thumbnail: str=None,
        image: str=None,
        channel: discord.TextChannel=None
        ):
        channel = channel or interaction.channel
        embed = Embed(title=title, description=description, color=color.value)

        if self.bot.validator.is_valid_url(thumbnail):
            embed.set_thumbnail(url=thumbnail)

        if self.bot.validator.is_valid_url(image):
            embed.set_image(url=image)
            
        embed.set_footer(text=footer)
        await channel.send(embed=embed)
        await interaction.response.send_message(
            f"Embed sent to {channel.mention}", 
            embed=embed,
            ephemeral=True
        )



    @commands.hybrid_command(description="Convert text to speech")
    @commands.cooldown(2, 60, commands.BucketType.user)
    async def tts(self, ctx:commands.Context, *, message:str):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:
            return
        
        bws:set[str] = set(self.bot.db.blocked_words)

        if len(message.split()) > 150 and len(message)<=1000:
            return await ctx.reply("**Up to 100 words allowed**", delete_after=30)
        
        if bws.intersection(set(message.split())):
            for i in bws.intersection(set(message.split())):
                message = message.replace(i, random.choice(constants.bws_replacement))

        output = gTTS(text=message, lang="en", tld="co.in")
        file_name = f"tts_{self.bot.time.now().timestamp()}_{ctx.author.id}.ogg"
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
        msg:str = ""
        if not user:
            user = ctx.author
            msg = random.choice(constants.whois)
        if user.bot == True:
            return await ctx.send("**Bot is always awesome**")
        elif user.id == self.bot.config.OWNER_ID:
            owneremb = Embed(description=f"{user.mention} **Best Friend :heart:**", color=color.blue)
            return await ctx.send(embed=owneremb)
        else:
            msg = random.choice(constants.whois)
            emb = Embed(description=f"{user.mention}  {msg}", color=color.blurple)
            await ctx.send(embed=emb)



    @commands.hybrid_command(with_app_command = True)
    @commands.bot_has_permissions(send_messages=True)
    @commands.cooldown(2, 8, commands.BucketType.user)
    async def toss(self, ctx:commands.Context):
        await ctx.defer(ephemeral=True)
        msg = f"https://cdn.discordapp.com/emojis/{random.choice(constants.coin)}.png"
        emb = Embed(color=color.yellow)
        emb.set_image(url=msg)
        await ctx.send(embed=emb)



    @commands.hybrid_command(with_app_command = True)
    @commands.bot_has_permissions(send_messages=True)
    @commands.cooldown(2, 8, commands.BucketType.user)
    async def invite(self, ctx:commands.Context):
        await ctx.defer(ephemeral=True)
        invbtn = Button(label="Invite Now", url=self.bot.config.INVITE_URL)
        view = View()
        view.add_item(invbtn)
        try:await ctx.send("**Click On The Button To Invite Me:**", view=view)
        except Exception:return



    @commands.hybrid_command(with_app_command = True)
    @commands.bot_has_permissions(send_messages=True)
    @commands.cooldown(2, 8, commands.BucketType.user)
    async def vote(self, ctx:commands.Context):
        await ctx.defer(ephemeral=True)
        invbtn = Button(label="Vote Now", url="https://top.gg/bot/931202912888164474/vote")
        view = View()
        view.add_item(invbtn)
        try:await ctx.send("**Click On The Button To Vote Me ^_^**", view=view)
        except Exception:return



    @commands.hybrid_command(with_app_command = True)
    @commands.bot_has_permissions(send_messages=True)
    @commands.cooldown(2, 8, commands.BucketType.user)
    async def support(self, ctx:commands.Context):
        await ctx.defer(ephemeral=True)
        invbtn = Button(label="Support", url="https://discord.gg/vMnhpAyFZm")
        view = View()
        view.add_item(invbtn)
        try:await ctx.send("**Click On The Button To Join Our Support Server For Any Issue**", view=view)
        except Exception:return



    @commands.hybrid_command(with_app_command=True, aliases=["em"])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(send_messages=True, manage_messages=True, embed_links=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def embed_img(self, ctx:commands.Context, image:str, *, message:str):
        await ctx.defer(ephemeral=False)

        # validate image url
        if self.bot.validator.is_valid_url(image) is False:
            return await ctx.send("**Invalid image URL provided. Please provide a valid image URL.**", delete_after=10)

        emb = Embed(description=message, color=self.bot.color.random())
        emb.set_image(url=image)

        if ctx.message and ctx.guild.me.guild_permissions.manage_messages:
            await ctx.message.delete()

        await ctx.send(embed=emb)


    @commands.hybrid_command(description="Get the current prefix of the bot", aliases=["pr"])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(send_messages=True)
    @commands.cooldown(2, 60, commands.BucketType.user)
    async def prefix(self, ctx:commands.Context):
        await ctx.defer(ephemeral=True)
        await ctx.send(f"My prefix is : {self.bot.config.PREFIX}")


    @commands.hybrid_command(description="Get the current member count of the server", aliases=["mc"])
    @commands.guild_only()
    @commands.bot_has_permissions(send_messages=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def member_count(self, ctx:commands.Context):
        await ctx.defer(ephemeral=True)
        
        emb = Embed(title="Members", description=f"{ctx.guild.member_count}", color=color.teal)
        emb.set_footer(text=f'Requested by - {ctx.author}', icon_url=ctx.author.avatar)
        await ctx.send(embed=emb)


    @commands.hybrid_command(description="Get information about a user", aliases=["ui"])
    @commands.guild_only()
    @commands.cooldown(2, 30, commands.BucketType.user)
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
 


    @commands.hybrid_command(with_app_command = True, aliases=["bi","stats", "about", "info", "status", "botstats"])
    @commands.cooldown(2, 60, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def botinfo(self, ctx:commands.Context):
        if ctx.author.bot:return
        await ctx.defer(ephemeral=True)
        memory = psutil.virtual_memory()
        mem_percent = f"{(psutil.Process(os.getpid()).memory_percent()):.2f}"
        system_info = f"`{memory.total / (1024**3):.2f} GB`/ `{psutil.Process(os.getpid()).memory_info().rss//2**20} MB`/ `{mem_percent}%`"
        emb = Embed(title="Spruce Bot", color=color.green)
        emb.add_field(name=f"{emoji.servers} __Servers__", value=f"`{len(self.bot.guilds)}`", inline=True)
        emb.add_field(name=f"{emoji.invite} __Members__", value=f"`{'{:,}'.format(len(self.bot.users))}`", inline=True)
        emb.add_field(name=f"{emoji.wifi} __Latency__", value=f"`{round(self.bot.latency*1000)}ms`", inline=True)
        emb.add_field(name=f"{emoji.ram} __Memory(Total/Usage/Percent)__", value=f"{system_info}", inline=False)
        emb.set_footer(text="Made with ❤️ | By hunter87ff")
        return await ctx.send(embed=emb)
    


    @app_commands.command(name="nick", description="Change a user's nickname")
    @app_commands.describe(
        user="The user whose nickname you want to change",
        nickname="The new nickname for the user"
    )
    @app_commands.checks.cooldown(2, 10, key=lambda i: i.user.id)
    @app_commands.default_permissions(manage_nicknames=True)
    @app_commands.guild_only()
    async def nick(self, interaction: Interaction, user: Member, nickname: str):
        if interaction.user.bot:
            return
        
        if interaction.user.top_role < user.top_role:
            return await interaction.response.send_message("You don't have enough permission", ephemeral=True)

        if interaction.guild.me.top_role < user.top_role:
            return await interaction.response.send_message("I don't have enough permission as ", ephemeral=True)
        
        try:
            await user.edit(nick=nickname)
            await interaction.response.send_message(f"Successfully changed {user.mention}'s nickname to `{nickname}`", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to change that user's nickname", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)



    @commands.hybrid_command(description="Get information about the server", aliases=["si", "server_info"])
    @commands.guild_only()
    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def serverinfo(self, ctx:commands.Context):
        await ctx.defer(ephemeral=True)
        guild = ctx.guild
        roles = ', '.join([role.mention for role in guild.roles[::-1][:20]])
        if len(roles) > 20:roles += "..."
        emb = Embed(title=f"{ctx.guild.name}'s Information",description=f"**__About__**\n**Name** : {guild.name}\n**Id** : {guild.id}\n**Owner** : <@{guild.owner_id}>\n**Members** : {guild.member_count}\n**Verification Level** : {guild.verification_level}\n**Upload Limit** : {(guild.filesize_limit)/1024/1024} MB\n**Created At** : {guild.created_at.strftime('%a, %#d %B %Y, %I:%M %p')}\n\n**__Channels__**\n**Category Channels** : {len(guild.categories)}\n**Voice Channels** : {len(guild.voice_channels)}\n**Text Channels** : {len(guild.text_channels)}\n\n**__Extras__**\n**Boost Lv.** : {guild.premium_tier}\n**Emojis** : {len(guild.emojis)}/{guild.emoji_limit}\n**Stickers** : {len(guild.stickers)}/{guild.sticker_limit}\n\n**__Server Roles__ [{len(guild.roles)}]** :\n{roles}\n\n**__Description__**\n{guild.description}",color=0xf1c40f)
        emb.set_thumbnail(url=guild.icon.url or self.bot.user.avatar.url)
        if ctx.guild.banner:emb.set_image(url=ctx.guild.banner.url)
        emb.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)
        await ctx.send(embed=emb)




    class Buttons(enum.Enum):
        green = ButtonStyle.green
        red = ButtonStyle.red
        grey = ButtonStyle.grey
        blurple = ButtonStyle.blurple


    @commands.hybrid_command(with_app_command = True)
    @commands.guild_only()
    @commands.cooldown(2, 60, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True, embed_links=True, manage_messages=True, manage_channels=True, manage_roles=True)
    async def setup_ticket(self, ctx:commands.Context, mod_role:Role=None, button_label:str=None, button_emoji:Emoji=None, button_color:Buttons=None, *, message:str=None):
        if ctx.author.bot:return
        if self.bot.config.PREFIX in ctx.message.content:
            return await ctx.reply("Use Slash Command to manage other properties!!", delete_after=10)
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
        embed = Embed(title="Create Ticket", description="Click on the button to create a ticket!!", color=color.green)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url)
        if not button_color:button_color = ButtonStyle.blurple
        else:button_color = button_color.value
        view = View().add_item(Button(emoji=button_emoji or emoji.default_ticket, label=button_label or "Create Ticket", style=button_color, custom_id=f"{self.bot.user.id}SPticket"))
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
            embed = Embed(title="Ticket Created", description=f"**{emoji.arow}Thanks for contacting\n{emoji.arow}Feel free to communicate**", color=color.green)
            view = View().add_item(Button(label="Close Ticket", style=ButtonStyle.red, custom_id=f"{self.bot.user.id}SPTcancel"))
            await channel.send(f"<@{interaction.user.id}>", embed=embed, view=view)
            await interaction.response.send_message(f"**Ticket <#{channel.id}> Created Successfully**", ephemeral=True, delete_after=10)

        if interaction.data["custom_id"] == f"{self.bot.user.id}SPTcancel":
            closeConfirm = Button(label="Confirm", style=ButtonStyle.red)
            closeCancel = Button(label="Cancel", style=ButtonStyle.green)
            view = View()
            view.add_item(closeConfirm); view.add_item(closeCancel)
            await interaction.response.send_message(embed=Embed(description="Are You Sure?", color=color.red), view=view, delete_after=10)

            async def closeTicket(interaction:Interaction):
                await interaction.response.send_message(embed=Embed(description="Closing Ticket...", color=color.red), ephemeral=True)
                await interaction.channel.delete(reason="Ticket Closed")

            async def cancelClose(interaction:Interaction):
                await interaction.message.delete()

            closeConfirm.callback = closeTicket
            closeCancel.callback = cancelClose


    @commands.Cog.listener()
    async def on_guild_join(self, guild:Guild):
        try:
            msg= f"```py\nGuild Name : {guild.name}\nGuild Id : {guild.id}\nGuild Owner : {guild.owner}\nOwner_id : {guild.owner.id}\nMembers : {guild.member_count}```"
            await self.bot.guild_join_log.send(msg)

        except Exception as e:
            self.bot.logger.warning(f"Error while logging guild join: {e}")
        

    @commands.Cog.listener()
    async def on_guild_remove(self, guild:Guild):
        try:
            msg= f"```py\nGuild Name : {guild.name}\nGuild Id : {guild.id}\nGuild Owner : {guild.owner}\nOwner_id : {guild.owner.id}\nMembers : {guild.member_count}```"
            await self.bot.guild_leave_log.send(msg)

        except Exception as e:
            self.bot.logger.warning(f"Error while logging guild leave: {e}")
