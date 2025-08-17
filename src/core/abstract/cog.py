from __future__ import annotations


from discord import Guild
import discord
from discord.ext import commands
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.bot import Spruce


__all__ = ("Cog", "GroupCog")


class BaseCog(commands.Cog):
    """A base class for custom Cog implementations."""
    _CACHE_HOOKS : dict[int, discord.Webhook] = {}
    hidden : bool = False
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.emoji: str = kwargs.pop("emoji", None)
        self.bot: "Spruce" = kwargs.pop("bot", None)

        
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


    async def fetch_message(self, channel_id: int, message_id: int):
            try:
                channel = self.bot.get_channel(channel_id)
                return await channel.fetch_message(message_id)
            
            except Exception:
                return None
            


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
    

    async def webhook(self, channel : discord.TextChannel):
        if channel.id in self._CACHE_HOOKS:
            return self._CACHE_HOOKS[channel.id]

        try:
            webhooks = await channel.webhooks()
            if webhooks:
                self._CACHE_HOOKS[channel.id] = webhooks[0]
                return webhooks[0]
            
            _webhook = await channel.create_webhook(name=channel.guild.me.name)
            self._CACHE_HOOKS[channel.id] = _webhook
            return _webhook
        
        except Exception:
            self._CACHE_HOOKS.pop(channel.id, None)
            return None


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
    