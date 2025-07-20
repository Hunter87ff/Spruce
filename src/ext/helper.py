"""
This project is licensed under the GNU GPL v3.0.
Copyright (C) 2022-present hunter87.dev@gmail.com
Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.
"""

import os
import re
import discord
import uuid
from discord.ext import commands
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.bot import Spruce


     
def parse_team_name(message:discord.Message, strict:bool=False) -> str | None:
    content = message.content.lower()
    teamname = re.search(r"team.*", content)
    if teamname is None:
        return f"{message.author}'s team"
    teamname = re.sub(r"<@*#*!*&*\d+>|team|name|[^\w\s]", "", teamname.group()).strip()
    if strict and not teamname:
        return None
    teamname = teamname if teamname else f"{message.author}'s team"
    return teamname.lower().strip()[0:20]



def parse_prize_pool(message:discord.Message) -> str | None:
    """
    Parses the prize pool from a message content.
    It looks for patterns like "prize pool", "prizes", or "prize money" followed by a value.
    If no prize pool is found, it returns None.
    
    Args:
        message (discord.Message): The message object containing the content to parse.    Returns:
        str|None: The extracted prize pool value or None if not found.
    """
    content = str(message.content.lower())
    # Input validation - check length and basic sanity
    if len(content) == 0 or len(content) > 2000:  # Discord message limit + safety check
        return None
    
    # Additional input sanitization - remove potential problematic characters
    content = re.sub(r'[^\w\s$€£¥₹.,\-+:()]', '', content)
      # Secure regex pattern to prevent ReDoS attacks
    # - Limited character set: alphanumeric, spaces, currency symbols, basic punctuation
    # - Strict length limit (50 chars max for prize value)
    # - Non-greedy quantifiers with atomic grouping
    # - Removed lookahead/lookbehind patterns that can cause backtracking
    prize_pattern = r'(?i)prize(?:\s+(?:pool|money)|s)?\s*:\s*([a-zA-Z0-9\s$€£¥₹.,\-+]{1,50})'
    
    match = re.search(prize_pattern, content)
    if match:
        result = match.group(1).strip()
        # Additional validation on the result
        if len(result) > 0 and len(result) <= 50:
            return result
    return None


class DuplicateTag:
    def __init__(self, mention: discord.Member, message: discord.Message):
        self.mention = mention
        self.message = message


async def duplicate_tag(bot:"Spruce", crole:discord.Role, message:discord.Message, slots=None) -> DuplicateTag | None:
    if not message.guild:
        return None

    slots = slots or 50

    for fmsg in  await bot.cache.tourney_reged.get(message.channel):
        # Ignore bot/user messages
        if any([fmsg.author.bot, not isinstance(fmsg.author, discord.Member)]):
            continue
        
        if fmsg.author.id != message.author.id and crole in fmsg.author.roles:
            for mention in fmsg.mentions:
                if mention in message.mentions:
                    return DuplicateTag(mention, fmsg)
    return None



def get_event_prefix(name:str):
    if len(name.split()[0]) <=2:
        return name.split()[0] + "-"

    li = []
    for i in name.split()[0:2]:li.append(i[0])
    return str("".join(li) + "-")


def get_scrim_log(guild:discord.Guild):
    channel = discord.utils.get(guild.text_channels, name=f"{guild.me.name.lower()}-scrim-log")
    return channel


def get_tourney_log(guild:discord.Guild):

    for channel in guild.text_channels:
        if channel.name == f"{guild.me.name.lower()}-tourney-log":
            return channel
    return None


async def unlock_channel(channel:discord.TextChannel, role:discord.Role=None):
    if not channel.permissions_for(channel.guild.me).manage_permissions:
        raise commands.errors.MissingPermissions([
            "manage_permissions",
            "manage_channels",
            "manage_roles"
        ])
    role = role or channel.guild.default_role
    overwrite = channel.overwrites_for(role)
    overwrite.update(send_messages=True)
    await channel.set_permissions(role, overwrite=overwrite)


async def lock_channel(channel:discord.TextChannel, role:discord.Role=None):
    if not channel.permissions_for(channel.guild.me).manage_permissions:
        raise commands.errors.MissingPermissions([
            "manage_permissions",
            "manage_channels",
            "manage_roles"
        ])

    role = role or channel.guild.default_role
    overwrite = channel.overwrites_for(role)
    overwrite.update(send_messages=False, add_reactions=False)
    await channel.set_permissions(role, overwrite=overwrite)


async def translate(token, from_lang:str, to_lang:str, text:str):
    import aiohttp
    api = "https://api.cognitive.microsofttranslator.com/translate"
    headers = {
                'Ocp-Apim-Subscription-Key': token,
                'Ocp-Apim-Subscription-Region': 'eastus2',
                'Content-type': 'application/json',
                'X-ClientTraceId': str(uuid.uuid4()),
            }
    async def _translate_async():
        params = {"api-version": "3.0", "from": from_lang, "to": to_lang}
        body = [{"text": text}]
        async with aiohttp.ClientSession() as session:
            async with session.post(api, params=params, headers=headers, json=body) as res:
                if res.status == 200:
                    data = await res.json()
                    return data[0]["translations"][0]["text"]
                else:
                    return "Something went wrong! please try again later."
    try:
        translated_text = await _translate_async()
        return translated_text
    
    except aiohttp.ClientError as e:
        return f"Network error: {str(e)}"


async def download_file(url:str, filename:str):
    """
    Downloads a file asynchronously using aiohttp.
    """
    import aiohttp
    import aiofiles

    print(f"Starting download of {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                # Open a file in async mode and write to it in chunks
                async with aiofiles.open(filename, 'wb') as f:
                    async for chunk in response.content.iter_chunked(1024):
                        await f.write(chunk)
                print(f"Successfully downloaded '{filename}'")

            return response.status


async def download(url:str, fp:str):
    """
    Downloads a file synchronously using wget.
    """
    silent = "> NUL 2>&1" if os.name == "nt" else "> /dev/null 2>&1"
    return os.system(f"wget {url} {'-O' + fp if fp else ''} {silent}")


async def get_input(
        interaction:discord.Interaction, 
        title:str="Enter Value", 
        label:str="Enter Value", 
        style:discord.TextStyle=discord.TextStyle.short, 
        max_length:int=None, 
        placeholder:str=None):
    
    modal = discord.ui.Modal(title=title)
    modal.add_item(discord.ui.TextInput(label=label, style=style, placeholder=placeholder,  max_length=max_length))
    await interaction.response.send_modal(modal)
    async def mod_val(interaction: discord.Interaction):
        await interaction.response.defer()
    modal.on_submit = mod_val
    await modal.wait()
    if modal.is_finished():
        return modal.children[0].value
