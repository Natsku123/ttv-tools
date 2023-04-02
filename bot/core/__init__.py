import nextcord
from nextcord.ext import commands, ipc

from config import settings, logger


class CustomBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ipc = ipc.Server(self, host="0.0.0.0", port=settings.IPC_PORT, secret_key=settings.IPC_SECRET)

        self.load_extension("ipc", package=".core.cogs")

    async def on_ready(self):
        logger.info(f"\nLogged in as:\n{self.user} (ID: {self.user.id})")

    async def on_ipc_ready(self):
        logger.info("IPC ready")

    async def on_ipc_error(self, endpoint, error):
        logger.info(f"{endpoint} raised {error}")


def get_bot(intents=nextcord.Intents.default()) -> CustomBot:
    return CustomBot(
        command_prefix=commands.when_mentioned_or("!"),
        description=settings.BOT_DESCRIPTION,
        owner_id=settings.BOT_OWNER,
        intents=intents,
    )
