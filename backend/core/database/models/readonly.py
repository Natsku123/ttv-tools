import uuid
from datetime import datetime

from sqlmodel import SQLModel, Field

from core.database import Team, User
from core.database.models import LinkObjectMixin, ObjectMixin


class MembershipRead(SQLModel, LinkObjectMixin):
    team_uuid: uuid.UUID = Field(
        description="UUID of team", foreign_key="team.uuid", primary_key=True
    )
    user_uuid: uuid.UUID = Field(
        description="UUID of user", foreign_key="user.uuid", primary_key=True
    )
    is_admin: bool = Field(description="Is admin of the team", default=False)
    allowed_invites: bool = Field(
        description="Is allowed to send invites", default=False
    )

    team: Team
    user: User

    class Config:
        from_attributes = True
        populate_by_name = True


class UserRead(SQLModel, ObjectMixin):
    discord_id: str | None = Field(
        None,
        description="ID on discord",
    )
    twitch_id: str = Field(
        description="ID on twitch",
    )
    name: str = Field(
        description="Twitch username of player",
    )
    login_name: str | None = Field(None, description="Twitch login name")
    icon_url: str | None = Field(None, description="Twitch icon url")
    offline_image_url: str | None = Field(None, description="Twitch offline image url")
    description: str | None = Field(None, description="Twitch description")
    is_superadmin: bool | None = Field(False, description="Is user super admin")

    teams: list[MembershipRead] = []

    def jsonable(self) -> dict:
        data: dict = self.dict()
        dts = [k for k, v in data.items() if isinstance(v, datetime)]
        ids = [k for k, v in data.items() if isinstance(v, uuid.UUID)]
        for dt in dts:
            data[dt] = data[dt].strftime("%Y-%m-%dT%H:%M:%S%z")
        for i in ids:
            data[i] = str(data[i])
        return data

    class Config:
        from_attributes = True
        populate_by_name = True


class TeamRead(SQLModel, ObjectMixin):
    name: str = Field(description="Name of team")
    description: str = Field(description="Description of team")

    members: list[MembershipRead] = []

    class Config:
        from_attributes = True
        populate_by_name = True
