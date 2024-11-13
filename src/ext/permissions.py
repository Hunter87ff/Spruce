"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

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


def is_dev(ctx:commands.Context):
    """Check if the user is a developer"""
    return ctx.author.id in devs

def is_admin(ctx: commands.Context) -> bool:
    return bool(
        ctx.author.guild_permissions.administrator or 
        ctx.guild.owner_id == ctx.author.id or 
        is_dev(ctx)
    )


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
        if ctx.author.guild_permissions.administrator:
            return True
        permissions: discord.Permissions = ctx.author.guild_permissions
        missing = [perm for perm, value in perms.items() if getattr(permissions, perm) != value]
        return len(missing) == 0

    return commands.check(predicate)



def has_role(role:str):
    """Check if the user has a role"""
    async def predicate(ctx:commands.Context):
        if not ctx.guild:return False
        if is_dev(ctx):return True
        _role = discord.utils.get(ctx.guild.roles, name=role)
        if not _role:return False
        return _role in ctx.author.roles
    return commands.check(predicate)


def has_any_role(*roles:str):
    """Check if the user has any of the roles"""
    async def predicate(ctx:commands.Context):
        if not ctx.guild:return False
        if is_dev(ctx):return True
        return any(has_role(ctx, role) for role in roles)
    return commands.check(predicate)


def owner_only():
    def predicate(ctx:commands.Context):
        return (ctx.message.author.id == config.owner_id)
    return commands.check(predicate)


def dev_only():
    """Check if the user is a developer"""
    async def predicate(ctx:commands.Context):
        await ctx.send("Command is under development", ephemeral=True)
        return ctx.message.author.id in db.cfdata["devs"]
    return commands.check(predicate)