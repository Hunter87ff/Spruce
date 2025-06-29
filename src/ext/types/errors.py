__all__ = (
    "ContextError",
    "ContextMigrationException",
)




# Context message not allowed
class ContextError(Exception):
    """Context related exception."""
    pass

class ContextMigrationException(Exception):
    """Exception raised when a context command is migrated to slash command"""
    pass

class ScrimAlreadyExists(Exception):
    """Exception raised when a scrim already exists."""
    pass

class VoiceError(Exception):
    """Exception raised for errors related to voice channels."""
    pass