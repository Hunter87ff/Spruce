from discord import Guild, Member, User
from typing import TypedDict, Unpack
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from modules.bot import Spruce

class TesterPayload(TypedDict):
    """
    Represents the payload for a tester.
    """
    id: str
    name: str
    guild: int
    level: float
    active: bool


class Tester:
    """
    Represents a tester.
    """
    def __init__(self, **kwargs: Unpack[TesterPayload]) -> None:
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.guild = kwargs.get("guild")
        self.level = kwargs.get("level")
        self.active = kwargs.get("active")

    def __eq__(self, value: Guild | Member | User) -> bool:
        if isinstance(value, Guild):
            return self.guild == value.id
        
        return self.id == value.id
    
    def to_dict(self) -> TesterPayload:
        """
        Converts the Tester instance to a dictionary.
        Returns:
            TesterPayload: A dictionary representation of the Tester instance.
        """
        return {
            "id": self.id,
            "name": self.name,
            "guild": self.guild,
            "level": self.level,
            "active": self.active
        }


    @staticmethod
    async def all(bot: "Spruce") -> list["Tester"]:
        """
        Fetches all testers from the database.
        Args:
            bot (Spruce): The bot instance.
        Returns:
            list[Tester]: A list of Tester instances.
        """
        testers_data = bot.db.testers.find().to_list(length=None)
        return [Tester(**data) for data in testers_data]
    

    async def save(self, bot: "Spruce") -> None:
        """
        Saves the Tester instance to the database.
        Args:
            bot (Spruce): The bot instance.
        """
        bot.db.testers.update_one(
            {"id": self.id},
            {"$set": self.to_dict()},
            upsert=True
        )
