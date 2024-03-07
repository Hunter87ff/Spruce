import discord, os, wavelink, asyncio, requests, time
from discord.ext import commands
from wavelink.ext import spotify
from discord import AllowedMentions, Intents
from modules import (message_handel as onm, config)
from database import Database
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
		self.core = ("channel", "dev", "helpcog", "moderation", "music", "tourney", "role", "utils")
		super().__init__(shard_count=config.shards, command_prefix= commands.when_mentioned_or(config.prefix),intents=intents,allowed_mentions=AllowedMentions(everyone=False, roles=False, replied_user=True, users=True),activity=discord.Activity(type=discord.ActivityType.listening, name="&help"))

	async def setup_hook(self) -> None:
		self.remove_command("help")
		for i in self.core:await self.load_extension(f"core.{i}")
		
	async def action(self, stch):
		await asyncio.sleep(21500)
		headers = {
			"Authorization": f"token {config.gh_api}",
			"Content-Type": "application/vnd.github+json",
		}
		response = requests.post(config.gh_action, headers=headers, json={"ref": "main"})
		if response.status_code == 204:await stch.send(f"<@{config.owner_id}>\nSuccessfully Restarted!!")
		else:await stch.send(f"<@{config.owner_id}>\nException during restart : {response.text}")
		#await self.action()

	async def on_ready(self):
		try:
			await self.tree.sync()
			stmsg = f'{self.user} is ready with {len(self.commands)} commands'
			print(stmsg)
			stch = self.get_channel(config.stl)
			#msg = await stch.send("<@885193210455011369>", embed=discord.Embed(title="Status", description=stmsg, color=0xff00))
			requests.post(url=config.stwbh, json={"content":"<@885193210455011369>","embeds":[{"title":"Status","description":stmsg,"color":0xff00}]})
			await self.action(stch)
		except Exception as ex:print(ex)

	async def on_disconnect():
		print('Disconnected from Discord. Reconnecting...')
		await self.wait_until_ready()
	
	async def on_message(self, message):
	    if config.notuser(message):return
	    await self.process_commands(message)
	    await onm.tourney(message)
	    await onm.ask(message, self)

	async def on_command_error(self, ctx, error):
	    await onm.error_handle(ctx, error, self)

	async def node_connect(self):
		try:
		  await self.wait_until_ready()
		  await wavelink.NodePool.create_node(bot=self,host=config.m_host,port=443,password=config.m_host_psw,https=True,spotify_client=spotify.SpotifyClient(client_id=config.spot_id,client_secret=config.spot_secret))
		except Exception as e:print(e)
    
bot = Spruce()