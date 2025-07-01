"""
This project is licensed under the GNU GPL v3.0.
Copyright (C) 2022 hunter87.dev@gmail.com
Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.
"""
 
 
 
import asyncio
import discord
from discord.ext import commands
from ext.constants import Alerts
from discord.ext.commands.converter import (RoleConverter, TextChannelConverter)

async def channel_input(ctx:commands.Context, check=None):
    check = check or (lambda m: m.channel == ctx.channel and m.author == ctx.author)
    try:
        async with asyncio.timeout(20):
            message: discord.Message = await ctx.bot.wait_for("message", check=check)

    except asyncio.TimeoutError:
        return await ctx.send(Alerts.TIMEOUT)
    
    else:
        await message.delete() if message.guild.me.guild_permissions.manage_messages else None

        channel = await TextChannelConverter().convert(ctx, message.content)
        return channel

async def check_role(ctx:commands.Context, check=None):
    check = check or (lambda m: m.channel == ctx.channel and m.author == ctx.author)
    try:
        async with asyncio.timeout(20):
            message: discord.Message = await ctx.bot.wait_for("message", check=check)
    except asyncio.TimeoutError:
        return await ctx.send("Time Out! Try Again")
    else:
        await message.delete() if message.guild.me.guild_permissions.manage_messages else None
        role = await RoleConverter().convert(ctx, message.content)
        return role


async def ttl_slots(ctx:commands.Context, check=None) -> int|None:
    check = check or (lambda m: m.channel == ctx.channel and m.author == ctx.author)
    try:
        async with asyncio.timeout(20):
            msg:discord.Message = await ctx.bot.wait_for("message", check=check)
    except asyncio.TimeoutError:
        await ctx.send("Time Out! Try Again")
        return None
    else:
        await msg.delete() if msg.guild.me.guild_permissions.manage_messages else None
        return int(msg.content)
    
async def get_input(interaction:discord.Interaction, title:str="Enter Value", label:str="Enter Value", style:discord.TextStyle=discord.TextStyle.short, max_length:int=None, placeholder:str=None):
    modal = discord.ui.Modal(title=title)
    modal.add_item(discord.ui.TextInput(label=label, style=style, placeholder=placeholder,  max_length=max_length))
    await interaction.response.send_modal(modal)
    async def mod_val(interaction:discord.Interaction):await interaction.response.defer()
    modal.on_submit = mod_val
    await modal.wait()
    if modal.is_finished():return modal.children[0].value

async def get_role(interaction:discord.Interaction):
    selection = discord.ui.RoleSelect(min_values=1, max_values=1, placeholder="Select Role")
    selection.callback = lambda i: i.response.defer()
    await interaction.response.send_message("Select Role", view=selection)
    return selection.values[0]
