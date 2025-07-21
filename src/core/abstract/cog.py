from discord import Guild
from discord.ext import commands

__all__ = ("Cog", "GroupCog")


class BaseCog(commands.Cog):
    """A base class for custom Cog implementations."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.emoji: str = kwargs.pop("emoji", None)
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Ensure emoji attribute exists on all subclasses
        if not hasattr(cls, 'emoji'):
            cls.emoji = None

    @property
    def cog_emoji(self) -> str:
        """Get the emoji for this cog, with fallback to None."""
        return getattr(self, 'emoji', None)

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
        """Gets members from cache or fetch them if not cached."""
        # If members are already cached, return them
        if guild.members:
            return guild.members
        
        # Otherwise, fetch all members
        members = []
        async for member in guild.fetch_members(limit=None):
            members.append(member)
        
        return members


class Cog(BaseCog):
    """A custom implementation of commands.Cog class."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return "{0.__class__.__name__}".format(self)


class GroupCog(commands.GroupCog, BaseCog):
    """A custom implementation of commands.GroupCog class."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def __str__(self):
        return "{0.__class__.__name__}".format(self)
    