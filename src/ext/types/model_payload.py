from __future__ import annotations
from typing import TypedDict




class TournamentPayload(TypedDict):
    name: str
    status: bool
    guild: int
    rch: int
    cch: int
    mentions: int
    ftch: bool
    crole: int
    gch: int
    tslot: int
    reged: int
    spg: int
    cgp: int | None
    mch: int
    cat: int


class ScrimPayload(TypedDict, total=False):
        status:bool
        name : str
        guild_id:int
        mentions:int
        reg_channel:int
        manage_channel:int
        slot_channel:int
        idp_role : int
        open_time:int
        close_time:int
        total_slots:int
        time_zone:str
        ping_role:int

        

class TourneyTeamPayload(TypedDict):
    _id : int #message id
    tid : int
    name : str
    capt : int
    members : set[int]


class TourneyRoundPayload(TypedDict):
     _id: int  # Unique identifier for the round
     tid: int  # Tournament ID
     name: str
     spg: int
     slots: int
     teams: set[int]

