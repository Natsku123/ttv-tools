import os
import logging
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    IPC_SECRET: str = os.environ.get("IPC_SECRET")
    IPC_PORT: int = os.environ.get("IPC_PORT", 9999)
    API_HOSTNAME: AnyHttpUrl = os.environ.get("API_HOSTNAME", "http://localhost:8000")
    SITE_HOSTNAME: AnyHttpUrl = os.environ.get("SITE_HOSTNAME", "http://localhost:3000")
    BOT_TOKEN: str = os.environ.get("BOT_TOKEN", "NO TOKEN")
    BOT_OWNER: int = os.environ.get("BOT_OWNER")
    BOT_DESCRIPTION: str = os.environ.get("BOT_DESCRIPTION", "Hellshade TTV tools discord helper")

    VERSION: str = os.environ.get("VERSION", "UNKNOWN")
    BUILD: str = os.environ.get("BUILD", "UNKNOWN")

    class Config:
        case_sensitive = True


logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)

settings = Settings()
