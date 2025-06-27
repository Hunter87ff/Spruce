

from discord.ext import commands
from typing import TYPE_CHECKING
from discord import Embed

if TYPE_CHECKING:
    from modules.bot import Spruce


class TourneyMigrateCog(commands.Cog):
    """Helps to identify the latest migrated commands for the tourney module"""

    def __init__(self, bot: "Spruce"):
        self.bot = bot
        self.migrated_group = "/tourney"

    async def migrated(self, ctx: commands.Context, from_command: str, to_command: str):
        embed = Embed(
            title="Command Migration",
            description=f"The `{from_command}` command has been migrated to `{to_command}`",
        )
        await ctx.send(embed=embed)

    @commands.command(name="tourney_setup", aliases=["ts", "tsetup"])
    async def tourney_setup(self, ctx: commands.Context):
        await self.migrated(ctx, "/tourney_setup", "/tourney setup")


    @commands.command(name="auto_group", aliases=["ag", "autogroup"])
    async def auto_group(self, ctx: commands.Context):
        await self.migrated(ctx, "/auto_group", "/tourney auto_group")

    @commands.command(name="group_setup", aliases=["gsetup"])
    async def group_setup(self, ctx: commands.Context):
        await self.migrated(ctx, "/group_setup", "/tourney group_setup")


    @commands.command(name="set_manager", aliases=["sm"])
    async def set_manager(self, ctx: commands.Context):
        await self.migrated(ctx, "/set_manager", "/tourney set manager")


    @commands.command(name="tourney_log", aliases=["tlog"])
    async def tourney_log(self, ctx: commands.Context):
        await self.migrated(ctx, "/tourney_log", "/tourney set log")


    @commands.command(name="export_event_data", aliases=["export_tourney"])
    async def export_event_data(self, ctx: commands.Context):
        await self.migrated(ctx, "/export_event_data", "/tourney export")


    @commands.command(name="tourney", aliases=["t"])
    async def tourney(self, ctx: commands.Context):
        await self.migrated(ctx, "/tourney", "/tourney config")



    @commands.command(name="cancel_slot", aliases=["cancel"])
    async def cancel_slot(self, ctx: commands.Context):
        await self.migrated(ctx, "/cancel_slot", "/tourney cancel_slot")


    @commands.command(name="add_slot", aliases=["add"])
    async def add_slot(self, ctx: commands.Context):
        await self.migrated(ctx, "/add_slot", "/tourney add_slot")


    @commands.command(name="start_tourney", aliases=["start"])
    async def start_tourney(self, ctx: commands.Context):
        await self.migrated(ctx, "/start_tourney", "/tourney start")


    @commands.command(name="pause_tourney", aliases=["pt"])
    async def pause_tourney(self, ctx: commands.Context):
        await self.migrated(ctx, "/pause_tourney", "/tourney pause")


    @commands.command(name="publish", aliases=["pub"])
    async def publish(self, ctx: commands.Context):
        await self.migrated(ctx, "/publish", "/tourney publish")


    @commands.command(name="faketag")
    async def faketag(self, ctx: commands.Context):
        await self.migrated(ctx, "/faketag", "/tourney faketag")

    
    @commands.command(name="tconfig")
    async def tconfig(self, ctx: commands.Context):
        await self.migrated(ctx, "/tconfig", "/tourney list")


    @commands.command(name="girls_lobby")
    async def girls_lobby(self, ctx: commands.Context):
        await self.migrated(ctx, "/girls_lobby", "/tourney girls_lobby")


    @commands.command(name="team_name")
    async def team_name(self, ctx: commands.Context):
        await self.migrated(ctx, "/team_name", "/tourney team_name")