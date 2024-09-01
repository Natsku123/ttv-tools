import os
import pytz
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator


def get_twitch_api_url():
    mock_enabled = os.environ.get("TWITCH_MOCK_ENABLED", "false")
    if mock_enabled.lower() == "true":
        return "http://localhost:8080/mock"
    else:
        return "https://api.twitch.tv/helix"


def get_twitch_id_url():
    mock_enabled = os.environ.get("TWITCH_MOCK_ENABLED", "false")
    if mock_enabled.lower() == "true":
        return "http://localhost:8080/auth"
    else:
        return "https://id.twitch.tv/oauth2"


class Settings(BaseSettings):
    SECRET_KEY: str = os.environ.get("SECRET_KEY")
    TWITCH_WEBHOOK_SECRET: str = os.environ.get("TWITCH_WEBHOOK_SECRET")
    IPC_SECRET: str = os.environ.get("IPC_SECRET")
    IPC_PORT: int = os.environ.get("IPC_PORT", 9999)
    IPC_HOST: str = os.environ.get("IPC_HOST", "bot")
    API_HOSTNAME: AnyHttpUrl = os.environ.get("API_HOSTNAME", "http://localhost:8000")
    REDIRECT_URL: AnyHttpUrl = os.environ.get("REDIRECT_URL", API_HOSTNAME)
    SITE_HOSTNAME: AnyHttpUrl = os.environ.get("SITE_HOSTNAME", "http://localhost:3000")
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = [str(API_HOSTNAME), str(SITE_HOSTNAME)]
    DISCORD_CLIENT_ID: str = os.environ.get("DISCORD_CLIENT_ID")
    DISCORD_CLIENT_SECRET: str = os.environ.get("DISCORD_CLIENT_SECRET")
    TWITCH_CLIENT_ID: str = os.environ.get("TWITCH_CLIENT_ID")
    TWITCH_CLIENT_SECRET: str = os.environ.get("TWITCH_CLIENT_SECRET")
    BOT_TOKEN: str = os.environ.get("BOT_TOKEN", "NO TOKEN")
    ROOT_PATH: str = os.environ.get("ROOT_PATH", "")

    OWNER_TWITCH_ID: str = os.environ.get("OWNER_TWITCH_ID", "")

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    DATABASE_SERVER: str = "db"
    DATABASE_USER: str = os.environ.get("DB_USER")
    DATABASE_PASSWORD: str = os.environ.get("DB_PASS")
    DATABASE_NAME: str = os.environ.get("DB_NAME")

    ORIGINS: list[AnyHttpUrl] = [
        os.environ.get("API_HOSTNAME", "http://localhost:8800"),
        os.environ.get("SITE_HOSTNAME", "http://localhost:3001"),
    ]

    VERSION: str = os.environ.get("VERSION", "UNKNOWN")
    BUILD: str = os.environ.get("BUILD", "UNKNOWN")

    TIME_ZONE: str = os.environ.get("TIMEZONE", os.environ.get("TZ", "UTC"))

    TWITCH_ID_URL: AnyHttpUrl = get_twitch_id_url()
    TWITCH_API_URL: AnyHttpUrl = get_twitch_api_url()

    class Config:
        case_sensitive = True


settings = Settings()
