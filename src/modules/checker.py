import typing
import asyncio
import discord
from discord.ext import commands
from discord.ext.commands.converter import (MemberConverter, RoleConverter, TextChannelConverter)

async def channel_input(ctx, check=None, timeout=20, delete_after=False, check_perms=True):
    check = check or (lambda m: m.channel == ctx.channel and m.author == ctx.author)
    try:message: discord.Message = await ctx.bot.wait_for("message", check=check, timeout=timeout)
    except asyncio.TimeoutError:return await ctx.send("Time Out! Try Again")
    else:
        try:await message.delete()
        except:pass
        channel = await TextChannelConverter().convert(ctx, message.content)
        return channel

async def check_role(ctx, check=None, timeout=20, delete_after=False, check_perms=True):
    check = check or (lambda m: m.channel == ctx.channel and m.author == ctx.author)
    try:message: discord.Message = await ctx.bot.wait_for("message", check=check, timeout=timeout)
    except asyncio.TimeoutError:return await ctx.send("Time Out! Try Again")
    else:
        try:await message.delete()
        except:pass
        role = await RoleConverter().convert(ctx, message.content)
        return role


async def ttl_slots(ctx:commands.Context, check=None, timeout=20) -> int:
    check = check or (lambda m: m.channel == ctx.channel and m.author == ctx.author)
    try:msg = await ctx.bot.wait_for("message", check=check, timeout=timeout)
    except asyncio.TimeoutError:
        await ctx.send("Time Out! Try Again")
        return None
    else:
        try:await msg.delete()
        except:pass
        return int(msg.content)
    

