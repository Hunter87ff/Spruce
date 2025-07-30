import asyncio
import time
from typing import TYPE_CHECKING, Literal
from typing import Unpack, TypedDict
from pymongo.collection import Collection
from pymongo.asynchronous.collection import AsyncCollection


if TYPE_CHECKING:
    from discord import Message, Member
    from core.bot import Spruce


class TournamentPayload(TypedDict):
    name: str
    status: bool
    guild: int
    rch: int
    cch: int
    mentions: int
    crole: int
    gch: int
    tslot: int
    reged: int
    spg: int
    cgp: int | None
    cat: int


class ConfirmedTeamModel:
    def __init__(self, message: 'Message'):
        self.message: 'Message' = message
        if not isinstance(message, Message):
            raise TypeError("message must be an instance of discord.Message")
        
        if message.author.id != message.guild.me.id:
            raise ValueError("message must be sent by the bot itself")
        
        if len(message.mentions) != 1 or not message.embeds:
            raise ValueError("message must mention exactly one user and contain an embed")
        
        self.captain = message.mentions[0]
        self.name = message.content.replace(self.captain.mention, "").strip() if message.content else f"{self.captain.name}'s Team"
        self.players = message.embeds[0].description.split("\n")[1].replace("Players: ", "").split(", ") if message.embeds[0].description else []


    
    async def edit(self, name: str = None, captain: "Member" = None):
        """Edit the team name and/or players in the confirmation message."""

        content = f"{name or self.name} {captain.mention or self.captain.mention}"
        embed = self.message.embeds[0]
        embed.description = embed.description.replace(self.name, name) if name else embed.description
 
        self.name = name if name else self.name
        self.captain = captain if captain else self.captain
        
        await self.message.edit(content=content, embed=embed)


    async def delete(self):
        """Delete the confirmation message."""
        if self.message:
            await self.message.delete()
            self.message = None
        else:
            raise ValueError("Message has already been deleted or does not exist.")


class TourneyModel:
    """
    Tourney class represents a tournament with various properties.
    """
    _cache: dict[int, 'TourneyModel'] = {}
    _col: Collection | AsyncCollection = None  # MongoDB collection name for tournaments
    bot : "Spruce" = None  # Reference to the bot instance

    def __init__(self, **kwargs: Unpack[TournamentPayload]) -> None:
        self.guild_id: int = kwargs.get("guild")
        self.status: bool = kwargs.get("status", True) # True if the tournament is active, False otherwise
        self.name: str = kwargs.get("name", "Tournament")
        self.reg_channel: int = kwargs.get("rch")
        self.slot_channel: int = kwargs.get("cch")
        self.group_channel: int = kwargs.get("gch")
        self.slot_manager: int = kwargs.get("mch") #slot manager channel id
        self.mentions: int = kwargs.get("mentions", 4) # minimum mentions required to register
        self.confirm_role: int = kwargs.get("crole") # confirmation role id
        self.total_slots: int = kwargs.get("tslot") # total slots available in the tournament
        self.team_count: int = kwargs.get("reged", 0) # number of teams registered in the tournament
        self.slot_per_group: int = kwargs.get("spg", 12) #number of slots per group (default: 12)
        self.current_group: int = kwargs.get("cgp", 0) # current group number (default: 0)
        self.created_at: int = kwargs.get("cat", int(time.time()))


        if kwargs.get("col"):
            self._col = kwargs.get("col", None)

    def __repr__(self) -> str:
        return f"<Tournament guild_id={self.guild_id} rch={self.reg_channel} cch={self.slot_channel} crole={self.confirm_role} gch={self.group_channel} tslot={self.total_slots} reged={self.team_count} pub={self.published} spg={self.slot_per_group} cgp={self.current_group} created_at={self.created_at}>"
    
    def __str__(self) -> str:
        return f"Tournament(guild_id={self.guild_id}, reg_channel={self.reg_channel}, slot_channel={self.slot_channel}, confirm_role={self.confirm_role}, group_channel={self.group_channel}, total_slot={self.total_slots}, team_count={self.team_count}, published={self.published}, slot_per_group={self.slot_per_group}, current_group={self.current_group}, created_at={self.created_at})"


    def __eq__(self, value):
        if isinstance(value, int):
            return self.reg_channel == value
        
        elif isinstance(value, TourneyModel):
            return any([
                self.reg_channel == value.reg_channel,
                self.slot_manager == value.slot_manager,
            ])
        return False


    def validate(self) -> bool:
        """Validates the Tournament instance.

        Returns:
            bool: True if the instance is valid, False otherwise.
        """
        
        return all([
            isinstance(self.guild_id, int),
            isinstance(self.reg_channel, int),
            isinstance(self.slot_channel, int),
            isinstance(self.confirm_role, int),
            isinstance(self.group_channel, int),
            isinstance(self.total_slots, int) and self.total_slots > 0,
            isinstance(self.team_count, int) and self.team_count >= 0,
            isinstance(self.slot_per_group, int) and self.slot_per_group > 0 and self.slot_per_group <= 25,
            isinstance(self.created_at, int)
        ])


    def to_dict(self) -> TournamentPayload:
        """Converts the Tournament instance to a dictionary.

        Returns:
            TournamentPayload: A dictionary representation of the Tournament instance.
        """
        return {
            "guild": self.guild_id,
            "rch": self.reg_channel,
            "cch": self.slot_channel,
            "mentions": self.mentions,
            "crole": self.confirm_role,
            "gch": self.group_channel,
            "tslot": self.total_slots,
            "reged": self.team_count,
            "spg": self.slot_per_group,
            "cgp": self.current_group,
            "mch": self.slot_manager,
            "cat": self.created_at
        }
    

    
    async def save(self):
        if not self.validate():
            raise ValueError("Invalid Tournament instance. Cannot save to database.")
        
        if isinstance(self._col, Collection):
            self._col.update_one(
                {"rch": self.reg_channel, "guild": self.guild_id},
                {"$set": self.to_dict()},
                upsert=True
            )

        elif isinstance(self._col, AsyncCollection):
            await self._col.update_one(
                {"rch": self.reg_channel, "guild": self.guild_id},
                {"$set": self.to_dict()},
                upsert=True
            )

        return self
    

    @classmethod
    async def find_one(cls, **kwargs:Unpack[TournamentPayload]):

        # async find from cache 
        _temp = cls(**kwargs)
        for tourney in cls._cache.values():
            if _temp == tourney:
                return tourney
            await asyncio.sleep(0)

        document: dict = cls._col.find_one(kwargs) if isinstance(cls._col, Collection) else await cls._col.find_one(kwargs)
        if document is None:
            return None
        # Create a new instance of TourneyModel with the fetched data
        
        _temp = cls(**document)
        cls._cache[_temp.reg_channel] = _temp

        return _temp


    @classmethod
    async def get(cls, reg_channel:int) -> 'TourneyModel':
        """Fetches a Tournament instance from the database by its registration channel.

        Args:
            reg_channel (int): The registration channel ID.

        Returns:
            TourneyModel: An instance of TourneyModel if found, otherwise None.
        """
        if reg_channel in cls._cache:
            return cls._cache[reg_channel]

        data = await cls.find_one(reg_channel=reg_channel)
        if not data:
            return None

        tournament = cls(**data)
        cls._cache[reg_channel] = tournament
        return tournament
    

    @classmethod
    async def create(cls, **kwargs: Unpack[TournamentPayload]) -> 'TourneyModel':
        """Creates a new Tournament instance and saves it to the database.

        Args:
            **kwargs: Keyword arguments to initialize the tournament.

        Returns:
            TourneyModel: The created TournamentModel instance.
        """
        if any([
            kwargs.get("guild_id") is None,
            kwargs.get("reg_channel") is None
        ]):
            raise ValueError("guild_id and reg_channel are required to create a tournament.")

        existing_tournament = await cls.get(kwargs.get("reg_channel"))
        if existing_tournament:
            return existing_tournament
        print("Creating new tournament with kwargs:", kwargs)
        tournament = TourneyModel(**kwargs)
        await tournament.save()
        cls._cache[tournament.reg_channel] = tournament
        return tournament
    

    @classmethod
    async def delete(cls, reg_channel: int) -> bool:
        """Deletes a Tournament instance from the database.

        Args:
            reg_channel (int): The registration channel ID of the tournament to delete.

        Returns:
            bool: True if the tournament was deleted, False otherwise.
        """
        if reg_channel not in cls._cache:
            return False

        cls._cache.pop(reg_channel, None)
        result = cls._col.delete_one(
            filter={"reg_channel": reg_channel}
        ) if isinstance(cls._col, Collection) else await cls._col.delete_one(
            filter={"reg_channel": reg_channel}
        )
        
        if result.deleted_count > 0:
            cls._cache.pop(reg_channel, None)
            return True
        return False