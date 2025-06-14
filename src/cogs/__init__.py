


"""
### cogs

This module initializes and registers cogs for the Spruce bot. It conditionally includes
development-only cogs based on the configuration, then defines a setup function to load
and attach these cogs to the bot instance.
"""
from modules.config import IS_DEV_ENV
from typing import TYPE_CHECKING
from .dev import DevCog
from .esports import EsportsCog, ScrimCog
from .helpcog import HelperCog
from .moderation import ModerationCog
from .role import RoleCog
from .tasks import TaskCog
from .utility import UtilityCog
from .esports import ScrimCog
from discord.ext.commands import Cog

if TYPE_CHECKING:
    from modules.bot import Spruce


_cogs : list[Cog] = [
    DevCog,
    HelperCog,
    RoleCog,
    EsportsCog,
    UtilityCog,
    ModerationCog,
    TaskCog,
    ScrimCog
]

_DEV_COGS = [

]



async def setup(bot: "Spruce") -> None:
    """
    Load all cogs into the bot.
    """
    for cog in _cogs:

        if not IS_DEV_ENV and cog in _DEV_COGS:
            continue

        await bot.add_cog(cog(bot))
        bot.logger.info(f"Extension Loaded : {cog.__name__}")

    bot.logger.info("All Extensions loaded")