"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2022 hunter87.dev@gmail.com
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.
"""

import time
import traceback
import cogs
from requests import post
from discord.ext import commands
from modules.chat import ChatClient
from ext import Database, Logger, color, helper, emoji, error as error_handle
from modules import (config, message_handle)
from discord import AllowedMentions, Intents, ActivityType, Activity, TextChannel, Message, Embed


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
        self.devs:list[int] = self.db.cfdata.get("devs")
        self.logger:Logger = Logger
        #self.chat_client = ChatClient(self)
        self.helper = helper
        self.color = color
        self.emoji = emoji
        self.ACTIVE_MODULES = config.activeModules
        

        super().__init__(
            shard_count=config.SHARDS, 
            command_prefix= commands.when_mentioned_or(config.PREFIX),
            intents=intents,
            allowed_mentions=AllowedMentions(everyone=False, roles=False, replied_user=True, users=True),
            activity=Activity(type=ActivityType.listening, name="&help")
        )

        self.log_channel:TextChannel = self.get_channel(config.erl)

    async def setup_hook(self) -> None:
        # Remove default help command 
        self.remove_command("help")

        # load the cogs
        await cogs.setup(self)

    async def on_ready(self):
        """Event that triggers when the bot is ready."""
        try:
            await self.tree.sync()
            starter_message = f'{self.user} | {len(self.commands)} Commands | Version : {config.version} | Boot Time : {round(time.time() - self._started_at, 2)}s'
            self.logger.info(starter_message)
            await config.vote_add(self)
            post(
                url=self.db.cfdata.get("stwbh"), 
                json={
                    "content": f"<@{config.owner_id}>",
                    "embeds": [
                        {
                            "title": "Status",
                            "description": starter_message,
                            "color": self.color.green
                        }
                    ]
                }
            )
        except Exception as ex:
            print(ex)
        

    async def on_disconnect(self):
        self.logger.info('Disconnected from Discord. Reconnecting...')
        await self.wait_until_ready()


    async def on_message(self, message:Message):
        if message.author.bot:
            return
        await self.process_commands(message)
        #await self.chat_client.chat(message) # emporarily disabled for the migration 
        if message.guild:
            await message_handle.tourney(message)
            await helper.vote_check(message)
         
    async def on_command_error(self, ctx:commands.Context, error:Exception):
        await error_handle.manage_context(ctx, error, self)


    async def on_error(self, event, *args, **kwargs):
        error = traceback.format_exc()
        await error_handle.manage_backend_error(error, self)


    async def  on_guild_channel_delete(self, channel:TextChannel):
        tourch = self.db.dbc.find_one({"rch" : channel.id})
        dlog = self.get_channel(config.tdlog)
        if tourch:
            self.db.dbc.delete_one({"rch" : channel.id})
            await dlog.send(f"```json\n{tourch}\n```")


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
        await self.get_channel(config.erl).send(f"```py\n{' '.join(messages)}\n```")


    async def start(self, _started_at:float) -> None:
        """
        Starts the bot and calculates the total boot time.
        Args:
            _start (float): boot start time to calculate the total boot time.
        """
        self._started_at = _started_at
        await super().start(self.db.token, reconnect=True)
