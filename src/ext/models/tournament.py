from datetime import datetime
from ..db import Database
from typing import Unpack, TypedDict


_tournament_cache: dict[int, 'TournamentModel'] = {}
collection = Database().sprucedb["tourney"]


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
    created_at: datetime



class TournamentModel:
    """
    Tourney class represents a tournament with various properties.
    """
    def __init__(self, **kwargs: Unpack[TournamentPayload]) -> None:
        self.guild_id: int = kwargs.get("guild_id")
        self.name: str = kwargs.get("name", "Tournament")
        self.reg_channel: int = kwargs.get("reg_channel")
        self.slot_channel: int = kwargs.get("slot_channel")
        self.group_channel: int = kwargs.get("group_channel")
        self.slot_manager: int = kwargs.get("slot_manager", None) #slot manager channel id
        self.mentions: int = kwargs.get("mentions", 4) # minimum mentions required to register
        self.confirm_role: int = kwargs.get("confirm_role") # confirmation role id
        self.total_slots: int = kwargs.get("total_slot") # total slots available in the tournament
        self.team_count: int = kwargs.get("team_count", 0) # number of teams registered in the tournament
        self.auto_group: bool = kwargs.get("auto_group", False) # whether the tournament has auto grouping enabled (deprecated)
        self.published: str = kwargs.get("published", None)
        self.slot_per_group: int = kwargs.get("slot_per_group", 12) #number of slots per group (default: 12)
        self.current_group: int = kwargs.get("current_group", 0) # current group number (default: 0)
        self.created_at: datetime = kwargs.get("created_at", datetime.now())


    def __repr__(self) -> str:
        return f"<Tournament guild_id={self.guild_id} rch={self.reg_channel} cch={self.slot_channel} crole={self.confirm_role} gch={self.group_channel} tslot={self.total_slots} reged={self.team_count} auto_grp={self.auto_group} pub={self.published} spg={self.slot_per_group} cgp={self.current_group} created_at={self.created_at}>"
    
    def __str__(self) -> str:
        return f"Tournament(guild_id={self.guild_id}, reg_channel={self.reg_channel}, slot_channel={self.slot_channel}, confirm_role={self.confirm_role}, group_channel={self.group_channel}, total_slot={self.total_slots}, team_count={self.team_count}, auto_group={self.auto_group}, published={self.published}, slot_per_group={self.slot_per_group}, current_group={self.current_group}, created_at={self.created_at})"


    def __eq__(self, value):
        if isinstance(value, int):
            return self.reg_channel == value
        elif isinstance(value, TournamentModel):
            return self.reg_channel == value.reg_channel and self.guild_id == value.guild_id
        elif isinstance(value, datetime):
            return self.created_at == value
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
            isinstance(self.auto_group, bool),
            isinstance(self.published, (str, type(None))),
            isinstance(self.slot_per_group, int) and self.slot_per_group > 0,
            isinstance(self.current_group, (int, type(None))),
            isinstance(self.created_at, datetime)
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
            "auto_group": self.auto_group,
            "published": self.published,
            "slot_per_group": self.slot_per_group,
            "current_group": self.current_group,
            "slot_manager": self.slot_manager,
            "created_at": self.created_at
        }
    
    async def save(self):
        if not self.validate():
            raise ValueError("Invalid Tournament instance. Cannot save to database.")

        return collection.update_one(
            {"reg_channel": self.reg_channel, "guild_id": self.guild_id},
            {"$set": self.to_dict()},
            upsert=True
        )
    

    @classmethod
    async def findOne(cls, **kwargs:Unpack[TournamentPayload]):
        """Fetches a Tournament instance from the database.

        Args:
            **kwargs: Keyword arguments to filter the tournament.

        Returns:
            TournamentModel: An instance of TournamentModel if found, otherwise None.
        """
        return collection.find_one(**kwargs)

    
    @classmethod
    async def get(cls, reg_channel:int) -> 'TournamentModel':
        """Fetches a Tournament instance from the database by its registration channel.

        Args:
            reg_channel (int): The registration channel ID.

        Returns:
            TournamentModel: An instance of TournamentModel if found, otherwise None.
        """
        if reg_channel in _tournament_cache:
            return _tournament_cache[reg_channel]

        data = await cls.findOne({"reg_channel": reg_channel})
        if not data:
            return None

        tournament = cls(**data)
        _tournament_cache[reg_channel] = tournament
        return tournament