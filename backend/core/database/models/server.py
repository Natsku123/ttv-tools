from sqlmodel import Field, SQLModel, Column, String, BigInteger

from core.database.models import ObjectMixin


class Server(SQLModel, ObjectMixin, table=True):
    discord_id: str = Field(
        description="ID on discord",
        sa_column=Column(String(), unique=True, nullable=False),
    )
    discord_channel_id: str | None = Field(
        None,
        description="ID of subscription channel on discord",
        sa_column=Column(String(), unique=False, nullable=True),
    )

    class Config:
        from_attributes = True
        populate_by_name = True


class ServerCreate(SQLModel):
    discord_id: str = Field(description="ID on discord")
    discord_channel_id: str | None = Field(
        None, description="ID of subscription channel on discord"
    )

    class Config:
        from_attributes = True
        populate_by_name = True


class ServerUpdate(SQLModel):
    discord_id: str | None = Field(None, description="ID on discord")
    discord_channel_id: str | None = Field(
        None, description="ID of subscription channel on discord"
    )

    class Config:
        from_attributes = True
        populate_by_name = True
