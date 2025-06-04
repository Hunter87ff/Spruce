"""
This project is licensed under the GNU GPL v3.0.
Copyright (C) 2022 hunter87.dev@gmail.com
Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.
"""

import time
import cogs
import asyncio
import traceback
from requests import post
from discord.ext import commands
from ext.models import Tester
from modules import (config, message_handle)
from ext import Database, Logger, color, helper, emoji, constants, ClientTime, validator, error as error_handle
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
intents.reactions = True
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
    def __init__(self) -> None:
        self.config = config
        self.db = Database() 
        self.devs:list[int] = self.db.config_data.get("devs")
        self.logger:Logger = Logger
        self.helper = helper
        self.color = color
        self.emoji = emoji
        self.constants = constants
        self.log_channel:TextChannel
        self.time = ClientTime()
        self.validator = validator
        self.testers:list[Tester] = self.config.TESTERS
        super().__init__(
            shard_count=config.SHARDS, 
            command_prefix= commands.when_mentioned_or(config.PREFIX),
            intents=intents,
            allowed_mentions=AllowedMentions(everyone=False, roles=True, replied_user=True, users=True),
            activity=Activity(type=ActivityType.listening, name=f"{self.config.PREFIX}help")
        )
        self.tree.on_error = self.tree_error_handler
        



    async def tree_error_handler(self, interaction, error):
        await error_handle.handle_interaction_error(interaction, error, self)



    async def setup_hook(self) -> None:
        # Remove default help command 
        self.remove_command("help")

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
            # load the cogs
            
            await self.tree.sync()
            self.log_channel:TextChannel = self.get_channel(config.client_error_log)
            starter_message = f'{self.user} | {len(self.commands)} Commands | Version : {config.VERSION} | Boot Time : {round(time.time() - self._started_at, 2)}s'
            self.logger.info(starter_message)
            if not self.config.IS_DEV_ENV:
                post(
                    url=self.db.config_data.get("stwbh"),
                    json={"embeds": [Embed(title="Status", description=starter_message, color=self.color.random()).to_dict()],}
                )
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
            await message_handle.tourney(message)


         
    async def on_command_error(self, ctx:commands.Context, error:Exception):
        await error_handle.manage_context(ctx, error, self)


    async def on_error(self, event, *args, **kwargs):
        error = traceback.format_exc()
        await error_handle.manage_backend_error(error, self)




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


    async def sleep(self, seconds:int) -> None:
        """
        Sleeps for the given number of seconds.
        Args:
            seconds (int): The number of seconds to sleep.
        """
        await asyncio.sleep(seconds)
    

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
        self._started_at = _started_at
        await super().start(self.db.token, reconnect=True)
