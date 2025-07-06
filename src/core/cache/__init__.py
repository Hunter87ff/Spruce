"""
Cache for storing tournament-related messages.
"""

from .messages.tourneyreged import TourneyRegedCache
from .messages.tourneyconfirm import TourneyConfirmCache


__all__ = (
    "Cache",
    "TourneyRegedCache",
    "TourneyConfirmCache",
)

class Cache:
    def __init__(self):
        self.tourney_reged = TourneyRegedCache()
        self.tourney_confirm = TourneyConfirmCache()

        