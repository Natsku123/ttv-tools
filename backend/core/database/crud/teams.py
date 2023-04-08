from core.database.crud import CRUDBase
from core.database.models.teams import Team, TeamCreate, TeamUpdate


class CRUDTeam(CRUDBase[Team, TeamCreate, TeamUpdate]):
    ...


crud = CRUDTeam(Team)
