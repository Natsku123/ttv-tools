import uuid

from sqlmodel import Session, select

from core.database.crud import CRUDBase, ModelType
from core.database.models.invites import TeamInvite, TeamInviteCreate, TeamInviteUpdate


class CRUDTeamInvite(CRUDBase[TeamInvite, TeamInviteCreate, TeamInviteUpdate]):
    def get_by_twitch_id(self, db: Session, twitch_id: str) -> ModelType | TeamInvite:
        return db.scalars(select(self.model).filter(self.model.user_twitch_id == twitch_id)).first()

    def get_by_team_uuid(self, db: Session, team_uuid: uuid.UUID) -> list[ModelType]:
        return db.scalars(select(self.model).filter(self.model.team_uuid == team_uuid)).all()


crud = CRUDTeamInvite(TeamInvite)
