import typing

from sqlmodel import Field, SQLModel, Relationship

from core.database.models import ObjectMixin
from core.database.models.memberships import Membership


class Team(SQLModel, ObjectMixin, table=True):
    name: str = Field(description="Name of team")
    description: str = Field(description="Description of team")

    members: list["Membership"] = Relationship(back_populates="team")

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

class TeamShort(SQLModel, ObjectMixin):
    name: str = Field(description="Name of team")
    description: str = Field(description="Description of team")
