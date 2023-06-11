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
        obj_in = EventSubscriptionUpdate(**{
            "twitch_id": twitch_id,
            "server_discord_id": db_obj.server_discord_id,
            "channel_discord_id": db_obj.channel_discord_id,
            "event": db_obj.event,
            "custom_title": db_obj.custom_title,
            "custom_description": db_obj.custom_description
        })
        return self.update(db, db_obj=db_obj, obj_in=obj_in)


crud = CRUDEventSubscription(EventSubscription)
