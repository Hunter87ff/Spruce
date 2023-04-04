import discord
from discord.ext import commands
from discord import app_commands, Interaction
import typing


class Slash(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		#self.tree = app_commands.CommandTree(self)

	async def setup_hook(self):
	    await self.tree.sync(guild=None)
	    

	@app_commands.command()
	@commands.bot_has_permissions(manage_roles=True)
	@commands.has_permissions(manage_roles=True)
	async def lock(self, interaction: Interaction, role:discord.Role=None, channel:typing.Union[discord.TextChannel, discord.VoiceChannel]=None):
		if not role:
			role = interaction.guild.default_role
		if not channel:
			channel = interaction.channel
		overwrite = channel.overwrites_for(role)
		overwrite.update(send_messages=False, add_reactions=False, connect=False, speak=False)
		await channel.set_permissions(role, overwrite=overwrite)
		await interaction.response.send_message(f"Channel {channel.mention} Locked From `{role.name}`")


async def setup(bot):
    await bot.add_cog(Slash(bot))