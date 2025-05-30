"""
This project is licensed under the GNU GPL v3.0.
Copyright (C) 2022 hunter87.dev@gmail.com
Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.
"""

import discord
from ext import Database
from discord.ext import commands
from modules import config
db = Database()
devs:list[int] = db.cfdata.get("devs", [])



def is_dev(ctx:commands.Context | discord.Interaction) -> bool:
    """Check if the user is a developer"""
    if isinstance(ctx, discord.Interaction):
        return ctx.user.id in devs
    return ctx.author.id in devs

def is_admin(ctx: commands.Context | discord.Interaction) -> bool:
    if isinstance(ctx, discord.Interaction):
        return ctx.user.guild_permissions.administrator or ctx.guild.owner_id == ctx.user.id or is_dev(ctx)
    
    return ctx.author.guild_permissions.administrator or ctx.guild.owner_id == ctx.author.id or is_dev(ctx)


def _is_manager(ctx:commands.Context):
    """Check if the user is a manager"""
    return bool(ctx.author.guild_permissions.manage_guild or ctx.guild.owner_id == ctx.author.id or is_dev(ctx))


def has_guild_permissions(**perms: bool):
    """Check if the user has the permissions
    Currently under development and having few issues!!
    """
    invalid = set(perms) - set(discord.Permissions.VALID_FLAGS)
    if invalid:
        valid_flags = ', '.join(discord.Permissions.VALID_FLAGS)
        raise TypeError(f"Invalid permission(s): {', '.join(invalid)}. Valid permissions are: {valid_flags}")

    def predicate(ctx: commands.Context) -> bool:
        if not ctx.guild:
            return False
        
        if is_dev(ctx):
            return True
        return commands.has_guild_permissions(**perms).predicate(ctx)

    return commands.check(predicate)



def has_role(role:str): #type: ignore
    """Check if the user has a role"""
    async def predicate(ctx:commands.Context):
        if is_dev(ctx):
            return True
        return await commands.has_role(role).predicate(ctx)
    return commands.check(predicate)


def owner_only():
    async def predicate(ctx:commands.Context):
        if ctx.message.author.id == config.OWNER_ID :
            return True
        else :
            await ctx.send("Command is only for developers!!", ephemeral=True, delete_after=10)
            return False
    return commands.check(predicate)


def tourney_mod():
    """Check if the user is a tourney mod"""
    async def predicate(ctx:commands.Context):
        if not ctx.guild:
            await ctx.send("This command can only be used in a server",ephemeral=True, delete_after=10)
            return False
        
        if is_dev(ctx) or is_admin(ctx) or _is_manager(ctx):
            return True
        
        return await commands.has_role("tourney-mod").predicate(ctx)
    return commands.check(predicate)


def scrim_mod():
    async def predicate(ctx:discord.Interaction ):
        _is_eligible = any([
            is_dev(ctx),
            ctx.user.guild_permissions.manage_guild,
            ctx.user.guild_permissions.administrator,
            discord.utils.get(ctx.guild.roles, name="scrim-mod")
        ])

        if not _is_eligible:
            raise discord.app_commands.errors.MissingPermissions([
                "manage_guild",
                "administrator",
                "scrim-mod role"
            ])
        return True
    
    return discord.app_commands.check(predicate)
    



def dev_only():
    """Check if the user is a developer"""
    async def predicate(ctx:commands.Context):
        is_dev = ctx.message.author.id in db.cfdata.get("devs", [])
        if not is_dev :
            await ctx.send("Command is under development or only for developers!!", ephemeral=True, delete_after=10)
            return False
        return True
    return commands.check(predicate)


def under_maintenance(message:str = "The command is currently under maintenance. Please try again later.", interaction:bool = False):
    """Check if the bot is under maintenance"""
    async def predicate(ctx:commands.Context | discord.Interaction):

        if isinstance(ctx, discord.Interaction):
            if ctx.user.id in config.DEVELOPERS:
                return True
            
            raise discord.app_commands.errors.MissingPermissions(
                ["developer"]
            )
        
        
        if ctx.author.id in config.DEVELOPERS:
            return True
        
        await ctx.send(message, delete_after=10)
        return False
    if interaction:
        return discord.app_commands.check(predicate)
    return commands.check(predicate)