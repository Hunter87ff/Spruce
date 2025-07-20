from discord import Guild
from discord.ext import commands

__all__ = ("Cog",)


class Cog(commands.Cog):
    """A custom implementation of commands.Cog class."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return "{0.__class__.__name__}".format(self)
    
    
    async def get_member(self, guild: Guild, member_id: int):
        _member = guild.get_member(member_id)
        try:
            if _member is None:
                _member = await guild.fetch_member(member_id)

        except Exception:
            return None
        
        return _member
