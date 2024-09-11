import uuid as uuid_pkg
import datetime
from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel

from core.database.utils import timezoned


class ObjectMixin(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    uuid: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4, primary_key=True, index=True, nullable=False
    )
    created_on: datetime.datetime = Field(default_factory=timezoned)
    updated_on: datetime.datetime | None = Field(nullable=True)


class LinkObjectMixin(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    created_on: datetime.datetime = Field(default_factory=timezoned)
    updated_on: datetime.datetime | None = Field(nullable=True)


class Meta(SQLModel):
    version: str | None
    build: str | None
