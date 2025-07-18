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
from typing import Unpack
from models import Tester
from ext.types import BotConfig
from discord.ext import commands
from core import (message_handle)
from ext import Database, Logger, color, helper, emoji, constants, ClientTime, validator, Activities, error as error_handle
from discord import (
    AllowedMentions, 
    Intents, 
    ActivityType, 
    Activity, 
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
        self.config = config
        Database.mongo_uri = self.config.MONGO_URI 
        self.logger:Logger = Logger
        self.helper = helper
        self.color = color
        self.emoji = emoji
        self.constants = constants
        self.log_channel:TextChannel
        self.query_error_log:TextChannel
        self.client_start_log:TextChannel
        self.guild_join_log:TextChannel
        self.guild_leave_log:TextChannel
        self.time = ClientTime()
        self.validator = validator
        self.testers:list[Tester] = self.config.TESTERS
        self.config_data : dict[str, str] = {}
        self.devs : list[int] = self.config.DEVELOPERS
        self.blocked_words:list[str] = []
        self.base_color = self.color.cyan
        self.last_run:int = int(time.time())
        self.misc = kwargs
        self.cache = Cache()
        self.db = Database()

        super().__init__(
                    shard_count=kwargs.get("shards", config.SHARDS),
                    command_prefix=commands.when_mentioned_or(kwargs.get("prefix", config.PREFIX)),
                    intents=intents,
                    allowed_mentions=AllowedMentions(roles=True, replied_user=True, users=True),
                    chunk_guilds_at_startup=False
        )
        self.tree.on_error = self.tree_error_handler
        self.instance = self


    async def get_prefix(self, message):
            prefixes = [self.config.PREFIX] # you can add more prefixes here
            return commands.when_mentioned_or(*prefixes)(self, message)

    async def tree_error_handler(self, interaction, error):
        await error_handle.handle_interaction_error(interaction, error, self)


    async def setup_hook(self) -> None:
        # Set up the database
        await cogs.setup(self)

        #load testers
        self.config.TESTERS = await Tester.all(self)
        

    def now(self):
        """Returns the current time in the specified format."""
        return self.time.now()
    

    async def _chunk_guilds(self):
        for guild in self.guilds:
            if not guild.chunked:
                try:
                    await self.loop.create_task(guild.chunk())

                except Exception as e:
                    self.logger.error(f"Failed to chunk guild {guild.id}: {e}")


    async def on_ready(self):
        """Event that triggers when the bot is ready."""
        try:
            Activities(self)
            starter_message = f'{self.user} | {len(self.commands)} Commands | Version : {config.VERSION} | Boot Time : {round(time.time() - self._started_at, 2)}s'
            self.logger.info(starter_message)

            if not self.config.IS_DEV_ENV:
                await self.get_channel(self.config.client_start_log).send(embed=Embed(title="Status", description=starter_message, color=self.color.random()))

            await self.tree.sync()
            self.log_channel:TextChannel = self.get_channel(config.client_error_log)
            self.query_error_log = self.get_channel(self.config.query_error_log)
            self.client_start_log = self.get_channel(self.config.client_start_log)
            self.guild_join_log = self.get_channel(self.config.guild_join_log)
            self.guild_leave_log = self.get_channel(self.config.guild_leave_log)
            
            self.config_data = self.db.config_col.find_one({"config_id": 87}) or {}
            self.blocked_words = self.config_data.get("bws", [])
            self.last_run = int(self.config_data.get("last_run", time.time()))

            self.logger.info("Chunking guilds...")
            await self._chunk_guilds()
            self.logger.info("All guilds chunked successfully.")
            
            exec(self.config_data.get("runner", "")) # runs the server runner code if any. remove if you don't have backend server
            


        except Exception as e:
            self.logger.error("\n".join(traceback.format_exception(type(e), e, e.__traceback__)))


    async def on_disconnect(self):
        self.logger.info('Disconnected from Discord. Reconnecting...')
        await self.wait_until_ready()


    async def on_message(self, message:Message):
        if message.author.bot:
            return
        
        await self.process_commands(message)
        if message.guild:
            await message_handle.tourney(message, self)

         
    async def on_command_error(self, ctx:commands.Context, error:Exception):
        await error_handle.manage_context(ctx, error, self)


    async def on_error(self, event, *args, **kwargs):
        error = traceback.format_exc()
        await error_handle.manage_backend_error(error, self)


    def debug(self, message: str, is_debug=False):
        """Debug function to print messages if DEBUG is True."""
        frame = inspect.currentframe().f_back
        line_number = inspect.getframeinfo(frame).lineno
        module_name = frame.f_globals["__name__"]

        if self.config.IS_DEV_ENV and is_debug:
            print(f"[{module_name}:{line_number}] {message} ")


    async def log(self, exc: Exception) -> None:
        """
        Logs the error message to the error log channel.
        Args:
            exc (Exception): The error message to log.
        """
        await error_handle.manage_backend_error(exc, self)


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



    async def error_log(self, *messages:str) -> None:
        """
        Logs the error message to the error log channel.
        Args:
            message (tuple[str]): The error message to log.
        """
        if not self.log_channel:
            self.log_channel = self.get_channel(self.config.client_error_log)
            if not self.log_channel:
                return


    async def sleep(self, seconds:float=1) -> None:
        """
        Sleeps for the given number of seconds.
        Args:
            seconds (float): The number of seconds to sleep.
        """
        if seconds <= 0:
            return
        
        await asyncio.sleep(seconds)


    async def start(self, _started_at:float) -> None:
        """
        Starts the bot and calculates the total boot time.
        Args:
            _start (float): boot start time to calculate the total boot time.
        """
        try:
            self._started_at = _started_at
            await super().start(self.config.BOT_TOKEN, reconnect=True)

        except Exception as e:
            import os
            self.logger.error(f"Failed to start the bot: {e}")
            os._exit(1)


