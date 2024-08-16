"""
MIT License

Copyright (c) 2022 hunter87ff

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from ext import Database
import wavelink,requests, time
from discord.ext import commands
from  wavelink import Node, Pool
from modules.chat import ChatClient
from modules import (config, message_handle as onm)
from discord import AllowedMentions, Intents, ActivityType, Activity, TextChannel, utils, Message, Embed

intents = Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True
intents.voice_states = True
intents.guilds = True
pt = time.time()

class Spruce(commands.AutoShardedBot):
    def __init__(self) -> None:
        self.config = config
        self.db = Database()
        self.logger = config.logger
        self.chat_client = ChatClient(self)
        self.core = ("channel", "dev", "helpcog", "moderation", "music", "tourney", "role", "utils")
        super().__init__(shard_count=config.shards, command_prefix= commands.when_mentioned_or(config.prefix),intents=intents,allowed_mentions=AllowedMentions(everyone=False, roles=False, replied_user=True, users=True),activity=Activity(type=ActivityType.listening, name="&help"))

    async def setup_hook(self) -> None:
        if config.env["tkn"] == "TOKEN":utils.setup_logging(level=30)
        self.remove_command("help")
        for i in self.core:await self.load_extension(f"core.{i}")
        nodes = [Node(uri=config.m_host, password=config.m_host_psw)]
        await Pool.connect(nodes=nodes, client=self, cache_capacity=None)

    async def on_ready(self):
        try:
            await self.tree.sync()
            stmsg = f'{self.user} | {len(self.commands)} Commands | Version : {config.version}'
            self.logger.info(stmsg)
            await config.vote_add(self)
            requests.post(url=config.stwbh, json={"content":f"<@{config.owner_id}>","embeds":[{"title":"Status","description":stmsg,"color":0xff00}]})
        except Exception as ex:print(ex)
        
    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload) -> None:
        self.logger.info(f"Node Connected")

    async def on_disconnect(self):
        self.logger.info('Disconnected from Discord. Reconnecting...')
        await self.wait_until_ready()

    async def on_shard_disconnect(self, shard_id):
        self.logger.warning(f"Shard {shard_id} disconnected.")
        shard = self.get_shard(shard_id)
        self.logger.info(f"Reconnecting shard {shard_id}...")
        await shard.reconnect()

    async def on_message(self, message:Message):
        if config.notuser(message):return
        await self.process_commands(message)
        await self.chat_client.chat(message)
        if message.guild:
            await onm.tourney(message)
            await config.vote_check(message)
         
    async def on_command_error(self, ctx, error):
        await onm.error_handle(ctx, error, self)

    async def  on_guild_channel_delete(self, channel:TextChannel):
        tourch = config.dbc.find_one({"rch" : channel.id})
        dlog = self.get_channel(config.tdlog)
        if tourch:
            config.dbc.delete_one({"rch" : channel.id})
            await dlog.send(f"```json\n{tourch}\n```")

bot = Spruce()