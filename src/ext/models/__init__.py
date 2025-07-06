from .scrim import ScrimModel
from .tester import Tester
from .tournament import TournamentModel
from .autorole import GuildAutoRoleModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ext.db import Database


__all__ = (
    "ScrimModel",
    "Tester",
    "TournamentModel",
    "GuildAutoRoleModel",
)

def init(db:"Database"):
    GuildAutoRoleModel.col = db.autoroles
    ScrimModel.col = db.scrims
    TournamentModel.col = db.dbc