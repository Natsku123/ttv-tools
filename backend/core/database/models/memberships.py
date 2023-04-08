import uuid
from sqlmodel import Field, SQLModel

from core.database.models import LinkObjectMixin


class Membership(SQLModel, LinkObjectMixin, table=True):
    team_uuid: uuid.UUID = Field(description="UUID of team", foreign_key="team.uuid",
                                 primary_key=True)
    user_uuid: uuid.UUID = Field(description="UUID of user", foreign_key="user.uuid",
                                 primary_key=True)
    is_admin: bool = Field(description="Is admin of the team", default=False)
    allowed_invites: bool = Field(description="Is allowed to send invites", default=False)

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class MembershipCreate(SQLModel):
    team_uuid: uuid.UUID = Field(description="UUID of team", foreign_key="team.uuid",
                                 primary_key=True)
    user_uuid: uuid.UUID = Field(description="UUID of user", foreign_key="user.uuid",
                                 primary_key=True)
    is_admin: bool | None = Field(False, description="Is admin of the team")
    allowed_invites: bool | None = Field(False, description="Is allowed to send invites")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class MembershipUpdate(SQLModel):
    is_admin: bool | None = Field(None, description="Is admin of the team")
    allowed_invites: bool | None = Field(None,
                                         description="Is allowed to send invites")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
