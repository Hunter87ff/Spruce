"""
This project is licensed under the GNU GPL v3.0.
Copyright (C) 2022 hunter87.dev@gmail.com
Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.
"""


import discord
from discord import app_commands
from asyncio import sleep
from discord.ext import commands
import typing

if typing.TYPE_CHECKING:
    from modules.bot import Spruce

class ModerationCog(commands.Cog):
    """
    ## ModerationCog Class
    This class contains commands for moderating a Discord server.
    """
    def __init__(self, bot:"Spruce"):
        self.bot = bot


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
            await ctx.send(f'**{self.bot.emoji.tick} Channel has been locked for `{role.name}`**', delete_after=5)
    

    @lock.command(name="channel", description="Lock a channel for a specific role")
    @commands.guild_only()
    @app_commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True, send_messages=True)
    @app_commands.describe(role="The role to lock the channel for", channel="The channel to lock")
    async def lock_channel(self, ctx:commands.Context, channel: discord.TextChannel, role:discord.Role=None):
        await self.lock(ctx, role=role, channel=channel)


    @lock.command(name="category", description="Lock a category for a specific role", aliases=["lc"])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.guild_only()
    @app_commands.describe(role="The role to lock the category for", category="The category to lock")
    async def lock_category(self, ctx:commands.Context, category: discord.CategoryChannel, role:discord.Role=None):
        await ctx.defer()
        if ctx.author.bot:return
       
        ms = await ctx.send(f'**{self.bot.emoji.loading} Processing...**')
        role:discord.Role = role or  ctx.guild.default_role
        overwrite = category.overwrites_for(role)
        overwrite.update(send_messages=False, add_reactions=False)

        try:
            await ms.edit(content=f'**{self.bot.emoji.tick} | Successfully Locked {category.name} From `{role.name}`**')

        except Exception:return


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
        await ctx.send(f'{self.bot.emoji.tick} | {channel.mention} has been unlocked from `{role.name}`', delete_after=5)



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
        overwrite = category.overwrites_for(role)
        overwrite.update(send_messages=False, add_reactions=False)
        if ms:
            await ms.edit(content=f'**{self.bot.emoji.tick} | Successfully Unlocked {category.name}**')



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



    @hide.command(name="category", description="Hide a category from a specific role", aliases=["hide_category"])
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
            await sleep(0.5)

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
            await sleep(0.5)
        
        if ctx.channel.permissions_for(ctx.guild.me).send_messages and _processing:
            await _processing.edit(content=f"**{self.bot.emoji.tick} | {category.name} is now visible to {role.name}**")



    @commands.hybrid_command(description="clear message within a limit and target filter", aliases=['purge'], )
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(2, 30, commands.BucketType.user)
    @app_commands.describe(amount="The number of messages to delete", target="The user to filter messages by")
    @commands.bot_has_guild_permissions(manage_messages=True)
    async def clear(self, ctx:commands.Context, amount:int=10, target:discord.Member=None):
        await ctx.defer()
        if ctx.author.bot:
            return

        if self.bot.is_ws_ratelimited():
            if ctx.me.guild_permissions.send_messages:
                return await ctx.send(
                    "**Rate limited!!.. please try again later**", 
                    delete_after=5
                )
            
        def filter(m:discord.Message):
            if not target:
                return True
            
            elif m.author.id == target.id:
                return True
            
            else:
                return False
        
        await ctx.channel.purge(
            limit= max(amount, 50),
            check=filter,
        )
        await ctx.send(
            f"**{self.bot.emoji.tick} | Cleared {amount} messages**",
            delete_after=5
        )    
        

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
        bt = ctx.guild.get_member(self.bot.user.id)
       
        ms:discord.Message = await ctx.send(f"**{self.bot.emoji.loading} Processing...**")
        if role:
            if role.position < bt.top_role.position:
                await role.edit(permissions=discord.Permissions(permissions=0))
                emb = discord.Embed(description=f'{self.bot.emoji.tick} | All Permissions Removed from {role.mention}')
                return await ms.edit(content=None, embed=emb)
            
        elif not role:
            for role in ctx.guild.roles:
                if role.position < bt.top_role.position:
                    await role.edit(permissions=discord.Permissions(permissions=0))
                    await sleep(1)
            emb = discord.Embed(descriptio=f'{self.bot.emoji.tick} | All permissions removed from all role below {bt.top_role.mention}')
            return await ms.edit(content=None, embed=emb)



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
    @commands.bot_has_guild_permissions(ban_members=True, send_messages=True)
    @commands.has_permissions(ban_members=True)
    @commands.cooldown(2, 15, commands.BucketType.user)
    @commands.guild_only()
    @app_commands.describe(member="The member to ban", reason="The reason for banning the member")
    async def ban(self, ctx:commands.Context, member: discord.Member, reason=None):
        await ctx.defer()
        if ctx.author.bot: return
        
        if ctx.author.top_role.position < member.top_role.position:
            await ctx.send(f"{member}'s role is higher than yours", delete_after=5)
        elif member == ctx.author:
            await ctx.send("**You can't ban your self**", delete_after=5)
        elif ctx.guild.me.top_role.position < member.top_role.position:
            await ctx.send("**I can't ban him**", delete_after=5)
        else:
            await ctx.guild.ban(member, reason=reason or f"{member} banned by {ctx.author}")
            await ctx.send(f"{member} banned", delete_after=5)