from discord import Guild, Member, User
from typing import TypedDict, Unpack
from pymongo.collection import Collection
from pymongo.asynchronous.collection import AsyncCollection


class TesterPayload(TypedDict):
    """
    Represents the payload for a tester.
    """
    id: str
    name: str
    guild: int
    level: float
    active: bool


class TesterModel:
    """
    Represents a tester.
    """
    _col : Collection | AsyncCollection = None

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


    @classmethod
    async def all(cls) -> list["TesterModel"]:
        """
        Fetches all testers from the database.
        Returns:
            list[Tester]: A list of Tester instances.
        """
        testers_data : list[dict] = None
        if isinstance(cls._col, AsyncCollection):
            testers_data = await cls._col.find().to_list(length=None)
        else:
            testers_data = cls._col.find().to_list(length=None)

        return [cls(**data) for data in testers_data]
    

    async def save(self) -> None:
        """
        Saves the Tester instance to the database.
        Args:
            bot (Spruce): The bot instance.
        """
        queries: list[dict] = [ {"id": self.id}, {"$set": self.to_dict()} ]

        if isinstance(self._col, AsyncCollection):
            await self._col.update_one( filter=queries[0], update=queries[1], upsert=True)
        else:
            self._col.update_one( filter=queries[0], update=queries[1], upsert=True)

        return self
