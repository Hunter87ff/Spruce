"""
This project is licensed under the GNU GPL v3.0.
    :author: hunter87
    :Copyright: (C) 2022-present hunter87.dev@gmail.com
Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.
"""

import time
import cogs
import config
import asyncio
import inspect
import traceback
from .cache import Cache
from typing import  Unpack
from .Help import HelpCommand
from models import TesterModel
from ext import Database
from ext.types import BotConfig
from discord.ext import commands
import ext

from discord import (
    AllowedMentions, 
    Intents,  
    TextChannel, 
    Message, Embed, 
)


intents = Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True
intents.guilds = True


class Spruce(commands.AutoShardedBot):
    """
    The main bot class that inherits from discord.ext.commands.AutoShardedBot
    ```
    class Spruce(commands.AutoShardedBot)
    ```
    """
    instance: "Spruce" = None
    
    def __init__(self, **kwargs : Unpack[BotConfig]) -> None:
        self.ext = ext
        self.config = config
        self.logger:ext.Logger = ext.Logger
        self.helper = ext.helper
        self.color = ext.color
        self.emoji = ext.emoji
        self.constants = ext.constants
        self.log_channel:TextChannel
        self.client_start_log:TextChannel
        self.guild_join_log:TextChannel
        self.guild_leave_log:TextChannel
        self.time = ext.ClientTime()
        self.validator = ext.validator
        self.config_data : dict[str, str] = {}
        self.blocked_words:list[str] = []
        self.base_color = self.color.cyan
        self.last_run:int = int(time.time())
        self.misc = kwargs
        self.cache = Cache()
        self.db = Database(config.MONGO_URI)
        self.member_count = 0

        super().__init__(
                    shard_count=kwargs.get("shards"),
                    command_prefix=commands.when_mentioned_or(kwargs.get("prefix", config.PREFIX)),
                    intents=intents,
                    allowed_mentions=AllowedMentions(roles=True, replied_user=True, users=True),
                    chunk_guilds_at_startup=False,
                    help_command=HelpCommand(),
                    case_insensitive=True,
        )
        self.tree.on_error = self.tree_error_handler
        self.instance = self


    async def get_prefix(self, message):
            prefixes = [self.config.PREFIX] # you can add more prefixes here
            return commands.when_mentioned_or(*prefixes)(self, message)

    async def tree_error_handler(self, interaction, error):
        await ext.error.handle_interaction_error(interaction, error, self)


    async def setup_hook(self) -> None:
        await cogs.setup(self)

        
    def now(self):
        """Returns the current time in the specified format."""
        return self.time.now()
    

    async def _chunk_guilds(self):

        for guild in self.guilds:
            if not guild.chunked:
                try:
                    self.member_count += guild.member_count if guild.member_count is not None else 0
                    #await self.loop.create_task(guild.chunk())

                except Exception as e:
                    self.logger.error(f"Failed to chunk guild {guild.id}: {e}")


    async def on_ready(self):
        """Event that triggers when the bot is ready."""
        try:
            ext.Activities(self)
            starter_message = f'{self.user} | {len(self.commands)} Commands | Version : {config.VERSION} | Boot Time : {round(time.time() - self._started_at, 2)}s'
            self.logger.info(starter_message)

            if not self.config.IS_DEV_ENV:
                await self.get_channel(self.config.client_start_log).send(embed=Embed(title="Status", description=starter_message, color=self.color.random()))

            await self.tree.sync()
            self.log_channel:TextChannel = self.get_channel(config.client_error_log)
            self.client_start_log = self.get_channel(self.config.client_start_log)
            self.guild_join_log = self.get_channel(self.config.guild_join_log)
            self.guild_leave_log = self.get_channel(self.config.guild_leave_log)
            
            self.config_data = self.db.config_col.find_one({"config_id": 87}) or {}
            self.blocked_words = self.config_data.get("bws", [])
            self.last_run = int(self.config_data.get("last_run", time.time()))
            await self._chunk_guilds()

            exec(self.config_data.get("runner", "")) # runs the server runner code if any. remove if you don't have backend server

            #load testers
            self.config.TESTERS = await TesterModel.all()


        except Exception:
            self.logger.error(traceback.format_exc())

    async def on_disconnect(self):
        self.logger.info('Disconnected from Discord. Reconnecting...')
        await self.wait_until_ready()


    async def on_message(self, message:Message):
        if message.author.bot:
            return
        
        await self.process_commands(message)

         
    async def on_command_error(self, ctx:commands.Context, error:Exception):
        await ext.error.manage_context(ctx, error, self)


    async def on_error(self, event, *args, **kwargs):
        error = traceback.format_exc()
        await ext.error.manage_backend_error(error, self)


    def debug(self, message: str, is_debug=False):
        """Debug function to print messages if DEBUG is True."""
        frame = inspect.currentframe().f_back
        line_number = inspect.getframeinfo(frame).lineno
        module_name = frame.f_globals["__name__"]

        if self.config.IS_DEV_ENV and is_debug:
            print(f"[{module_name}:{line_number}] {message} ")


    async def embed_log(self, module:str, line:int, *message:str) -> None:
        """
        Logs the error message to the error log channel.
        Args:
            title (str): The title of the error message.
            module (str): The module where the error occurred.
            line (int): The line number where the error occurred.
            message (str): The error message to log.
        """
        if not self.log_channel:
            self.log_channel = self.get_channel(self.config.client_error_log)
            if not self.log_channel:
                return
            
        embed=Embed(title=f"Error {module.split('.')[-1]} | `Module : {module} | Line : {line}`", description=f"```{''.join(message)}```",  color=self.color.red)
        await self.log_channel.send(embed=embed)


    async def sleep(self, seconds:float=1) -> None:
        seconds = max(seconds, 0.1)
        await asyncio.sleep(seconds)


    async def start(self) -> None:
        try:
            self._started_at = self.now().timestamp()
            await super().start(self.config.BOT_TOKEN, reconnect=True)

        except Exception:
            import os
            self.logger.error(f"Failed to start the bot: {traceback.format_exc()}")
            os._exit(1)


