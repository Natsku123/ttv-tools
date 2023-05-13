import typing

from sqlmodel import Field, SQLModel, Relationship

from core.database.models import ObjectMixin
from core.database.models.memberships import Membership

if typing.TYPE_CHECKING:
    from core.database.models.users import User


class Team(SQLModel, ObjectMixin, table=True):
    name: str = Field(description="Name of team")
    description: str = Field(description="Description of team")

    members: list["User"] = Relationship(back_populates="teams", link_model=Membership)

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class TeamCreate(SQLModel):
    name: str = Field(description="Name of team")
    description: str = Field(description="Description of team")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class TeamUpdate(SQLModel):
    name: str | None = Field(None, description="Name of team")
    description: str | None = Field(None, description="Description of team")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
