"""
A module for moderation commands in Spruce.
    :author: hunter87
    :copyright: (c) 2022-present hunter87.dev@gmail.com
    :license: GPL-3, see LICENSE for more details.
"""
from __future__ import annotations

import typing
import discord
from discord import app_commands
from discord.ext import commands
from core.abstract import Cog

if typing.TYPE_CHECKING:
    from core.bot import Spruce

class ModerationCog(Cog):
    """
    ## ModerationCog Class
    This class contains commands for moderating a Discord server.
    """

 
    def __init__(self, bot:"Spruce"):
        self.bot = bot
        self.emoji = self.bot.emoji.mod
        self.debug_mode = False
        self.Embed = self.bot.ext.EmbedBuilder

    def _declear(self,target:discord.TextChannel, role:discord.Role, action:str):
        return "{channel} is now {action} for {role}".format(
            channel=target, 
            action=action, 
            role=role
        )
    

    


    @commands.hybrid_group(name="lock", description="Lock a channel for a specific role", invoke_without_command=True)
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(role="The role to lock the channel for", channel="The channel to lock")
    @commands.has_permissions(manage_roles=True)
    @commands.cooldown(2, 15, commands.BucketType.user)
    @commands.bot_has_guild_permissions(manage_roles=True, send_messages=True)
    async def lock(self, ctx:commands.Context, role: discord.Role=None, channel:discord.TextChannel=None):
        await ctx.defer()
        if ctx.author.bot:
            return
        if ctx.invoked_subcommand:
            return
    
        role = role or  ctx.guild.default_role
        channel = channel or ctx.channel
        overwrite = channel.overwrites_for(role)
        overwrite.update(send_messages=False)
        await channel.set_permissions(role, overwrite=overwrite)

        if ctx.channel.permissions_for(ctx.guild.me).send_messages:
            await ctx.send(
                embed=self.Embed.success(
                    self._declear(channel, role, "locked")
                    ), 
                delete_after=5
            )


    @lock.command(name="channel", description="Lock a channel for a specific role")
    @commands.guild_only()
    @app_commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True, send_messages=True)
    @app_commands.describe(role="The role to lock the channel for", channel="The channel to lock")
    async def lock_channel(self, ctx:commands.Context, channel: discord.TextChannel=None, role:discord.Role=None):
        await self.lock(ctx, role=role, channel=channel or ctx.channel)



    @lock.command(name="category", description="Lock a category for a specific role", aliases=["lc"])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.guild_only()
    @app_commands.describe(role="The role to lock the category for", category="The category to lock")
    async def lock_category(self, ctx:commands.Context, category: discord.CategoryChannel, role:discord.Role=None):
        await ctx.defer()
        if ctx.author.bot:return
       
        ms:discord.Message = await ctx.send(f'**{self.bot.emoji.loading} Processing...**')
        role:discord.Role = role or  ctx.guild.default_role

        for channel in category.channels:
            overwrite = channel.overwrites_for(role)
            overwrite.update(send_messages=False, add_reactions=False)
            await channel.set_permissions(role, overwrite=overwrite)
            await self.bot.sleep(0.5)

        if ms:
            await ms.edit(content=f'{self.bot.emoji.tick} | {category.name} is locked for {role.name}')



    @commands.hybrid_group(name="unlock", description="Unlock a channel for a specific role", invoke_without_command=True)
    @app_commands.guild_only()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    @app_commands.describe( role="The role to unlock the channel for", channel="The channel to unlock")
    @commands.cooldown(2, 15, commands.BucketType.user)
    async def unlock(self, ctx:commands.Context, role: discord.Role=None, channel:discord.TextChannel=None):
        await ctx.defer()
        if ctx.author.bot:return
        if ctx.invoked_subcommand:
            return
        
        channel = channel or ctx.channel
        role = role or ctx.guild.default_role
        overwrite = channel.overwrites_for(role)
        overwrite.update(send_messages=True)
        await channel.set_permissions(role, overwrite=overwrite)
        await ctx.send(
            embed=self.Embed.success(f'{self.bot.emoji.tick} | {channel.mention} has been unlocked from `{role.name}`'),
            delete_after=5
        )



    @unlock.command(name="channel", description="Unlock a channel for a specific role")
    @commands.guild_only()
    @app_commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True, send_messages=True)
    @app_commands.describe(role="The role to unlock the channel for", channel="The channel to unlock")
    async def unlock_channel(self, ctx:commands.Context, channel: discord.TextChannel, role:discord.Role=None):
        await self.unlock(ctx, role=role, channel=channel)


    @unlock.command(name="category", description="Unlock a category for a specific role", aliases=["unlock_category"])
    @commands.guild_only()
    @app_commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True, send_messages=True)
    @app_commands.describe(role="The role to unlock the category for", category="The category to unlock")
    @commands.cooldown(2, 30, commands.BucketType.user)
    async def unlock_category(self, ctx:commands.Context,category: discord.CategoryChannel, role:discord.Role=None):
        await ctx.defer()
        if ctx.author.bot:return
        
        ms:discord.Message = await ctx.send(f'**{self.bot.emoji.loading} Processing...**')
        role:discord.Role = role or  ctx.guild.default_role

        for channel in category.channels:
            overwrite = channel.overwrites_for(role)
            overwrite.update(send_messages=True, add_reactions=True)
            await channel.set_permissions(role, overwrite=overwrite)
            await self.bot.sleep(0.5)

        if ms:
            await ms.edit(content=f'{self.bot.emoji.tick} | {category.name} is unlocked for {role.name}')



    @commands.hybrid_group(name="hide", description="Hide a channel from a specific role", invoke_without_command=True)
    @app_commands.guild_only()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.cooldown(2, 15, commands.BucketType.user)
    @app_commands.describe( role="The role to hide the channel from", channel="The channel to hide")
    async def hide(self, ctx:commands.Context, role: typing.Union[discord.Role, discord.Member]=None, channel:typing.Union[discord.TextChannel, discord.VoiceChannel]=None):
        await ctx.defer()
        if ctx.author.bot: return
        if ctx.invoked_subcommand:
            return
        role = role or ctx.guild.default_role
        channel = channel or ctx.channel
        overwrite = ctx.channel.overwrites_for(role)
        overwrite.update(view_channel=False)
        await channel.set_permissions(role, overwrite=overwrite)
        return await ctx.send(embed=discord.Embed(description=f'{self.bot.emoji.tick} | This channel is now hidden to {role.mention}'), delete_after=30)
    

    @hide.command(name="channel", description="Hide a channel from a specific role")
    @app_commands.guild_only()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.cooldown(2, 15, commands.BucketType.user)
    @app_commands.describe( role="The role to hide the channel from", channel="The channel to hide")
    async def hide_channel(self, ctx:commands.Context, role:discord.Role=None, channel:typing.Union[discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel]=None):
        await self.hide(ctx, role=role, channel=channel)



    @hide.command(name="category", description="Hide a category from a specific role", aliases=["hide_category", "hc"])
    @commands.guild_only()
    @app_commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.cooldown(2, 30, commands.BucketType.user)
    @commands.bot_has_guild_permissions(manage_roles=True, send_messages=True)
    @app_commands.describe(category="The category to hide", role="The role to hide from")
    async def hide_category(self, ctx:commands.Context,category: discord.CategoryChannel, role:discord.Role=None):
        await ctx.defer()
        if ctx.author.bot:return
        
        ms:discord.Message = await ctx.send(f'**{self.bot.emoji.loading} Processing...**')
        role:discord.Role = role or  ctx.guild.default_role

        for channel in category.channels:
            overwrite = channel.overwrites_for(role)
            overwrite.update(view_channel=False)
            await channel.set_permissions(role, overwrite=overwrite)
            await self.bot.sleep(0.5)

        if ms:
            await ms.edit(content=f'{self.bot.emoji.tick} | {category.name} is hidden from {role.name}')



    @commands.hybrid_group(name="unhide", description="Unhide a channel from a specific role", invoke_without_command=True)
    @app_commands.guild_only()
    @commands.guild_only()
    @commands.cooldown(1, 15, commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True, send_messages=True)
    @app_commands.describe(role="The role to unhide from", channel="The channel to hide")
    @app_commands.describe(role="The role to unhide the channel from", channel="The channel to unhide")
    async def unhide(self, ctx:commands.Context, role: typing.Union[discord.Role, discord.Member]=None, channel:typing.Union[discord.TextChannel, discord.VoiceChannel]=None):
        if ctx.author.bot: return
        if ctx.invoked_subcommand:return
        await ctx.defer()
        
        role = role or ctx.guild.default_role
        channel = channel or ctx.channel

        overwrite = ctx.channel.overwrites_for(role)
        overwrite.update(view_channel=True)
        await channel.set_permissions(role, overwrite=overwrite)
        
        if channel.permissions_for(ctx.guild.me).send_messages:
            await ctx.send(
                embed=discord.Embed(description=f'{self.bot.emoji.tick} | This channel is now visible to {role.mention}'), 
                delete_after=30
            )

    
    @unhide.command(name="channel", description="Unhide a channel from a specific role")
    @commands.has_permissions(manage_roles=True)
    @commands.guild_only()
    @app_commands.guild_only()
    @commands.bot_has_guild_permissions(manage_roles=True, send_messages=True)
    @app_commands.describe(role="The role to unhide the channel from", channel="The channel to unhide")
    async def unhide_channel(self, ctx:commands.Context, channel: discord.TextChannel, role:discord.Role=None):
        await self.unhide(ctx, role=role, channel=channel)



    @unhide.command(name="category", description="Unhide a category from a specific role", aliases=["unhide_category"])
    @commands.has_permissions(manage_roles=True)
    @commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.bot_has_guild_permissions(manage_roles=True, send_messages=True)
    async def unhide_category(self, ctx:commands.Context, category: discord.CategoryChannel, role :discord.Role = None):
        await ctx.defer()
        if ctx.author.bot:
            return
        _processing = await ctx.send(f'**{self.bot.emoji.loading} Processing...**')
        role:discord.Role = role or  ctx.guild.default_role

        for channel in category.channels:
            overwrite = channel.overwrites_for(role)
            overwrite.update(view_channel=True)
            await channel.set_permissions(role, overwrite=overwrite)
            await self.bot.sleep(0.5)
        
        if ctx.channel.permissions_for(ctx.guild.me).send_messages and _processing:
            await _processing.edit(content=f"**{self.bot.emoji.tick} | {category.name} is now visible to {role.name}**")



    @commands.hybrid_command(description="clear message within a limit and target filter", aliases=['purge'], )
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(2, 30, commands.BucketType.user)
    @app_commands.describe(amount="The number of messages to delete", target="The user to filter messages by")
    @commands.bot_has_guild_permissions(manage_messages=True)
    async def clear(self, ctx:commands.Context, amount:int=10, target:discord.User=None):
        _debug = False
        await ctx.defer()
        if ctx.author.bot:
            return

        if self.bot.is_ws_ratelimited():
            if ctx.me.guild_permissions.send_messages:
                return await ctx.send(
                    "**Rate limited!!.. please try again later**", 
                    delete_after=5
                )
        _limit= min(amount, max(amount, 50))

        def filter(m:discord.Message):
            if any([self.bot.is_ws_ratelimited()]):
                return False

            if not target:
                return True
            
            if m.author.id == target.id:
                return True
            
            else:
                return False
            
        try:
            await ctx.channel.purge(limit=_limit, check=filter, bulk=True)
            await self.bot.sleep(1)  # To avoid hitting rate limits
            await ctx.send(
                embed=self.Embed.success(
                    f"Cleared {amount} messages"
                ),
                delete_after=5
            )

        except Exception as e:
            self.bot.debug(f"Error while clearing messages: {e}", is_debug=_debug)


    @commands.hybrid_command(name="clear_perms", description="Clear all permissions from a role")
    @commands.guild_only()
    @app_commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.cooldown(1, 15, commands.BucketType.user)
    @app_commands.describe(role="The role to unhide the channel from")
    async def clear_perms(self, ctx:commands.Context, role: discord.Role=None):
        await ctx.defer()
        if ctx.author.bot:return

        ms:discord.Message = await ctx.send(f"**{self.bot.emoji.loading} Processing...**")
        if not role:
            for _role in ctx.guild.roles:
                if _role.position >= ctx.guild.me.top_role.position:
                    continue

                await _role.edit(permissions=discord.Permissions(permissions=0))
                await self.bot.sleep()
                continue

            emb = self.Embed.success(f'All permissions removed from all role below {ctx.guild.me.top_role.mention}')
            await ms.edit(content=None, embed=emb)
            return

        if role.position < ctx.guild.me.top_role.position:
            await role.edit(permissions=discord.Permissions(permissions=0))
            emb = self.Embed.success(f'All Permissions Removed from {role.mention}')
            await ms.edit(content=None, embed=emb)
            return


    @commands.hybrid_command(name="kick", description="Kick a member from the server")
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(kick_members=True, send_messages=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.guild_only()
    @app_commands.describe(member="The member to kick", reason="The reason for kicking the member")
    async def kick(self, ctx:commands.Context, member: discord.Member, reason=None):
        await ctx.defer()
        if ctx.author.bot:
            return
        
        if ctx.author.top_role.position < member.top_role.position:
            return await ctx.send("You don't have enough permission", delete_after=5)
        elif member == ctx.author:
            return await ctx.send("**You can't kick yourself**", delete_after=5)
        elif ctx.guild.me.top_role.position < member.top_role.position:
            return await ctx.send("**I can't kick this member**", delete_after=5)
        
        await ctx.guild.kick(member, reason=reason or f"{member} kicked by {ctx.author}")
        await ctx.send(f"**{self.bot.emoji.tick} | {member} has been kicked**", delete_after=5)


    @commands.hybrid_command(name="ban", description="Ban a member from the server")
    @commands.guild_only()
    @app_commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True, send_messages=True)
    @commands.cooldown(2, 30, commands.BucketType.user)
    @app_commands.describe(member="The member to ban", reason="The reason for banning the member")
    async def ban(self, ctx:commands.Context, member: discord.Member, reason=None):
        await ctx.defer()
        if ctx.author.bot: return
        
        if ctx.author.top_role.position < member.top_role.position:
            await ctx.send(embed=self.Embed.warning(f"{member}'s role is higher than yours"), delete_after=5)

        elif member == ctx.author:
            await ctx.send(embed=self.Embed.warning("**You can't ban your self**"), delete_after=5)

        elif ctx.guild.me.top_role.position < member.top_role.position:
            await ctx.send(embed=self.Embed.warning("**I can't ban him**"), delete_after=5)
            
        else:
            await ctx.guild.ban(member, reason=reason or f"{member} banned by {ctx.author}")
            await ctx.send(embed=self.Embed.success(f"{member} banned"), delete_after=5)


    @app_commands.command(name="unban", description="Unban a member from the server, Note: process might disrupt from discord's side!!")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.checks.bot_has_permissions(ban_members=True, send_messages=True)
    @app_commands.checks.cooldown(1, 60, key=lambda i: i.guild.id)
    @app_commands.describe(user="user id or username", unban_all="Whether to unban all (200 at a time) users", reason="The reason for unbanning the member")
    async def unban(self, ctx:discord.Interaction, user: discord.User=None, unban_all:bool=False, reason:str=None):
        await ctx.response.defer()

        if unban_all:
            processing = await ctx.channel.send(
                f"**{self.bot.emoji.loading} Processing...**"
            )

            unbanned_users = 0
            stage = 25 # per 25 member unbanned
            banned_users = ctx.guild.bans(limit=self.bot.config.MAX_UNBAN_LIMIT)
            async for _user in banned_users:
                try:
                    await ctx.guild.unban(_user.user, reason=reason or f"Unbanned by {ctx.user}")
                    unbanned_users += 1
                    if unbanned_users % stage == 0:
                        await processing.edit(content=f"**{self.bot.emoji.tick} Unbanned {unbanned_users} users so far...**")
                        await self.bot.sleep((unbanned_users//stage) * 2)  # To avoid hitting rate limits
                    
                    await self.bot.sleep(0.5)  # To avoid hitting rate limits


                except discord.NotFound:
                    continue

            await processing.delete()
            return await ctx.followup.send(f"**{self.bot.emoji.tick} Unbanned {unbanned_users} users successfully!**")

        if user:
            if not isinstance(user, discord.User):
                return await ctx.followup.send(
                    embed=discord.Embed(description=f"{self.bot.emoji.cross} Please provide a valid user to unban", color=self.bot.color.red)
                )

            await ctx.guild.unban(user, reason=reason or f"Unbanned by {ctx.user}")
            return await ctx.followup.send(f"**{user} has been unbanned**")
        
        return await ctx.followup.send("**Please provide a valid user to unban or use the `all` option**")


    @commands.command(aliases=['chd'])
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True, send_messages=True)
    async def channel_del(self, ctx:commands.Context,  *channels: discord.TextChannel):
        ms =await ctx.send("Processing...")
        for ch in channels:
            await ch.delete(reason=f"deleted by: {ctx.author}")
            await self.bot.sleep()
        await ms.edit(content=f'**{self.bot.emoji.tick} | Channels deleted Successfully**')
        

    @commands.hybrid_command(aliases=['dc'], description="Delete a category and all its channels")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def delete_category(self, ctx:commands.Context,  category: discord.CategoryChannel):
        await ctx.defer()
        if ctx.author.bot:return
        
        bt11 = discord.ui.Button(label="Confirm", style=discord.ButtonStyle.danger, custom_id="dcd_btn")
        bt12 = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.green, custom_id="dcc_btn")
        view = discord.ui.View()
        for i in [bt11, bt12]:
            view.add_item(i)
        del_t_con = await ctx.reply(f"**Are You Sure To Delete `{category.name}`?**", view=view)


        async def dc_confirmed(interaction:discord.Interaction):

            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message(
                    embed=self.Embed.warning(f"{self.bot.emoji.cross} | You are not allowed to do this"),
                    ephemeral=True
                )
                return
            
            if not ctx.guild.me.guild_permissions.manage_channels:
                await interaction.response.send_message(
                    embed=self.Embed.warning(f"I don't have permission to manage channels"),
                    ephemeral=True
                )
                return
            

            emb = discord.Embed(color=0x00ff00, description=f"**{self.bot.emoji.loading} | Deleting `{category.name}` Category**")
            await del_t_con.edit(content=None, embed=emb, view=None)
            for channel in category.channels:
                try:
                    await channel.delete(reason=f'Deleted by {ctx.author.name}')
                    await self.bot.sleep(1)

                    if len(category.channels) == 0:
                        await category.delete()
                        return await del_t_con.edit(
                            embed=self.Embed.success(message=f"**Successfully Deleted ~~{category.name}~~ Category**")
                        ) if del_t_con else None
                    
                except Exception as e:
                    self.bot.debug(f"Failed to delete channel {channel.name} in category {category.name}: {e}", is_debug=self.debug_mode)

                    await del_t_con.edit(
                        content=None,
                        embed=self.Embed.alert(f"**Failed to Delete `{channel.name}` Channel\nReason : maybe i don't have `permission`**"
                        ),
                        view=None
                    )

        async def del_msg(interaction:discord.Interaction):
            await interaction.message.delete()
            
            
        bt11.callback = dc_confirmed
        bt12.callback = del_msg


    
    @commands.hybrid_command(name="slowmode", description="Set slowmode for a channel")
    @commands.guild_only()
    @app_commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_guild_permissions(manage_channels=True, send_messages=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @app_commands.describe(seconds="The number of seconds to set slowmode for", channel="The channel to set slowmode for")
    async def slowmode(self, ctx:commands.Context, seconds:int=5, channel:discord.TextChannel=None):
        await ctx.defer()
        if ctx.author.bot:
            return
        
        channel = channel or ctx.channel
        if seconds < 0:
            return await ctx.send(embed=self.Embed.warning("**Slowmode can't be negative**"), delete_after=5)
        
        if seconds > 21600:
            return await ctx.send(embed=self.Embed.warning("**Slowmode can't be more than 6 hours**"), delete_after=5)

        await channel.edit(slowmode_delay=seconds)
        await ctx.send(embed=self.Embed.success(f"**{channel.mention} slowmode set to {seconds} seconds**"), delete_after=5)


    