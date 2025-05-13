"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2022 hunter87.dev@gmail.com
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.
"""


import discord
import discord.ext
import discord.ext.commands
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
        if ctx.message.author.id == config.owner_id :
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
        
        if is_dev(ctx):
            return True
        
        return await commands.has_role("tourney-mod").predicate(ctx)
    return commands.check(predicate)


def dev_only():
    """Check if the user is a developer"""
    async def predicate(ctx:commands.Context):
        is_dev = ctx.message.author.id in db.cfdata.get("devs", [])
        if not is_dev :
            await ctx.send("Command is under development or only for developers!!", ephemeral=True, delete_after=10)
            return False
        return True
    return commands.check(predicate)