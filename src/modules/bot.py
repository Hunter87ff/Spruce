import discord
from discord.ext import commands
from discord import AllowedMentions, Intents
intents = Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True
intents.voice_states = True
intents.guilds = True
from modules import config


class Spruce(commands.AutoShardedBot):
   def __init__(self) -> None:
     super().__init__(
      shard_count=10, 
      command_prefix= commands.when_mentioned_or(config.prefix),
      intents=intents,
      allowed_mentions=AllowedMentions(everyone=False, roles=False, replied_user=True, users=True),
      activity=discord.Activity(type=discord.ActivityType.listening, name="&help"))

bot = Spruce()