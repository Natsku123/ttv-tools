import uuid
from sqlmodel import Field, SQLModel

from core.database.models import ObjectMixin


class TeamInvite(SQLModel, ObjectMixin, table=True):
    team_uuid: uuid.UUID = Field(description="UUID of team", foreign_key="team.uuid")
    user_twitch_id: str = Field(description="Twitch id of invited user")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class TeamInviteCreate(SQLModel):
    team_uuid: uuid.UUID = Field(description="UUID of team", foreign_key="team.uuid")
    user_twitch_id: str = Field(description="Twitch id of invited user")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class TeamInviteUpdate(SQLModel):
    ...

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
