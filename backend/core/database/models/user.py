from sqlmodel import Field, SQLModel, Column, String

from core.database.models import ObjectMixin


class User(SQLModel, ObjectMixin, table=True):
    discord_id: str = Field(
        None,
        sa_column=Column(String(64), nullable=True, unique=True),
        alias="discordId",
        description="ID on discord",
    )
    twitch_id: str = Field(
        sa_column=Column(String(64), nullable=False, unique=True),
        alias="twitchId",
        description="ID on twitch"
    )
    name: str = Field(
        sa_column=Column(String(64), nullable=False),
        description="Twitch username of player",
    )
    login_name: str | None = Field(None, description="Twitch login name")
    icon_url: str | None = Field(None, description="Twitch icon url")
    offline_image_url: str | None = Field(None, description="Twitch offline image url")
    description: str | None = Field(None, description="Twitch description")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class UserCreate(SQLModel):
    discord_id: str | None = Field(None, alias="discordId", description="ID on discord")
    twitch_id: str = Field(alias="twitchId", description="ID on twitch")
    name: str = Field(description="Twitch username of player")
    login_name: str = Field(description="Twitch login name")
    icon_url: str | None = Field(None, description="Twitch icon url")
    offline_image_url: str | None = Field(None, description="Twitch offline image url")
    description: str | None = Field(None, description="Twitch description")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class UserUpdate(SQLModel):
    discord_id: str | None = Field(
        None, alias="discordId", description="ID on discord"
    )
    twitch_id: str | None = Field(None, alias="twitchId", description="ID on twitch")
    name: str | None = Field(None, description="Twitch username of player")
    login_name: str | None = Field(None, description="Twitch login name")
    icon_url: str | None = Field(None, description="Twitch icon url")
    offline_image_url: str | None = Field(None, description="Twitch offline image url")
    description: str | None = Field(None, description="Twitch description")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
