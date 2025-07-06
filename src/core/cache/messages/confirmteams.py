from cachetools import TTLCache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import Message, TextChannel


class ConfirmTeamsCache:
    """
    Cache for storing tournament confirmation messages.
    """
    def __init__(self, maxsize: int = 100, ttl: int = 30):
        self.cache: TTLCache[int, list["Message"]] = TTLCache(maxsize=maxsize, ttl=ttl)


    async def get(self, channel: "TextChannel", limit=100, old=False) -> list["Message"]:
        """
        Fetches cached messages for a given channel or retrieves them from history if not cached.
        """
        _cache_messages = self.cache.get(channel.id, None)

        if _cache_messages is None:
            _cache_messages = []
            async for message in channel.history(limit=limit, oldest_first=old):
                _cache_messages.append(message)
            self.cache[channel.id] = _cache_messages

        return _cache_messages
    

    def clear(self, channel: "TextChannel"):
        """
        Clears the cache for a specific channel.
        """
        if channel.id in self.cache:
            del self.cache[channel.id]
            return True
        return False
    
    def insert(self, channel: "TextChannel", message: "Message"):
        """
        Inserts a message into the cache for a specific channel.
        """
        if channel.id not in self.cache:
            self.cache[channel.id] = []
            
        self.cache[channel.id].append(message)