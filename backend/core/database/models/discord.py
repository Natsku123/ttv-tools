from pydantic import BaseModel


class DiscordRole(BaseModel):
    discord_id: str
    name: str
    color: tuple[int, int, int]
    mention: str


class DiscordChannel(BaseModel):
    discord_id: str
    name: str
    jump_url: str


class DiscordUser(BaseModel):
    discord_id: str
    avatar_url: str | None
    name: str
    mention: str
    is_admin: bool


class DiscordServer(BaseModel):
    discord_id: str
    name: str
    icon_url: str | None
    description: str | None
    owner: DiscordUser
    channels: list[DiscordChannel]
    roles: list[DiscordRole]
