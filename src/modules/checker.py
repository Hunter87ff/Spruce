import typing
import asyncio
import discord
from discord.ext import commands
from discord.ext.commands.converter import (MemberConverter, RoleConverter, TextChannelConverter)






async def channel_input(ctx, check=None, timeout=20, delete_after=False, check_perms=True):
    check = check or (lambda m: m.channel == ctx.channel and m.author == ctx.author)
    try:
        message: discord.Message = await ctx.bot.wait_for("message", check=check, timeout=timeout)
    except asyncio.TimeoutError:
        return await ctx.send("Time Out! Try Again")

    else:
        channel = await TextChannelConverter().convert(ctx, message.content)
        return channel






async def ttl_slots(ctx, check=None, timeout=30):
    check = check or (lambda m: m.channel == ctx.channel and m.author == ctx.author)
    try:
        msg = await ctx.bot.wait_for("message", check=check, timeout=timeout)

    except asyncio.TimeoutError:
        return await ctx.send("Time Out! Try Again")


    else:
        return msg.content
    

