import discord, os, wavelink, asyncio, requests
from discord.ext import commands
from wavelink.ext import spotify
from discord import AllowedMentions, Intents
from modules import (message_handel as onm, channel_handel as ochd, config)

intents = Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True
intents.voice_states = True
intents.guilds = True

class Spruce(commands.AutoShardedBot):
	def __init__(self) -> None:
		self.config = config
		self.db = config.cfdata
		self.mdb = config.maindb
		self.sdb = config.spdb
		super().__init__(shard_count=config.shards, command_prefix= commands.when_mentioned_or(config.prefix),intents=intents,allowed_mentions=AllowedMentions(everyone=False, roles=False, replied_user=True, users=True),activity=discord.Activity(type=discord.ActivityType.listening, name="&help"))
		
	async def extensions(self):
		for filename in os.listdir(config.cogs_path):
		  if filename.endswith(".py"):
			  await self.load_extension(f"modules.cogs.{filename[:-3]}")
		
	async def on_ready(self):
		await self.extensions()
		try:
		  await self.node_connect()
		  await self.tree.sync()
		  stmsg = f'{self.user} is ready with {len(self.commands)} commands'
		  print(stmsg)
		  requests.post(url=config.stwbh, json={"content":"<@885193210455011369>","embeds":[{"title":"Status","description":stmsg,"color":0xff00}]})
		  while True:
			  for st in config.status:
				  await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=st))
				  await asyncio.sleep(120)
		except Exception as ex:
		  print(ex)
	
	async def node_connect(self):
		try:
		  await self.wait_until_ready()
		  await wavelink.NodePool.create_node(bot=self,host=config.m_host,port=443,password=config.m_host_psw,https=True,spotify_client=spotify.SpotifyClient(client_id=config.spot_id,client_secret=config.spot_secret))
		except Exception as e:
		  print(e)
	
	async def on_message(self, message):
	    if config.notuser(message):
	      return
	    await self.process_commands(message)
	    await onm.tourney(message)
	    await onm.ask(message, self)

	async def on_command_error(self, ctx, error):
	    await onm.error_handle(ctx, error, self)

	async def on_guild_channel_delete(self, channel):
		await ochd.ch_handel(channel=channel, bot=self)
    
bot = Spruce()
