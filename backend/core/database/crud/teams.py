import uuid

from sqlmodel import Session, select

from core.database.crud import CRUDBase, ModelType
from core.database.models.teams import Team, TeamCreate, TeamUpdate


class CRUDTeam(CRUDBase[Team, TeamCreate, TeamUpdate]):
    def get_by_user_uuid(self, db: Session, user_uuid: uuid.UUID) -> list[ModelType]:
        return db.exec(
            select(self.model).filter(self.model.user_uuid == user_uuid)).all()


crud = CRUDTeam(Team)
