"""
Cache for storing tournament-related messages.
"""


from .messages.confirmteams import ConfirmTeamsCache


__all__ = (
    "Cache",
)

class Cache:
    def __init__(self):
        self.tourney_reged = ConfirmTeamsCache(ttl=60, maxsize=100)
        self.tourney_confirm = ConfirmTeamsCache(ttl=160, maxsize=100)

        