import re, pytz
from datetime import datetime
from typing import TYPE_CHECKING
from ext.helper import time_parser
from ext.constants import TimeZone
from ext import permissions
from discord.ext import commands, tasks
from ext.models.scrim import ScrimModel
from discord import Embed, Message, Member, Interaction, errors,  app_commands as app




if TYPE_CHECKING:
    from modules.bot import Spruce    



class ScrimCog(commands.Cog):
    """Currently in development mode!!"""
    def __init__(self, bot:"Spruce") -> None:
        self.bot = bot
        self.monitor_scrims.start()


    @commands.hybrid_group(name="scrim", aliases=["scrims"], invoke_without_command=True)
    @commands.guild_only()
    @app.guild_only()
    @permissions.tourney_mod()
    @commands.bot_has_guild_permissions( embed_links=True, manage_messages=True, read_message_history=True )
    async def scrim(self, ctx:commands.Context):
        """Scrim commands group"""
        
 
        if isinstance(ctx, Interaction):
            await ctx.response.defer(ephemeral=True)
            

        else:
            await ctx.send(
                embed=Embed(
                    title="Scrim Commands",
                    description="Use `/scrim create` to create a new scrim.\n"
                                "Use `/scrim list` to list all scrims.\n"
                                "Use `/scrim info <scrim_id>` to get information about a specific scrim.",
                    color=0x00ff00
                ),
                ephemeral=True
            )
            

        if ctx.invoked_subcommand and not isinstance(ctx, Interaction):
            raise errors.DiscordException("All commands are moved to slash commands. Please use `/scrim` to see available commands.")
        
        return


    @scrim.command(name="create", aliases=["new"])
    @commands.guild_only()
    @app.guild_only()
    @permissions.tourney_mod()
    @commands.bot_has_guild_permissions( embed_links=True, manage_messages=True, read_message_history=True )
    async def create_scrim(self, ctx:commands.Context, name:str):
        """Create a new scrim"""
        print(f"Creating scrim with name: {name}")





    def find_team(self, message:Message):
        content = message.content.lower()
        teamname = re.search(r"team.*", content)
        if teamname is None:
            return f"{message.author}'s team"
        teamname = re.sub(r"<@*#*!*&*\d+>|team|name|[^\w\s]", "", teamname.group()).strip()
        teamname = f"{teamname.title()}" if teamname else f"{message.author}'s team"
        return teamname


    async def ft_ch(self, message:Message) -> Member|None:
        ctx = message
        current_mentions = set(ctx.mentions)
        messages = [message async for message in ctx.channel.history(limit=123)]  
        for fmsg in messages:
            previous_mentions = set(fmsg.mentions)
            if len(current_mentions.intersection(previous_mentions)) > 0:
                return fmsg.author
        return None
                    

    

    @tasks.loop(seconds=30)
    async def monitor_scrims(self):
        _time = datetime.now(pytz.timezone(TimeZone.Asia_Kolkata.value)).strftime("%H-%M")
        print(f"Checking scrims at {_time}")
