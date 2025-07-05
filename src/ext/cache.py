from cachetools import TTLCache
from typing import TYPE_CHECKING, AsyncIterator

if TYPE_CHECKING:
    from discord import Message, TextChannel

# Initialize a cache with a time-to-live of 10 seconds and a maximum size of 100
cache_con_msg_by_channel: TTLCache[int, AsyncIterator["Message"]] = TTLCache(maxsize=100, ttl=10)
cache_reg_msg_by_channel: TTLCache[int, AsyncIterator["Message"]] = TTLCache(maxsize=100, ttl=30)

def get_cache_con_msg(channel: "TextChannel", limit=100, old=False) -> AsyncIterator["Message"]:
    _cache_messages = cache_con_msg_by_channel.get(channel.id, None)
    if _cache_messages is None:
        _cache_messages = channel.history(limit=limit, oldest_first=old)
        cache_con_msg_by_channel[channel.id] = _cache_messages
    return _cache_messages


def get_cache_reg_msg(channel: "TextChannel", limit=100, old=False) -> AsyncIterator["Message"]:
    _cache_messages = cache_reg_msg_by_channel.get(channel.id, None)
    if _cache_messages is None:
        _cache_messages = channel.history(limit=limit, oldest_first=old)
        cache_reg_msg_by_channel[channel.id] = _cache_messages
    return _cache_messages