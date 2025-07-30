from .scrim import ScrimModel
from .tester import TesterModel
from .tourney import TourneyModel
from .autorole import GuildAutoRoleModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ext.db import Database


__all__ = (
    "ScrimModel",
    "TesterModel",
    "TourneyModel",
    "GuildAutoRoleModel",
)

def init(db:"Database"):
    GuildAutoRoleModel.col = db.autoroles
    ScrimModel.col = db.scrims
    TourneyModel._col = db.dbc
    TesterModel._col = db.testers