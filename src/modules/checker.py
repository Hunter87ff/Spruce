import asyncio
import discord
from discord.ext import commands
from discord.ext.commands.converter import (RoleConverter, TextChannelConverter)

async def channel_input(ctx:commands.Context, check=None, timeout=20):
    check = check or (lambda m: m.channel == ctx.channel and m.author == ctx.author)
    try:message: discord.Message = await ctx.bot.wait_for("message", check=check, timeout=timeout)
    except asyncio.TimeoutError:return await ctx.send("Time Out! Try Again")
    else:
        try:await message.delete()
        except:pass
        channel = await TextChannelConverter().convert(ctx, message.content)
        return channel

async def check_role(ctx:commands.Context, check=None, timeout=20):
    check = check or (lambda m: m.channel == ctx.channel and m.author == ctx.author)
    try:message: discord.Message = await ctx.bot.wait_for("message", check=check, timeout=timeout)
    except asyncio.TimeoutError:return await ctx.send("Time Out! Try Again")
    else:
        try:await message.delete()
        except:pass
        role = await RoleConverter().convert(ctx, message.content)
        return role


async def ttl_slots(ctx:commands.Context, check=None, timeout=20) -> int|None:
    check = check or (lambda m: m.channel == ctx.channel and m.author == ctx.author)
    try:msg:discord.Message = await ctx.bot.wait_for("message", check=check, timeout=timeout)
    except asyncio.TimeoutError:
        await ctx.send("Time Out! Try Again")
        return None
    else:
        try:await msg.delete()
        except:pass
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
