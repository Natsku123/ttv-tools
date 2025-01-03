import uuid

from sqlmodel import Field, SQLModel, Column, String

from core.database.models import ObjectMixin


class EventSubscription(SQLModel, ObjectMixin, table=True):
    user_uuid: uuid.UUID = Field(foreign_key="user.uuid", description="UUID of user", ondelete="CASCADE")
    server_discord_id: str = Field(
        description="Discord ID of Server", sa_column=Column(String(), nullable=False)
    )
    channel_discord_id: str = Field(
        description="Discord ID of Channel", sa_column=Column(String(), nullable=False)
    )
    event: str = Field(description="Name of event object")
    twitch_id: str | None = Field(None, description="Twitch ID of Event Subscription")
    custom_title: str | None = Field(None, description="Custom title for notification")
    custom_description: str | None = Field(
        None, description="Custom description for notification"
    )
    message: str | None = Field(None, description="Message of notification")

    class Config:
        from_attributes = True
        populate_by_name = True


class EventSubscriptionCreate(SQLModel):
    user_uuid: uuid.UUID = Field(foreign_key="user.uuid", description="UUID of user")
    server_discord_id: str = Field(description="Discord ID of Server")
    channel_discord_id: str = Field(description="Discord ID of Channel")
    event: str = Field(description="Name of event object")
    twitch_id: str | None = Field(None, description="Twitch ID of Event Subscription")
    custom_title: str | None = Field(None, description="Custom title for notification")
    custom_description: str | None = Field(
        None, description="Custom description for notification"
    )
    message: str | None = Field(None, description="Message of notification")


class EventSubscriptionUpdate(SQLModel):
    server_discord_id: str | None = Field(None, description="Discord ID of Server")
    channel_discord_id: str | None = Field(None, description="Discord ID of Channel")
    event: str | None = Field(None, description="Name of event object")
    custom_title: str | None = Field(None, description="Custom title for notification")
    custom_description: str | None = Field(
        None, description="Custom description for notification"
    )
    twitch_id: str | None = Field(None, description="Twitch ID of Event Subscription")
    message: str | None = Field(None, description="Message of notification")

    class Config:
        from_attributes = True
        populate_by_name = True
