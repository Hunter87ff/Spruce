from discord import Embed, utils
from ext import color, emoji



class EmbedBuilder(Embed):
    """
    Base class for all embeds used in the bot.
    Provides a consistent look and feel across different embeds.
    """

    def __init__(self, title: str = None, description: str = None, color: int = color.cyan, emoji: str = None, short_desc: str = None, timestamp=utils.utcnow()):
        super().__init__(title=title, description=description, color=color)
        # self.set_footer(text="Spruce | Born to host battles")
        self.timestamp = timestamp
        self.emoji = emoji
        self.short_desc = short_desc

    @classmethod
    def warning(cls, message: str) -> "EmbedBuilder":
        """
        Adds a warning message to the embed.
        """
        embed = cls(description=f"{emoji.cross} {message}", color=color.red)
        return embed

    @classmethod
    def success(cls, message: str) -> "EmbedBuilder":
        """
        Adds a success message to the embed.
        """
        embed = cls(description=f"{emoji.tick} {message}", color=color.green)
        return embed
    
    @classmethod
    def alert(cls, message: str) -> "EmbedBuilder":
        """
        Adds an alert message to the embed.
        """
        embed = cls(description=f"{emoji.cross} {message}", color=color.yellow)
        return embed