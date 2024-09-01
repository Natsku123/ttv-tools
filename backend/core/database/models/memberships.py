import uuid
import typing
from sqlmodel import Field, SQLModel, Relationship

from core.database.models import LinkObjectMixin

if typing.TYPE_CHECKING:
    from core.database.models.teams import Team
    from core.database.models.users import User


class Membership(SQLModel, LinkObjectMixin, table=True):
    team_uuid: uuid.UUID = Field(description="UUID of team", foreign_key="team.uuid",
                                 primary_key=True)
    user_uuid: uuid.UUID = Field(description="UUID of user", foreign_key="user.uuid",
                                 primary_key=True)
    is_admin: bool = Field(description="Is admin of the team", default=False)
    allowed_invites: bool = Field(description="Is allowed to send invites", default=False)

    team: "Team" = Relationship(back_populates="members")
    user: "User" = Relationship(back_populates="teams")

    class Config:
        from_attributes = True
        populate_by_name = True


class MembershipCreate(SQLModel):
    team_uuid: uuid.UUID = Field(description="UUID of team", foreign_key="team.uuid",
                                 primary_key=True)
    user_uuid: uuid.UUID = Field(description="UUID of user", foreign_key="user.uuid",
                                 primary_key=True)
    is_admin: bool | None = Field(False, description="Is admin of the team")
    allowed_invites: bool | None = Field(False, description="Is allowed to send invites")

    class Config:
        from_attributes = True
        populate_by_name = True


class MembershipUpdate(SQLModel):
    is_admin: bool | None = Field(None, description="Is admin of the team")
    allowed_invites: bool | None = Field(None,
                                         description="Is allowed to send invites")

    class Config:
        from_attributes = True
        populate_by_name = True
