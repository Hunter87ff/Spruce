from typing import TYPE_CHECKING, Unpack, TypedDict


from pymongo.collection import Collection
from pymongo.asynchronous.collection import AsyncCollection



class GuildAutoRoleModelDict(TypedDict):
    guild_id: int
    auto_role_human: list[int] | None
    auto_role_bot: list[int] | None
    auto_role_all: list[int] | None


class GuildAutoRoleModel:
    _cache : dict[int, 'GuildAutoRoleModel'] = {}
    col: Collection | AsyncCollection = None

    def __init__(self, **kwargs : Unpack[GuildAutoRoleModelDict]):
        """
        GuildAutoRoleModel constructor

        :param kwargs: keyword arguments
        :param guild_id: int
        :param auto_role_human: list of int
        :param auto_role_bot: list of int
        :param auto_role_all: list of int
        """
        self.guild_id:int = kwargs.get("guild_id")
        self.auto_role_human:int = kwargs.get("auto_role_human", None)
        self.auto_role_bot:int = kwargs.get("auto_role_bot", None)
        self.auto_role_all:int = kwargs.get("auto_role_all", None)

        if kwargs.get("col", None):
            GuildAutoRoleModel.col = kwargs.get("col")

    def to_dict(self):
        return {
            "guild_id": self.guild_id,
            "auto_role_human": self.auto_role_human,
            "auto_role_bot": self.auto_role_bot,
            "auto_role_all": self.auto_role_all
        }
    
    @classmethod
    async def create(cls, guild_id:int, auto_role_human:list[int]=None, auto_role_bot:list[int]=None, auto_role_all:list[int]=None) -> 'GuildAutoRoleModel':
        """Create a new GuildAutoRoleModel
        
        :param guild_id: int
        :param auto_role_human: role id to assign to human members
        :param auto_role_bot: role id to assign to bot members
        :param auto_role_all: role id to assign to all members
        :return: GuildAutoRoleModel or None
        """
        query: dict[str, int] = {"guild_id": guild_id}
        _guild : dict = None

        if isinstance(cls.col, AsyncCollection):
            _guild = await cls.col.find_one(query)
        else:
            _guild = cls.col.find_one(query)

        if _guild:
            return None
        
        new_guild = cls(
            guild_id=guild_id,
            auto_role_human=auto_role_human,
            auto_role_bot=auto_role_bot,
            auto_role_all=auto_role_all
        )
        await new_guild.save()
        return new_guild


    @classmethod
    async def find_one(cls, guild_id:int) -> 'GuildAutoRoleModel':
        """Find a single GuildAutoRoleModel by guild_id"""
        _guild:GuildAutoRoleModel = cls._cache.get(guild_id)
        
        if _guild:
            return _guild

        if isinstance(cls.col, AsyncCollection):
            _guild = await cls.col.find_one({"guild_id": guild_id})
        else:
            _guild = cls.col.find_one({"guild_id": guild_id})

        if not _guild:
            return None
        
        return cls(**_guild)
    

    def reset(self):
        _del = self.col.delete_one({
            "guild_id": self.guild_id
        })
        if _del.deleted_count == 0:
            return None

        self._cache.pop(self.guild_id, None)
        return True
    

    async def save(self) -> None:
        """Save the GuildAutoRoleModel to the database"""
        query = [ {"guild_id": self.guild_id} , {"$set": self.to_dict()} ]
        if isinstance(self.col, AsyncCollection):
            await self.col.update_one( filter=query[0], update=query[1], upsert=True)

        else:
            self.col.update_one( filter=query[0], update=query[1], upsert=True)
            
        self._cache[self.guild_id] = self
        return self