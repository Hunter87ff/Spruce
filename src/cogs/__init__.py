


"""
### cogs

This module initializes and registers cogs for the Spruce bot. It conditionally includes
development-only cogs based on the configuration, then defines a setup function to load
and attach these cogs to the bot instance.
"""
from modules.config import activeModules
from typing import TYPE_CHECKING
from cogs.channel import ChannelCog
from cogs.dev import DevCog
from cogs.tourney import EsportsCog
from cogs.helpcog import HelperCog
from cogs.moderation import ModerationCog
from cogs.role import RoleCog
from cogs.tasks import TaskCog
from cogs.utility import UtilityCog
from cogs.scrim import ScrimCog
from discord.ext.commands import Cog


_cogs : list[Cog] = [
    ChannelCog,
    DevCog,
    HelperCog,
    RoleCog,
    EsportsCog,
    UtilityCog,
    ModerationCog,
    TaskCog,
    # ScrimCog
]

if activeModules.music:
    from cogs.music import MusicCog
    _cogs.append(MusicCog)
    

if TYPE_CHECKING:
    from modules.bot import Spruce


async def setup(bot: "Spruce") -> None:
    """
    Load all cogs into the bot.
    """
    for cog in _cogs:
        await bot.add_cog(cog(bot))
        bot.logger.info(f"Extension Loaded : {cog.__name__}")

    bot.logger.info("All Extensions loaded")