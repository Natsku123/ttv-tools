from pydantic import BaseModel


class DiscordChannel(BaseModel):
    discord_id: str
    name: str
    jump_url: str


class DiscordUser(BaseModel):
    discord_id: str
    avatar_url: str
    name: str
    mention: str
    is_admin: bool


class DiscordServer(BaseModel):
    discord_id: str
    name: str
    icon_url: str
    description: str
    channels: list[DiscordChannel]
