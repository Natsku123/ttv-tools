import datetime
import typing
import uuid

from sqlmodel import Field, SQLModel, Column, String, Relationship, BigInteger

from core.database.models import ObjectMixin
from core.database.models.memberships import Membership

if typing.TYPE_CHECKING:
    from core.database.models.teams import Team


class User(SQLModel, ObjectMixin, table=True):
    discord_id: int | None = Field(
        None,
        description="ID on discord",
        sa_column=Column(BigInteger(), unique=True, nullable=True),
    )
    twitch_id: int = Field(
        description="ID on twitch",
        sa_column=Column(BigInteger(), unique=True, nullable=False),
    )
    name: str = Field(
        sa_column=Column(String(64), nullable=False),
        description="Twitch username of player",
    )
    login_name: str | None = Field(None, description="Twitch login name")
    icon_url: str | None = Field(None, description="Twitch icon url")
    offline_image_url: str | None = Field(None, description="Twitch offline image url")
    description: str | None = Field(None, description="Twitch description")
    is_superadmin: bool | None = Field(False, description="Is user super admin")

    teams: list["Membership"] = Relationship(back_populates="user")

    def jsonable(self) -> dict:
        data: dict = self.dict()
        dts = [k for k, v in data.items() if isinstance(v, datetime.datetime)]
        ids = [k for k, v in data.items() if isinstance(v, uuid.UUID)]
        for dt in dts:
            data[dt] = data[dt].strftime("%Y-%m-%dT%H:%M:%S%z")
        for i in ids:
            data[i] = str(data[i])
        return data

    class Config:
        from_attributes = True
        populate_by_name = True


class UserCreate(SQLModel):
    discord_id: int | None = Field(None, description="ID on discord")
    twitch_id: int = Field(description="ID on twitch")
    name: str = Field(description="Twitch username of player")
    login_name: str = Field(description="Twitch login name")
    icon_url: str | None = Field(None, description="Twitch icon url")
    offline_image_url: str | None = Field(None, description="Twitch offline image url")
    description: str | None = Field(None, description="Twitch description")

    class Config:
        from_attributes = True
        populate_by_name = True


class UserUpdate(SQLModel):
    discord_id: int | None = Field(None, description="ID on discord")
    twitch_id: int | None = Field(None, description="ID on twitch")
    name: str | None = Field(None, description="Twitch username of player")
    login_name: str | None = Field(None, description="Twitch login name")
    icon_url: str | None = Field(None, description="Twitch icon url")
    offline_image_url: str | None = Field(None, description="Twitch offline image url")
    description: str | None = Field(None, description="Twitch description")
    is_superadmin: bool | None = Field(False, description="Is user super admin")

    class Config:
        from_attributes = True
        populate_by_name = True
