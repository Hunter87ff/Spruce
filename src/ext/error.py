"""
This project is licensed under the GNU GPL v3.0.
Copyright (C) 2022 hunter87.dev@gmail.com
Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.
"""

import traceback
from ext import Logger
from ext import types
import pytz, datetime
from modules import config
import discord
from discord.errors import HTTPException
from discord import Embed, File, Interaction, app_commands, errors
from ext.constants import TimeZone
from discord.ext import commands
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.bot import Spruce


def update_error_log(error_message: str):
    """Append error with timestamp to local error.log file."""
    timestamp = datetime.datetime.now(pytz.timezone(TimeZone.Asia_Kolkata.value))
    text = f"{timestamp} : {error_message}"
    with open("error.log", "a") as log_file:
        Logger.error(error_message)
        log_file.write(text + "\n")


async def manage_backend_error(error: Exception, bot: "Spruce"):
    """Handle low-level Discord API errors by sending logs to a log channel."""
    message = f"```json\n{error}\n```"
    if isinstance(error, errors.HTTPException):
        message = f"```json\n{error.text}\nStatus Code : {error.status}\n```"
    if bot.log_channel:
        await bot.log_channel.send(message)


async def manage_context(ctx: commands.Context, error: commands.errors.DiscordException, bot: "Spruce", _msg: str = None, *args, **kwargs):
    """Main error handler for command errors."""
    cmdnf = bot.get_channel(config.cmd_not_found_log)

    try:
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(embed=Embed(color=0xff0000, description=f"Missing required arguments!\nTip: use `{config.PREFIX}help {ctx.command.name}`"))

        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(embed=Embed(color=0xff0000, description="This command is currently disabled."))

        elif isinstance(error, commands.CommandNotFound):
            if cmdnf:
                await cmdnf.send(
                    f"```py\nGuild Name: {ctx.guild}\nGuild Id : {ctx.guild.id}\nUser Tag : {ctx.author}\nUser Id : {ctx.author.id}\nCommand : {ctx.message.content}```"
                )
            else:
                bot.logger.warning(
                    f"[WARN] 'cmd_not_found_log' channel not set. Cannot log unknown command: {ctx.message.content}"
                )
                update_error_log(f"Unknown command attempted: {ctx.message.content} by {ctx.author} in {ctx.guild}")

        elif isinstance(error, (commands.MissingRole, commands.MissingAnyRole)):
            return await ctx.send(embed=Embed(color=0xff0000, description=str(error)))

        elif isinstance(error, types.errors.ContextMigrationException):
            return await ctx.send(embed=Embed(color=0xff0000, description="This command has moved to slash. Try using `/command`."))

        elif isinstance(error, commands.BotMissingPermissions):
            return await ctx.send(embed=Embed(color=0xff0000, description=str(error).replace("Bot", bot.user.name)))

        elif isinstance(error, commands.EmojiNotFound):
            return await ctx.send(embed=Embed(color=0xff0000, description="Emoji not found."))

        elif isinstance(error, commands.NotOwner):
            return await ctx.send(embed=Embed(color=0xff0000, description="Only the bot owner can use this command."))

        elif isinstance(error, commands.MessageNotFound):
            return await ctx.send(embed=Embed(color=0xff0000, description="Message not found or already deleted."))

        elif isinstance(error, commands.MemberNotFound):
            return await ctx.send(embed=Embed(color=0xff0000, description="Member not found."))

        elif isinstance(error, commands.ChannelNotFound):
            return await ctx.send(embed=Embed(color=0xff0000, description="Channel not found."))

        elif isinstance(error, commands.GuildNotFound):
            return await ctx.send("I'm not in the server you're referring to.", delete_after=19)

        elif isinstance(error, commands.ChannelNotReadable):
            return await ctx.send(embed=Embed(color=0xff0000, description="I can't read messages in that channel."))

        elif isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(embed=Embed(color=0xff0000, description=str(error)))

        elif "Unknown file format." in str(error):
            return await ctx.send(embed=Embed(description="Invalid file format.", color=0xff0000))

        elif "This playlist type is unviewable." in str(error):
            return await ctx.send(embed=Embed(description="Unsupported playlist type.", color=0xff0000))

        elif "Maximum number of channels in category reached" in str(error):
            return await ctx.send(embed=Embed(description="Channel limit reached in this category.", color=0xff0000))

        elif "error code: 10003" in str(error):
            return await ctx.send(embed=Embed(description="Channel deleted or invalid.", color=0xff0000))

        elif "error code: 50013" in str(error):
            return await ctx.send(embed=Embed(description="Missing permissions. Please check my role.", color=0xff0000), delete_after=30)

        elif "Unknown Role" in str(error):
            return await ctx.send(embed=Embed(description="Role is invalid or deleted.", color=0xff0000), delete_after=30)

        elif "Cannot delete a channel required for community servers" in str(error):
            return await ctx.send(embed=Embed(description="Cannot delete a required community channel.", color=0xff0000), delete_after=30)

        elif "error code: 50001" in str(error):
            return await ctx.send(embed=Embed(description="I don't have access to perform this action.", color=0xff0000), delete_after=30)

        elif "error code: 30005" in str(error):
            return await ctx.send(embed=Embed(description="Guild role limit reached (250).", color=0xff0000))

        elif "error code: 30007" in str(error):
            return await ctx.send(embed=Embed(description="Webhook limit reached (15).", color=0xff0000))

        elif "error code: 30008" in str(error):
            return await ctx.send(embed=Embed(description="Emoji limit reached.", color=0xff0000))

        elif "error code: 30010" in str(error):
            return await ctx.send(embed=Embed(description="Reaction limit reached (20).", color=0xff0000))

        elif "error code: 30013" in str(error):
            return await ctx.send(embed=Embed(description="Guild channel limit reached (500).", color=0xff0000))

        elif isinstance(error, commands.UserInputError):
            return await ctx.send(embed=Embed(color=0xff0000, description="Invalid arguments."))

        elif isinstance(error, HTTPException):
            await bot.log_channel.send(f"```\n{error.text}\nStatus Code : {error.status}\n```")

        elif isinstance(error, commands.MissingPermissions):
            return await ctx.send(embed=Embed(color=0xff0000, description=str(error).replace("and", "").replace("comm.", "command.")))

        else:
            bot.logger.error(f"Unhandled error in `{ctx.command}` by `{ctx.author}` ({ctx.author.id}) in `{ctx.guild}` ({ctx.guild.id})")
            content = ''.join(traceback.format_exception(type(error), error, error.__traceback__))

            with open("error.txt", "w", encoding="utf-8") as file:
                file.write(content)

            await bot.log_channel.send(content=f"<@{bot.config.OWNER_ID}>", file=File("error.txt"))
            update_error_log(content)

    except Exception as e:
        bot.logger.warning(traceback.format_exception(e), "ext.error")
        update_error_log('\n'.join(traceback.format_exception(type(e), e, e.__traceback__)))



async def handle_interaction_error(interaction: Interaction, error: app_commands.AppCommandError, bot: "Spruce"):
    """Handles slash command interaction errors."""
    if isinstance(error, app_commands.MissingPermissions):
        return await interaction.response.send_message(embed=Embed(color=0xff0000, description=str(error)), ephemeral=True)

    elif isinstance(error, app_commands.CommandOnCooldown):
        return await interaction.response.send_message(embed=Embed(color=0xff0000, description=str(error)), ephemeral=True)

    elif isinstance(error, (app_commands.MissingRole, app_commands.MissingAnyRole, app_commands.CheckFailure)):
        return await interaction.response.send_message(embed=Embed(color=0xff0000, description=str(error)), ephemeral=True)

    elif isinstance(error, app_commands.CommandNotFound):
        return await interaction.response.send_message(embed=Embed(color=0xff0000, description="Command not found."), ephemeral=True)

    elif isinstance(error, app_commands.NoPrivateMessage):
        return await interaction.response.send_message(embed=Embed(color=0xff0000, description="This command cannot be used in private messages."), ephemeral=True)

    elif isinstance(error, app_commands.BotMissingPermissions):
        return await interaction.response.send_message(embed=Embed(color=0xff0000, description=str(error).replace("Bot", bot.user.name)), ephemeral=True)

    else:
        await interaction.response.send_message(embed=Embed(color=0xff0000, description="Something went wrong. Please try again later."), ephemeral=True)
        with open("error.txt", "w", encoding="utf-8") as file:
            file.write("\n".join(traceback.format_exception(type(error), error, error.__traceback__)))
        if bot.log_channel.permissions_for(bot.log_channel.guild.me).attach_files:
            await bot.log_channel.send(content=f"<@{bot.config.OWNER_ID}>", file=File("error.txt"))
