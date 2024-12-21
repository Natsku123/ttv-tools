from sqlmodel import SQLModel, Field

from core.database.models import ObjectMixin


class TeamShort(SQLModel, ObjectMixin):
    name: str = Field(description="Name of team")
    description: str = Field(description="Description of team")

    class Config:
        from_attributes = True
        populate_by_name = True


class UserShort(SQLModel, ObjectMixin):
    discord_id: str = Field(
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

    class Config:
        from_attributes = True
        populate_by_name = True
