import traceback
import pytz
import datetime
from modules import config
from discord import Embed, File
from ext.constants import TimeZone
from discord.ext import commands
from discord.ext.commands import errors

def update_error_log(error_message: str):
    timestamp = datetime.datetime.now(pytz.timezone(TimeZone.Asia_Kolkata.value))
    log_entry = f"{timestamp} : {error_message}"
    with open("error.log", "a") as log_file:
        log_file.write(log_entry + "\n")

async def handle_standard_errors(ctx:commands.Context, error, error_map:dict[Exception:str]):
    """Handles standard errors by sending predefined messages."""
    response = error_map.get(type(error))
    if response:
        return await ctx.send(embed=Embed(color=0xff0000, description=response))

async def handle_custom_error_strings(ctx:commands.Context, error, custom_errors:dict[str:str]):
    """Handles errors based on custom string conditions in the error message."""
    for condition, response in custom_errors.items():
        if condition in str(error):
            return await ctx.send(embed=Embed(color=0xff0000, description=response))

async def manage_context(ctx: commands.Context, error: errors.DiscordException, client: commands.Bot):
    """
    Manages all errors and sends them to the error log channel.
    """
    erl = client.get_channel(config.erl)
    cmdnf = client.get_channel(config.cmdnf)
    
    # Standard error mappings
    error_map = {
        commands.MissingRequiredArgument: "Missing Required Arguments! Check command usage with `{config.prefix}help {ctx.command.name}`.",
        commands.MissingPermissions: f"You don't have permissions to use this command.",
        commands.DisabledCommand: "This command is currently disabled. Try again later.",
        commands.MissingRole: str(error),
        commands.MissingAnyRole: str(error),
        commands.EmojiNotFound: "Emoji not found.",
        commands.NotOwner: "This is an owner-only command.",
        commands.MessageNotFound: "Message not found or deleted.",
        commands.MemberNotFound: "Member not found.",
        commands.ChannelNotFound: "Channel not found.",
        commands.GuildNotFound: "I'm not in the server you want to see.",
        commands.ChannelNotReadable: "Cannot read messages in the channel.",
        commands.CommandOnCooldown: str(error),
        commands.BotMissingPermissions: str(error),
        commands.UserInputError: "Please enter valid arguments.",
        commands.RoleNotFound: "Role not found.",
        commands.BadArgument: "Invalid argument.",

    }
    
    # Custom error strings
    custom_errors = {
        "Manage Messages": "Missing `Manage Messages` permission",
        "Unknown file format.": "Invalid input",
        "Send Messages": f"I don't have permission to send messages in this channel - {ctx.channel.mention}",
        "This playlist type is unviewable.": "This playlist type is unsupported!",
        "Maximum number of channels in category reached (50)": "Maximum number of channels in category reached (50)",
        "error code: 10003": "Channel deleted or invalid",
        "error code: 50013": "Missing permissions. Check my permissions.",
        "Unknown Role": "Given role is invalid or deleted",
        "Cannot delete a channel required for community servers": "Cannot delete a channel required for community servers",
        "error code: 50001": "I don't have access to do this.",
        "error code: 30005": "Maximum number of guild roles reached (250)",
        "error code: 30007": "Maximum number of webhooks reached (15)",
        "error code: 30008": "Maximum number of emojis reached",
        "error code: 30010": "Maximum number of reactions reached (20)",
        "error code: 30013": "Maximum number of guild channels reached (500)"
    }

    try:
        # Check if the error is in the standard error map
        if await handle_standard_errors(ctx, error, error_map):
            return
        
        # Check if the error message contains any custom error strings
        if await handle_custom_error_strings(ctx, error, custom_errors):
            return

        # Specific error handling for CommandNotFound
        if isinstance(error, commands.CommandNotFound):
            await cmdnf.send(f"```py\nGuild Name: {ctx.guild}\nGuild Id: {ctx.guild.id}\nUser Tag: {ctx.author}\nUser Id: {ctx.author.id}\nCommand: {ctx.message.content}```")
            return

        # Specific error handling for HTTPException
        if isinstance(error, config.discord.HTTPException):
            await erl.send(f"```json\n{error.text}\nStatus Code: {error.status}\n```")
            return

        # Fallback for uncategorized errors
        trace = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        text = (f"<@{config.owner_id}>\n{await ctx.guild.channels[0].create_invite(unique=False) or ''}\n\n\n"
                f"```py\nCommand: {ctx.command.name}\nGuild Name: {ctx.guild}\nGuild Id: {ctx.guild.id}\n"
                f"Channel Id: {ctx.channel.id}\nUser Tag: {ctx.author}\nUser Id: {ctx.author.id}\n\n\n"
                f"Error: {error}\nTraceback: {trace}\n```")

        if len(text) >= 1999:
            await erl.send(file=File(fp=text, filename="error.txt"))
        else:
            await erl.send(text)

        # Log the error
        update_error_log(trace)

    except Exception as e:
        # Log any exceptions that occur during error handling
        update_error_log(''.join(traceback.format_exception(type(e), e, e.__traceback__)))
        config.logger.warning("An error occurred while handling an error: %s", traceback.format_exception(e))
