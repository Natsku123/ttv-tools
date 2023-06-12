import uuid
from sqlmodel import Session, select

from core.database.crud import CRUDBase, ModelType
from core.database.models.memberships import Membership, MembershipCreate, MembershipUpdate


class CRUDMembership(CRUDBase[Membership, MembershipCreate, MembershipUpdate]):
    def get_by_user_uuid(self, db: Session, user_uuid: uuid.UUID) -> list[ModelType]:
        return db.scalars(
            select(self.model).filter(self.model.user_uuid == user_uuid)).all()

    def get_by_team_uuid(self, db: Session, team_uuid: uuid.UUID) -> list[ModelType]:
        return db.scalars(
            select(self.model).filter(self.model.team_uuid == team_uuid)).all()

    def get_by_team_user_uuid(self, db: Session, user_uuid: uuid.UUID, team_uuid: uuid.UUID) -> ModelType | None:
        return db.scalars(
            select(self.model).filter(self.model.user_uuid == user_uuid).filter(self.model.team_uuid == team_uuid)
        ).first()

    def remove_by_team_user_uuid(self, db: Session, *, user_uuid: uuid.UUID, team_uuid: uuid.UUID) -> ModelType:
        obj = self.get_by_team_user_uuid(db, user_uuid, team_uuid)
        db.delete(obj)
        db.commit()
        return obj


crud = CRUDMembership(Membership)
