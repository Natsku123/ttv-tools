import uuid
from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship, Column, Integer, String

from core.database.utils import INTEGER_SIZE
from core.database.models import ObjectMixin

if TYPE_CHECKING:
    from .all import User


class OAuth2Token(SQLModel, ObjectMixin, table=True):
    user_id: uuid.UUID = Field(
        foreign_key="user.uuid",
        description="ID of user",
    )
    name: str = Field(
        description="Name of token OAuth provider",
    )

    user: "User" = Relationship()

    token_type: str | None = Field(
        description="Type of token"
    )
    access_token: str = Field(
        description="Access token from OAuth provider",
    )
    refresh_token: str | None = Field(
        description="Refresh token from OAuth provider",
    )
    expires_at: int | None = Field(
        sa_column=Column(Integer, default=0),
        ge=0,
        le=INTEGER_SIZE,
        description="Token expiration",
    )

    def to_token(self):
        return dict(
            access_token=self.access_token,
            token_type=self.token_type,
            refresh_token=self.refresh_token,
            expires_at=self.expires_at,
        )

    class Config:
        from_attributes = True
        populate_by_name = True


class OAuth2TokenCreate(SQLModel):
    user_id: uuid.UUID = Field(
        description="ID of user",
    )
    name: str = Field(description="Name of token OAuth provider")
    token_type: str | None = Field(
        None, description="Type of token"
    )
    access_token: str = Field(
        description="Access token from OAuth provider"
    )
    refresh_token: str | None = Field(
        None, description="Refresh token from OAuth provider"
    )
    expires_at: int | None = Field(
        0, ge=0, le=INTEGER_SIZE, description="Token expiration"
    )

    class Config:
        from_attributes = True
        populate_by_name = True


class OAuth2TokenUpdate(SQLModel):
    user_id: uuid.UUID | None = Field(
        None,
        description="ID of user",
    )
    name: str | None = Field(None, description="Name of token OAuth provider")
    token_type: str | None = Field(
        None, description="Type of token"
    )
    access_token: str | None = Field(
        None, description="Access token from OAuth provider"
    )
    refresh_token: str | None = Field(
        None, description="Refresh token from OAuth provider"
    )
    expires_at: int | None = Field(
        None, ge=0, le=INTEGER_SIZE, description="Token expiration"
    )

    class Config:
        from_attributes = True
        populate_by_name = True

