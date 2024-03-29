import signal
import nextcord
from nextcord.ext import commands

from config import settings, logger
from core import get_bot


def main():

    logger.info("Starting bot...")

    intents = nextcord.Intents(
        members=True,
        guilds=True,
        reactions=True
    )
    bot = get_bot(intents=intents)

    def handle_sigterm(sig, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, handle_sigterm)

    bot.ipc.start()
    bot.run(settings.BOT_TOKEN)


if __name__ == "__main__":
    main()
