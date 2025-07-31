from .scrim import ScrimModel
from .tester import TesterModel

from .autorole import GuildAutoRoleModel
from .tourney import TourneyModel, TeamModel, TourneyRoundModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ext.db import Database


__all__ = (
    "ScrimModel",
    "TesterModel",
    "TourneyModel",
    "GuildAutoRoleModel",
    "TeamModel",
    "TourneyRoundModel",
)

def init(db:"Database"):
    GuildAutoRoleModel.col = db.autoroles
    ScrimModel.col = db.scrims
    TourneyModel._col = db.sprucedb["tournaments"]
    TesterModel._col = db.testers
    TeamModel._col = db.sprucedb["teams"]