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

class ModelNames:
    SCRIM = "scrim"
    TESTER = "tester"
    TOURNEY = "tourney"
    AUTOROLE = "autorole"
    TEAM = "team"
    ROUND = "round"


def init(db:"Database"):
    GuildAutoRoleModel.col = db.autoroles
    ScrimModel.col = db.scrims
    TesterModel._col = db.testers
    TourneyModel._col = db.tournaments
    TeamModel._col = db.teams