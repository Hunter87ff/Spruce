"""
This project is licensed under the GNU GPL v3.0.
Copyright (C) 2022 hunter87.dev@gmail.com
Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.
"""


import re
import discord
from ext import Database
from discord.ext import commands



def get_db():
    """
    Returns a Database Object
    """
    return Database()


async def is_dev(ctx: commands.Context | discord.Interaction):
    """
    Checks if the user is a developer
    """
    user_id = ctx.user.id if isinstance(ctx, discord.Interaction) else ctx.author.id
    if user_id not in get_db().config_data["devs"]:
        response = ctx.response.send_message if isinstance(ctx, discord.Interaction) else ctx.send
        await response("Command is under development", ephemeral=True if isinstance(ctx, discord.Interaction) else False)
        return False
    return True
     
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
        message (discord.Message): The message object containing the content to parse.
    
    Returns:
        str|None: The extracted prize pool value or None if not found.
    """
    content = str(message.content.lower())
    if len(content) == 0:
        return None
    prize_pattern = r'(?i)prize(?:\s+(?:pool|money)|s?)?\s*:\s*(.+?)(?:\s*$)'
    match = re.search(prize_pattern, content)
    return match.group(1).strip() if match else None



async def duplicate_tag(crole:discord.Role, message:discord.Message):
    """
    Checks if a message mentions a user with the same role as the author.
    If a user with the same role is mentioned in previous messages, it returns that user.
    Args:
        crole (discord.Role): The role to check against.
        message (discord.Message): The message object to check for mentions.
    Returns:
        discord.Member | None: The first mentioned user with the same role, or None if no such user is found.
    """

    class DuplicateTag:
        def __init__(self, mention: discord.Member, message: discord.Message):
            self.mention = mention
            self.message = message

    messages = [message async for message in message.channel.history(limit=100)]
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
