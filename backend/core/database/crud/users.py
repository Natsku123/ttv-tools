from typing import Optional
from sqlmodel import Session, select

from core.database.crud import CRUDBase, ModelType
from core.database.models.users import User, UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_twitch_id(self, db: Session, twitch_id: str) -> Optional[ModelType]:
        return db.exec(select(self.model).filter(self.model.twitch_id == twitch_id)).first()

    def get_by_discord_id(self, db: Session, discord_id: str) -> Optional[ModelType]:
        return db.exec(select(self.model).filter(self.model.discord_id == discord_id)).first()


crud = CRUDUser(User)
