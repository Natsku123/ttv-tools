import uuid

from sqlmodel import Session, select

from core.database.crud import CRUDBase, ModelType
from core.database.models.eventsubs import EventSubscription, EventSubscriptionCreate, EventSubscriptionUpdate


class CRUDEventSubscription(CRUDBase[EventSubscription, EventSubscriptionCreate, EventSubscriptionUpdate]):
    def get_multi_by_user_uuid(
        self,
        db: Session,
        user_uuid: uuid.UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ModelType]:

        q = select(self.model).where(EventSubscription.user_uuid == user_uuid)

        return db.exec(q.offset(skip).limit(limit)).all()

    def get_multi_by_user_uuid_and_event(
        self,
        db: Session,
        user_uuid: uuid.UUID,
        event: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ModelType]:

        q = select(self.model).where(EventSubscription.user_uuid == user_uuid).where(EventSubscription.event == event)

        return db.exec(q.offset(skip).limit(limit)).all()

    def update_twitch_id(
        self,
        db: Session,
        *,
        db_obj: EventSubscription,
        twitch_id: str
    ) -> ModelType:
        db_obj.twitch_id = twitch_id

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


crud = CRUDEventSubscription(EventSubscription)
