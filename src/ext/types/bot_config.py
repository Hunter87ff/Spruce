from typing import TypedDict


class BotConfig(TypedDict):
    token: str
    prefix: str
    version: str
    shards: int
    dev_env: bool
    lavalink: bool
    testers: list[int]
    developers: list[int]