import uuid as uuid_pkg
import datetime
from pydantic import BaseModel
from sqlmodel import Field, SQLModel

from core.database.utils import timezoned


class ObjectMixin(BaseModel):
    uuid: uuid_pkg.UUID = Field(default_factory=uuid_pkg.uuid4, primary_key=True, index=True, nullable=False)
    created_on: datetime.datetime = Field(default_factory=timezoned)
    updated_on: datetime.datetime | None = Field(nullable=True)


class LinkObjectMixin(BaseModel):
    created_on: datetime.datetime = Field(default_factory=timezoned)
    updated_on: datetime.datetime | None = Field(nullable=True)


class Meta(SQLModel):
    version: str | None
    build: str | None
