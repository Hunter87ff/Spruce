"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2022 hunter87.dev@gmail.com
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.
"""
import traceback
from ext import Logger
import pytz, datetime
from discord import errors as derrors
from modules import config
from discord.errors import HTTPException
from discord import Embed, File
from ext.constants import TimeZone
from ext import types
from discord.ext import commands
from discord.ext.commands import errors
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.bot import Spruce


def update_error_log(error_message: str):
    """
    Appends an error message with a timestamp to the error log file.
    
    The function adds the current date and time in the Asia/Kolkata timezone
    to the error message and writes it to the 'error.log' file.
    
    Args:
        error_message (str): The error message to be logged.
        
    Returns:
        None
        
    Example:
        >>> update_error_log("Database connection failed")
    """
    text = f"{datetime.datetime.now(pytz.timezone(TimeZone.Asia_Kolkata.value))} : {error_message}"
    with open("error.log", "a") as log_file:
        Logger.error(error_message)
        log_file.write(text + "\n")


async def manage_backend_error(error: Exception, bot: "Spruce"):
    """
    Manages backend errors by sending error details to a designated error log channel.
    
    This function handles different types of discord.py errors by formatting them
    appropriately and sending them to the error log channel defined in the config.
    
    Args:
        error (Exception): The exception that was raised
        bot (commands.Bot): The bot instance to get the error log channel
        
    Supported error types:
        - discord.errors.HTTPException: Sends status code and error text
        - discord.errors.ConnectionClosed: Sends the error message
        - discord.errors.GatewayNotFound: Sends the error message
        - discord.errors.RateLimited: Sends the error message
    
    Returns:
        None
    """

    if isinstance(error, derrors.HTTPException):
        await bot.log_channel.send(f"```json\n{error.text}\nStatus Code : {error.status}\n```")
    elif isinstance(error, derrors.ConnectionClosed):
        await bot.log_channel.send(f"```json\n{error}\n```")
    elif isinstance(error, derrors.GatewayNotFound):
        await bot.log_channel.send(f"```json\n{error}\n```")
    elif isinstance(error, derrors.RateLimited):
        await bot.log_channel.send(f"```json\n{error}\n```")



async def manage_context(ctx:commands.Context, error:errors.DiscordException, bot:"Spruce", _msg: str = None, *args, **kwargs):
    """
    manages all the errors and sends them to the error log channel
    """
    cmdnf = bot.get_channel(config.cmd_not_found_log)

    try:
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(embed=Embed(color=0xff0000, description=f"Missing Required Arguments! You Should Check How To Use This Command.\nTip: use `{config.PREFIX}help {ctx.command.name}` to get Instructions"))
        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(embed=Embed(color=0xff0000, description="This Command Is Currently Disabled! You Can Try Again Later"))
        elif isinstance(error, commands.CommandNotFound):
            await cmdnf.send(f"```py\nGuild Name: {ctx.guild}\nGuild Id : {ctx.guild.id}\nUser Tag : {ctx.author}\nUser Id : {ctx.author.id}\nCommand : {ctx.message.content}```")
        elif isinstance(error, (commands.MissingRole, commands.MissingAnyRole)):
            return await ctx.send(embed=Embed(color=0xff0000, description=str(error)))

        elif isinstance(error, types.errors.ContextMigrationException):
            return await ctx.send(embed=Embed(color=0xff0000, description="This command has been migrated to a slash command. Please use the new command format."))
        
        elif isinstance(error, commands.EmojiNotFound):
            return await ctx.send(embed=Embed(color=0xff0000, description="Emoji Not Found"))
        elif isinstance(error, commands.NotOwner):
            return await ctx.send(embed=Embed(color=0xff0000, description="This Is A Owner Only Command You Can't Use It"))
        elif isinstance(error, commands.MessageNotFound):
            return await ctx.send(embed=Embed(color=0xff0000, description="Message Not Found Or Deleted"))
        elif isinstance(error, commands.MemberNotFound):
            return await ctx.send(embed=Embed(color=0xff0000, description="Member Not Found"))
        elif isinstance(error, commands.ChannelNotFound):
            return await ctx.send(embed=Embed(color=0xff0000, description="Channel Not Found"))
        elif isinstance(error, commands.GuildNotFound):
            return await ctx.send("**I'm Not In The Server! which You Want To See**", delete_after=19)
        elif isinstance(error, commands.ChannelNotReadable):
            return await ctx.send(embed=Embed(color=0xff0000, description="Can Not Read Messages Of The Channel"))
        elif isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(embed=Embed(color=0xff0000, description=str(error)))
        elif "Manage Messages" in str(error):
            return await ctx.send(embed=Embed(description="Missing `Manage Messages` Permission", color=0xff0000))
        elif "Unknown file format." in str(error):
            return await ctx.send(embed=Embed(description="Invalid Input", color=0xff0000))
        elif "Send Messages" in str(error):
            return await ctx.author.send(embed=Embed(description=f"I don't have Permissions To Send message in this channel - {ctx.channel.mention}", color=0xff0000))
        elif "This playlist type is unviewable." in str(error):
            return await ctx.send(embed=Embed(description="This playlist type is unsupported!", color=0xff0000))
        elif "Maximum number of channels in category reached (50)" in str(error):
            return await ctx.send(embed=Embed(description="Maximum number of channels in category reached (50)", color=0xff0000), delete_after=30)
        elif isinstance(error, commands.BotMissingPermissions):
            return await ctx.send(embed=Embed(color=0xff0000, description=str(error)))
        elif "error code: 10003" in str(error):
            return await ctx.send(embed=Embed(description="Channel Deleted Or Invalid", color=0xff0000))
        elif "error code: 50013" in str(error):
            return await ctx.send(embed=Embed(description="**Missing Permissions! You Should Check My Permissions**", color=0xff0000), delete_after=30)
        elif "Unknown Role" in str(error):
            return await ctx.send(embed=Embed(description="**Given Role Is Invalid Or Deleted**", color=0xff0000), delete_after=30)
        elif "Cannot delete a channel required for community servers" in str(error):
            return await ctx.send(embed=Embed(description="**I Cannot delete a channel required for community servers**", color=0xff0000), delete_after=30)
        elif "error code: 50001" in str(error):
            return await ctx.send(embed=Embed(description="**I don't have access to do this**", color=0xff0000), delete_after=30)
        elif "error code: 30005" in str(error):
            return await ctx.send(embed=Embed(description="Maximum number of guild roles reached (250)", color=0xff0000))
        elif "error code: 30007" in str(error):
            return await ctx.send(embed=Embed(description="Maximum number of webhooks reached (15)", color=0xff0000))
        elif "error code: 30008" in str(error):
            return await ctx.send(embed=Embed(description="Maximum number of emojis reached", color=0xff0000))
        elif "error code: 30010" in str(error):
            return await ctx.send(embed=Embed(description="Maximum number of reactions reached (20)", color=0xff0000))
        elif "error code: 30013" in str(error):
            return await ctx.send(embed=Embed(description="Maximum number of guild channels reached (500)", color=0xff0000))
        elif isinstance(error, commands.UserInputError):
            return await ctx.send(embed=Embed(color=0xff0000, description="Please Enter Valid Arguments"))
        elif isinstance(error, HTTPException):
            await bot.log_channel.send(f"```json\n{error.text}\nStatus Code : {error.status}\n```")
        elif isinstance(error, commands.MissingPermissions):
            return await ctx.send(embed=Embed(color=0xff0000, description="You don't have Permissions To Use This Command"))
        else: 
            text = f"```py\nCommand : {ctx.command.name}\nGuild Name: {ctx.guild}\nGuild Id : {ctx.guild.id}\nChannel Id : {ctx.channel.id}\nUser Tag : {ctx.author}\nUser Id : {ctx.author.id}\n\n\nError : {error}\nTraceback: {''.join(traceback.format_exception(type(error), error, error.__traceback__))}\n```"
            content=f"<@885193210455011369>\nMessage : {_msg or ''}\n{await ctx.guild.channels[0].create_invite(unique=False) or ''}"
            with open("error.txt", "w") as file:
                file.write(text)
            await bot.log_channel.send(
                content=content,
                file=File("error.txt")
            )
            update_error_log(''.join(traceback.format_exception(type(error), error, error.__traceback__)))

    except Exception as e:
        bot.logger.warning(traceback.format_exception(e), "ext.error")
        update_error_log(''.join(traceback.format_exception(type(e), e, e.__traceback__)))
        