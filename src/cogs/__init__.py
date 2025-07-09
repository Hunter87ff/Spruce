


"""
### cogs

This module initializes and registers cogs for the Spruce bot. It conditionally includes
development-only cogs based on the configuration, then defines a setup function to load
and attach these cogs to the bot instance.
"""
from config import IS_DEV_ENV
from typing import TYPE_CHECKING

from .dev import DevCog
from .role import RoleCog
from .tasks import TaskCog

from .helpcog import HelperCog
from .utility import UtilityCog
from .autorole import AutoRoleCog
from .moderation import ModerationCog
from .esports import TourneyCog, ScrimCog



if TYPE_CHECKING:
    from core.bot import Spruce
    from discord.ext.commands import Cog


_cogs : list["Cog"] = [
    DevCog,
    HelperCog,
    RoleCog,
    AutoRoleCog,
    TourneyCog,
    UtilityCog,
    ModerationCog,
    TaskCog,
    ScrimCog,
]

if IS_DEV_ENV:
    from .music import MusicCog
    from .testing.test_tourney import TestTourney


    _cogs.append(MusicCog)
    _cogs.append(TestTourney)



async def setup(bot: "Spruce") -> None:
    """
    Load all cogs into the bot.
    """
    for cog in _cogs:
        
        await bot.add_cog(cog(bot))
        bot.logger.info(f"Extension Loaded : {cog.__name__}")

    bot.logger.info("All Extensions loaded")