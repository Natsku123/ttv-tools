import uuid
from sqlmodel import Field, SQLModel

from core.database.models import ObjectMixin


class EventSubscription(SQLModel, ObjectMixin, table=True):
    user_uuid: uuid.UUID = Field(foreign_key="user.uuid", description="UUID of user")
    server_uuid: uuid.UUID = Field(foreign_key="server.uuid", description="UUID of server")
    event: str = Field(description="Name of event object")
    custom_title: str | None = Field(None, description="Custom title for notification")
    custom_description: str | None = Field(None, description="Custom description for notification")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class EventSubscriptionCreate(EventSubscription):
    ...


class EventSubscriptionUpdate(SQLModel):
    server_uuid: uuid.UUID | None = Field(None, foreign_key="server.uuid", description="UUID of server")
    event: str | None = Field(None, description="Name of event object")
    custom_title: str | None = Field(None, description="Custom title for notification")
    custom_description: str | None = Field(None,
                                           description="Custom description for notification")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
