"""
### cogs

This module initializes and registers cogs for the Spruce bot. It conditionally includes
development-only cogs based on the configuration, then defines a setup function to load
and attach these cogs to the bot instance.
"""

from modules.config import IS_DEV_ENV
from typing import TYPE_CHECKING
from cogs.dev import DevCog
from cogs.esports import EsportsCog, ScrimCog
from cogs.helpcog import HelperCog
from cogs.moderation import ModerationCog
from cogs.role import RoleCog
from cogs.tasks import TaskCog
from cogs.utility import UtilityCog
from discord.ext.commands import Cog

if TYPE_CHECKING:
    from modules.bot import Spruce

# List of class-based cogs
_cogs : list[Cog] = [
    DevCog,
    HelperCog,
    RoleCog,
    EsportsCog,
    UtilityCog,
    ModerationCog,
    TaskCog,
    ScrimCog,
]

# Dev-only cogs (empty for now)
_DEV_COGS = [

]

async def setup(bot: "Spruce") -> None:
    """
    Load all cogs into the bot.
    """
    # Load all class-based cogs
    for cog in _cogs:
        if not IS_DEV_ENV and cog in _DEV_COGS:
            continue

        await bot.add_cog(cog(bot))
        bot.logger.info(f"Extension Loaded : {cog.__name__}")

    # Load mention_responder separately using extension loader
    try:
        await bot.load_extension("cogs.mention_responder")
        bot.logger.info("Extension Loaded : mention_responder")
    except Exception as e:
        bot.logger.error(f"Failed to load mention_responder: {e}")

    bot.logger.info("All Extensions loaded")
