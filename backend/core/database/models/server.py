from sqlmodel import Field, SQLModel, Column, String

from core.database.models import ObjectMixin


class Server(SQLModel, ObjectMixin, table=True):
    discord_id: str = Field(
        sa_column=Column(String(64), nullable=False, unique=True),
        alias="discordId",
        description="ID on discord",
    )
    discord_channel_id: str = Field(
        None,
        sa_column=Column(String(64), nullable=True, unique=False),
        alias="discordChannelId",
        description="ID of subscription channel on discord"
    )

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class ServerCreate(SQLModel):
    discord_id: str = Field(alias="discordId", description="ID on discord")
    discord_channel_id: str | None = Field(None, alias="discordChannelId", description="ID of subscription channel on discord")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class ServerUpdate(SQLModel):
    discord_id: str | None = Field(None, alias="discordId", description="ID on discord")
    discord_channel_id: str | None = Field(None, alias="discordChannelId",
                                           description="ID of subscription channel on discord")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
