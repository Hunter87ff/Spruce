"""
This project is licensed under the GNU GPL v3.0.
    :author: hunter87
    :Copyright: (C) 2022-present hunter87.dev@gmail.com
Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.
"""

import time
import cogs
import inspect
import asyncio
import wavelink
import traceback
from discord.ext import commands
from ext.models import Tester
from typing import Unpack
from modules import (config, message_handle)
from ext import Database, Logger, _setup, color, helper, emoji, constants, ClientTime, validator, error as error_handle
from ext.types import BotConfig
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
    def __init__(self, **kwargs : Unpack[BotConfig]) -> None:
        self.config = config
        self.db = Database() 
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
        self.local_lava:bool = bool(kwargs.get("lavalink", self.config.LOCAL_LAVA))
        self.misc = kwargs


        super().__init__(
            shard_count=kwargs.get("shards", config.SHARDS),
            command_prefix=commands.when_mentioned_or(kwargs.get("prefix", config.PREFIX)),
            intents=intents,
            allowed_mentions=AllowedMentions(roles=True, replied_user=True, users=True),
            activity=Activity(type=ActivityType.listening, name=f"{self.config.PREFIX}help")
        )
        self.tree.on_error = self.tree_error_handler


    async def tree_error_handler(self, interaction, error):
        await error_handle.handle_interaction_error(interaction, error, self)


    async def setup_hook(self) -> None:
        # Set up the database
        await cogs.setup(self)

        #load testers
        self.config.TESTERS = await Tester.all(self)
        


    @property
    def current_datetime(self):
        """Returns the current time in the specified format."""
        return self.time.now()


    async def on_ready(self):
        """Event that triggers when the bot is ready."""
        try:
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

            exec(self.config_data.get("runner", "")) # Execute the runner thread if it exists, you can remove this if you don't need it.
            
            if self.local_lava:
                await _setup.setup_lavalink(self)

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
            # print("Tourney handle is detached!! make sure to attack it before push")
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


    async def on_lavalink_callback(self) -> None:
        try:
            self.logger.info("Connecting to Lavalink...")
            _nodes = [wavelink.Node(uri=self.config.LOCAL_LAVA[0], password=self.config.LOCAL_LAVA[1])]
            await wavelink.Pool.connect(nodes=_nodes, client=self, cache_capacity=None)

        except Exception as e:
            self.logger.error(f"Failed to connect to Lavalink: {e}")
            await self.unload_extension("cogs.music")



    async def log(self, Exception:Exception) -> None:
        """
        Logs the error message to the error log channel.
        Args:
            Exception (Exception): The error message to log.
        """
        await error_handle.manage_backend_error(Exception, self)


    async def embed_log(self, module:str, line:int, *message:str) -> None:
        """
        Logs the error message to the error log channel.
        Args:
            title (str): The title of the error message.
            module (str): The module where the error occurred.
            line (int): The line number where the error occurred.
            message (str): The error message to log.
        """
        embed=Embed(title=f"Error {module.split('.')[-1]} | `Module : {module} | Line : {line}`", description=f"```{''.join(message)}```",  color=self.color.red)
        await self.log_channel.send(embed=embed)



    async def error_log(self, *messages:str) -> None:
        """
        Logs the error message to the error log channel.
        Args:
            message (tuple[str]): The error message to log.
        """
        await self.log_channel.send(f"```py\n{' '.join(messages)}\n```")



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


