"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2022 hunter87.dev@gmail.com
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.
"""
import ast
import time
import traceback
import wavelink
from discord.ext import commands
from wavelink import Node, Pool
from modules.chat import ChatClient
from ext import Database, Logger, error as error_handle
from modules import (config, message_handle)
from discord import AllowedMentions, Intents, ActivityType, Activity, TextChannel, utils, Message


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
        self.chat_client = ChatClient(self)
        self.core = ("channel", "dev", "helpcog", "moderation", "tourney", "role", "utils", "tasks", "music")

        super().__init__(
            shard_count=config.shards, 
            command_prefix= commands.when_mentioned_or(config.prefix),
            intents=intents,
            allowed_mentions=AllowedMentions(everyone=False, roles=False, replied_user=True, users=True),
            activity=Activity(type=ActivityType.listening, name="&help")
        )

    async def setup_hook(self) -> None:
        if config.env["tkn"] == "TOKEN":
            utils.setup_logging(level=30)

        self.remove_command("help")

        for i in self.core:
            await self.load_extension(f"core.{i}")
        if config.shards==1:
            await self.load_extension("core.scrim")
        Logger.info("Core Extensions Loaded")
        if config.LOCAL_LAVA:
            _nodes = [Node(uri=config.LOCAL_LAVA[0], password=config.LOCAL_LAVA[1])]
            await Pool.connect(nodes=_nodes, client=self, cache_capacity=None)


    async def on_ready(self):
        """Event that triggers when the bot is ready."""
        try:
            await self.tree.sync()
            stmsg = f'{self.user} | {len(self.commands)} Commands | Version : {config.version} | Boot Time : {round(time.time() - self._started_at, 2)}s'
            Logger.info(stmsg)
            await config.vote_add(self)
            config.webpost(
                url=self.db.cfdata.get("stwbh"), 
                json={
                    "content":f"<@{config.owner_id}>",
                    "embeds":[
                        {
                            "title":"Status",
                            "description":stmsg,
                            "color":0xff00
                        }
                    ]
                }
            )
        except Exception as ex:print(ex)
        
    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload) -> None:
        Logger.info(f"Node Connected {payload.node.identifier}")

    async def on_disconnect(self):
        Logger.info('Disconnected from Discord. Reconnecting...')
        await self.wait_until_ready()

    # async def fetch_payment_hook(self, message:Message):
    #     """Fetches the payment object from the message content in paylog channel and updates the primedbc"""
    #     if message.channel.id != config.paylog or (not message.webhook_id) or not payment: return
    #     try:
    #         obj:payment.PaymentHook = payment.PaymentHook(ast.literal_eval(message.content.replace("```", "").replace("\n", "")))
    #         if isinstance(obj, payment.PaymentHook) and obj.payment_status == "SUCCESS":
    #             return self.db.primedbc.update_one({"guild_id":obj.guild_id}, {"$set":obj.to_dict}, upsert=True)
    #         if isinstance(obj, payment.PaymentHook) and obj.payment_status == "FAILED":
    #             return self.db.paydbc.delete_one({"guild_id":obj.guild_id})
    #         print("Ignored the check")
    #     except Exception:
    #         traceback.print_exc()

    async def on_message(self, message:Message):
        # if message.channel.id == config.paylog: 
        #     await self.fetch_payment_hook(message)
        if config.notuser(message):return
        await self.process_commands(message)
        await self.chat_client.chat(message)
        if message.guild:
            await message_handle.tourney(message)
            await config.vote_check(message)
         
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


    async def error_log(self, message:str) -> None:
        """
        Logs the error message to the error log channel.
        Args:
            message (str): The error message to log.
        """
        await self.get_channel(config.erl).send(f"```py\n{message}\n```")


    async def start(self, _started_at:float) -> None:
        """
        Starts the bot and calculates the total boot time.
        Args:
            _start (float): boot start time to calculate the total boot time.
        """
        self._started_at = _started_at
        await super().start(self.db.token, reconnect=True)