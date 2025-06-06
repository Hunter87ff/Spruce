"""
This project is licensed under the GNU GPL v3.0.
Copyright (C) 2022 hunter87.dev@gmail.com
Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.
"""


import re
import discord
import requests, uuid
from ext import Database
from discord.ext import commands



def get_db():
    """
    Returns a Database Object
    """
    return Database()


     
def parse_team_name(message:discord.Message, strict:bool=False) -> str:
    """
    Parses the team name from a message content.
    If the message contains a mention of a team, it extracts the name and formats it.
    If no team name is found, it defaults to the author's name followed by "'s team".
    Args:
        message (discord.Message): The message object containing the content to parse.
        strict (bool): If True, it will only return the team name if it is explicitly mentioned.
    Returns:
        str: The formatted team name.
    """
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

async def duplicate_tag(crole:discord.Role, message:discord.Message, slots=None, **kwargs) -> DuplicateTag | None:
    """
    Checks if a message mentions a user with the same role as the author.
    If a user with the same role is mentioned in previous messages, it returns that user.
    Args:
        crole (discord.Role): The role to check against.
        message (discord.Message): The message object to check for mentions.
    Returns:
        discord.Member | None: The first mentioned user with the same role, or None if no such user is found.
    """
    if slots is None:
        slots = 50

    messages = [message async for message in message.channel.history(limit=slots)]
    for fmsg in messages:

        # Ignore bot messages
        if fmsg.author.bot:
            continue
        
        if fmsg.author.id != message.author.id and crole in fmsg.author.roles:
            for mention in fmsg.mentions:
                if mention in message.mentions:
                    return DuplicateTag(mention, fmsg)
    return None



def get_event_prefix(name:str):
    """
    Returns the event prefix for a given name.
    If the first word is less than or equal to 2 characters, it returns the first word followed by a hyphen.
    Otherwise, it returns the first two letters of the first word followed by a hyphen.

    Args:
        name (str): The name to extract the prefix from.

    Returns:
        str: The event prefix. eg: "T3-", "WS-", "MC-", etc.
    """

    if len(name.split()[0]) <=2:
        return name.split()[0] + "-"

    li = []
    for i in name.split()[0:2]:li.append(i[0])
    return str("".join(li) + "-")


def get_scrim_log(guild:discord.Guild):
    channel = discord.utils.get(guild.text_channels, name=f"{guild.me.name.lower()}-scrim-log")
    return channel


def get_tourney_log(guild:discord.Guild):
    # channel = discord.utils.get(guild.text_channels, name=f"{guild.me.name}-tourney-log")
    for channel in guild.text_channels:
        if channel.name == f"{guild.me.name.lower()}-tourney-log":
            return channel
    return None


async def unlock_channel(channel:discord.TextChannel, role:discord.Role=None):
    """
    Unlocks a channel to allow a specific role to send messages.
    This method updates the permissions overwrites for a channel to allow a role to send messages.

    Args:
        channel (discord.TextChannel): The channel to be unlocked.
        role (discord.Role, optional): The role to grant send message permissions to.
            Defaults to the guild's default role if not provided.

    Returns:
        None: This method doesn't return anything.

    Raises:
        discord.Forbidden: If the bot doesn't have permissions to modify channel permissions.
        discord.HTTPException: If modifying the permissions fails.
    """
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
    """
    Locks a channel to prevent a specific role from sending messages.
    This method updates the permissions overwrites for a channel to deny a role from sending messages.

    Args:
        channel (discord.TextChannel): The channel to be locked.
        role (discord.Role, optional): The role to deny send message permissions to.
            Defaults to the guild's default role if not provided.

    Returns:
        None: This method doesn't return anything.

    Raises:
        commands.errors.MissingPermissions: If the bot lacks the required permissions to manage channel permissions.
        Exception: If any other error occurs while locking the channel.
    """

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


def translate(token, from_lang:str, to_lang:str, text:str):
    """
    Translates text from one language to another using Microsoft Translator API.
    Args:
        token (str): The subscription key for the Microsoft Translator API.

        from_lang (str): The source language code (e.g., 'en' for English).
        to_lang (str): The target language code (e.g., 'es' for Spanish).
        text (str): The text to be translated.

    Returns:
        str: The translated text if successful, otherwise an error message.
    """
    api = "https://api.cognitive.microsofttranslator.com/translate"
    headers = {
                'Ocp-Apim-Subscription-Key': token,
                'Ocp-Apim-Subscription-Region': 'eastus2',
                'Content-type': 'application/json',
                'X-ClientTraceId': str(uuid.uuid4()),
            }
    res = requests.post(api, params={"api-version":"3.0", "from":from_lang, "to":to_lang}, headers=headers, json=[{"text":text}])
    if res.status_code==200: return res.json()[0]["translations"][0]["text"]
    else: return "Something went wrong! please try again later."