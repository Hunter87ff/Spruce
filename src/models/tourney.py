import time
from typing import TYPE_CHECKING
from typing import Unpack, TypedDict

if TYPE_CHECKING:
    from discord import Message, Member
    from pymongo.asynchronous.collection import AsyncCollection
    from core.bot import Spruce

_tourney_cache: dict[int, 'TourneyModel'] = {}

class TournamentPayload(TypedDict):
    guild_id: int
    reg_channel: int
    slot_channel: int
    confirm_role: int
    group_channel: int
    total_slot: int
    team_count: int
    auto_group: str | None
    published: str | None
    slot_per_group: int
    current_group: int | None
    created_at: int


class ConfirmedTeamModel:
    def __init__(self, message: 'Message'):
        self.message: 'Message' = message
        if not isinstance(message, Message):
            raise TypeError("message must be an instance of discord.Message")
        
        if message.author.id != message.guild.me.id:
            raise ValueError("message must be sent by the bot itself")
        
        if len(message.mentions) != 1 or not message.embeds:
            raise ValueError("message must mention exactly one user and contain an embed")
        
        self.captain = message.mentions[1]
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
            del self
        else:
            raise ValueError("Message has already been deleted or does not exist.")


class TourneyModel:
    """
    Tourney class represents a tournament with various properties.
    """
    col: "AsyncCollection" = None  # MongoDB collection name for tournaments
    bot : "Spruce" = None  # Reference to the bot instance

    def __init__(self, **kwargs: Unpack[TournamentPayload]) -> None:
        self.guild_id: int = kwargs.get("guild_id")
        self.name: str = kwargs.get("name", "Tournament")
        self.reg_channel: int = kwargs.get("rch")
        self.slot_channel: int = kwargs.get("cch")
        self.group_channel: int = kwargs.get("gch")
        self.slot_manager: int = kwargs.get("mch", None) #slot manager channel id
        self.mentions: int = kwargs.get("mentions", 4) # minimum mentions required to register
        self.confirm_role: int = kwargs.get("crole") # confirmation role id
        self.total_slots: int = kwargs.get("slots") # total slots available in the tournament
        self.team_count: int = kwargs.get("reged", 0) # number of teams registered in the tournament
        self.published: str = kwargs.get("published", None)
        self.slot_per_group: int = kwargs.get("spg", 12) #number of slots per group (default: 12)
        self.current_group: int = kwargs.get("current_group", 0) # current group number (default: 0)
        self.created_at: int = kwargs.get("created_at", int(time.time()))

        if kwargs.get("col"):
            self.col = kwargs.get("col", None)

    def __repr__(self) -> str:
        return f"<Tournament guild_id={self.guild_id} rch={self.reg_channel} cch={self.slot_channel} crole={self.confirm_role} gch={self.group_channel} tslot={self.total_slots} reged={self.team_count} pub={self.published} spg={self.slot_per_group} cgp={self.current_group} created_at={self.created_at}>"
    
    def __str__(self) -> str:
        return f"Tournament(guild_id={self.guild_id}, reg_channel={self.reg_channel}, slot_channel={self.slot_channel}, confirm_role={self.confirm_role}, group_channel={self.group_channel}, total_slot={self.total_slots}, team_count={self.team_count}, published={self.published}, slot_per_group={self.slot_per_group}, current_group={self.current_group}, created_at={self.created_at})"


    def __eq__(self, value):
        if isinstance(value, int):
            return self.reg_channel == value
        elif isinstance(value, TourneyModel):
            return self.reg_channel == value.reg_channel and self.guild_id == value.guild_id
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
            isinstance(self.published, (str, type(None))),
            isinstance(self.slot_per_group, int) and self.slot_per_group > 0 and self.slot_per_group <= 100,
            isinstance(self.current_group, (int, type(None))),
            isinstance(self.created_at, int)
        ])


    def to_dict(self) -> TournamentPayload:
        """Converts the Tournament instance to a dictionary.

        Returns:
            TournamentPayload: A dictionary representation of the Tournament instance.
        """
        return {
            "guild_id": self.guild_id,
            "reg_channel": self.reg_channel,
            "slot_channel": self.slot_channel,
            "confirm_role": self.confirm_role,
            "group_channel": self.group_channel,
            "total_slot": self.total_slots,
            "team_count": self.team_count,
            "published": self.published,
            "slot_per_group": self.slot_per_group,
            "current_group": self.current_group,
            "slot_manager": self.slot_manager,
            "created_at": self.created_at
        }
    

    
    async def save(self):
        if not self.validate():
            raise ValueError("Invalid Tournament instance. Cannot save to database.")

        return await self.col.update_one(
            {"reg_channel": self.reg_channel, "guild_id": self.guild_id},
            {"$set": self.to_dict()},
            upsert=True
        )
    

    @classmethod
    async def find_one(cls, **kwargs:Unpack[TournamentPayload]):
        """Fetches a Tournament instance from the database.

        Args:
            **kwargs: Keyword arguments to filter the tournament.

        Returns:
            TournamentModel: An instance of TournamentModel if found, otherwise None.
        """
        document = await cls.col.find_one(**kwargs)
        if document is None:
            return None
        return cls(**document)

    
    @classmethod
    async def get(cls, reg_channel:int) -> 'TourneyModel':
        """Fetches a Tournament instance from the database by its registration channel.

        Args:
            reg_channel (int): The registration channel ID.

        Returns:
            TourneyModel: An instance of TourneyModel if found, otherwise None.
        """
        if reg_channel in _tourney_cache:
            return _tourney_cache[reg_channel]

        data = await cls.find_one({"reg_channel": reg_channel})
        if not data:
            return None

        tournament = cls(**data)
        _tourney_cache[reg_channel] = tournament
        return tournament
    

    @classmethod
    async def create(cls, **kwargs: Unpack[TournamentPayload]) -> 'TourneyModel':
        """Creates a new Tournament instance and saves it to the database.

        Args:
            **kwargs: Keyword arguments to initialize the tournament.

        Returns:
            TourneyModel: The created TournamentModel instance.
        """
        if not kwargs.get("guild_id") or not kwargs.get("reg_channel"):
            raise ValueError("guild_id and reg_channel are required to create a tournament.")

        existing_tournament = await cls.find_one({"reg_channel": kwargs["reg_channel"], "guild_id": kwargs["guild_id"]})
        if existing_tournament:
            return existing_tournament

        tournament = cls(**kwargs)
        await tournament.save()
        _tourney_cache[tournament.reg_channel] = tournament
        return tournament
    

    @classmethod
    async def delete(cls, reg_channel: int) -> bool:
        """Deletes a Tournament instance from the database.

        Args:
            reg_channel (int): The registration channel ID of the tournament to delete.

        Returns:
            bool: True if the tournament was deleted, False otherwise.
        """
        if reg_channel not in _tourney_cache:
            return False
        
        _tourney_cache.pop(reg_channel, None)
        result = await cls.col.delete_one({"reg_channel": reg_channel})
        if result.deleted_count > 0:
            _tourney_cache.pop(reg_channel, None)
            return True
        return False