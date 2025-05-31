"""
This project is licensed under the GNU GPL v3.0.
Copyright (C) 2022 hunter87.dev@gmail.com
Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.
"""

import discord
from .db import Database
from discord.ext import commands
from modules import config
db = Database()



def _is_dev (ctx:commands.Context | discord.Interaction) -> bool:
    """Check if the user is a developer"""
    if isinstance(ctx, discord.Interaction):
        return ctx.user.id in config.DEVELOPERS
    return ctx.author.id in config.DEVELOPERS


def _is_admin(ctx: commands.Context | discord.Interaction) -> bool:
    if isinstance(ctx, discord.Interaction):
        return ctx.user.guild_permissions.administrator or ctx.guild.owner_id == ctx.user.id or _is_dev(ctx)
    
    return ctx.author.guild_permissions.administrator or ctx.guild.owner_id == ctx.author.id or _is_dev(ctx)


def _is_manager(ctx:commands.Context | discord.Interaction):
    """Check if the user is a manager"""
    if isinstance(ctx, discord.Interaction):
        return ctx.user.guild_permissions.manage_guild or ctx.guild.owner_id == ctx.user.id or _is_dev(ctx)

    return ctx.author.guild_permissions.manage_guild or ctx.guild.owner_id == ctx.author.id or _is_dev(ctx)


def _check_bot_manage_perms(ctx:commands.Context | discord.Interaction):
    if ctx.guild is None:
        raise discord.app_commands.NoPrivateMessage("This command can only be used in a server")

    if not all([
            ctx.guild.me.guild_permissions.manage_roles,
            ctx.guild.me.guild_permissions.manage_channels,
            ctx.guild.me.guild_permissions.manage_messages
        ]):
        if isinstance(ctx, discord.Interaction):
            raise discord.app_commands.errors.BotMissingPermissions(["`manage_roles`", "`manage_channels`", "`manage_messages`"])
        raise commands.BotMissingPermissions(["`manage_roles`", "`manage_channels`", "`manage_messages`"])
    return True
        

def _has_role (ctx:commands.Context | discord.Interaction, role:str|int) -> bool:
    """Check if the user has a role"""
    if _is_dev(ctx):
        return True
    
    if isinstance(ctx, discord.Interaction):
        if isinstance(role, int):
            return ctx.user.get_role(role) is not None
        
        return discord.utils.get(ctx.user.roles, name=role) is not None
    
    if isinstance(role, int):
        return ctx.author.get_role(role) is not None
    
    return discord.utils.get(ctx.author.roles, name=role) is not None


def tourney_mod(interaction:bool = False):
    """Check if the user is a tourney mod"""
    async def predicate(ctx:commands.Context | discord.Interaction):
        _check_bot_manage_perms(ctx)

        if _is_dev(ctx) or _is_admin(ctx) or _is_manager(ctx) or _has_role(ctx, "tourney-mod"):
            return True
        
        missing_perms = [
            "`tourney-mod` role or",
            "`manage_guild`",
        ]
        if isinstance(ctx, discord.Interaction):
            raise discord.app_commands.errors.MissingPermissions(missing_perms)
        raise commands.MissingPermissions(missing_perms)
    
        
    
    return discord.app_commands.check(predicate) if interaction else commands.check(predicate)


def scrim_mod(interaction:bool = True):
    async def predicate(ctx:commands.Context | discord.Interaction ):
        _check_bot_manage_perms(ctx)


        _is_eligible = any([
            _is_dev(ctx), _is_admin(ctx), _is_manager(ctx), _has_role(ctx, "scrim-mod")
        ])
        
        if not _is_eligible:
            missing_perms = [ "`scrim-mod` role or", "`manage_guild`" ]
            if isinstance(ctx, discord.Interaction):
                raise discord.app_commands.errors.MissingPermissions(missing_perms)
            raise commands.MissingPermissions(missing_perms)

        return True

    if interaction:
        return discord.app_commands.check(predicate)
    
    return commands.check(predicate)


def dev_only(interaction:bool = False):
    """Check if the user is a developer"""
    async def predicate(ctx:commands.Context | discord.Interaction):
        if _is_dev(ctx):
            return True
        if isinstance(ctx, discord.Interaction):
            raise discord.app_commands.errors.MissingPermissions(["developer"])
        raise commands.MissingPermissions(["developer"])

    return discord.app_commands.check(predicate) if interaction else commands.check(predicate)


def under_maintenance(interaction:bool = False):
    """Check if the bot is under maintenance"""
    return dev_only(interaction=interaction)  # Reusing dev_only for maintenance check, as it serves a similar purpose.
        