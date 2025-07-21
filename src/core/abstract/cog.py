from discord import Guild
from discord.ext import commands

__all__ = ("Cog", "GroupCog")

class BaseCog:
    """A base class for custom Cog implementations."""
    
    def __init__(self, *args, **kwargs):
        pass

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
    

    async def members(self, guild: Guild):
        """gets member from cache or fetch them if not cached."""
        members = []

        if guild.members:
            members = guild.members

        async for member in guild.fetch_members(limit=None):
            members.append(member)

        return members


class Cog(commands.Cog , BaseCog):
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


class GroupCog(commands.GroupCog , BaseCog):
    """A custom implementation of commands.GroupCog class."""

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
    
    