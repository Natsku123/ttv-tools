from bot.core import CustomBot
from bot.core.embeds import get_notification_embed
from nextcord.ext import commands, ipc


class IpcRoutes(commands.Cog):
    def __init__(self, bot):
        self.bot: CustomBot = bot

    @ipc.server.route()
    async def send_live_notification(self, data) -> None:
        embed = get_notification_embed(data.broadcaster_name, data.twitch_icon, data.twitch_url)

        embed.title = data.broadcaster_title
        embed.description = data.broadcaster_description

        await self.bot.get_channel(data.discord_channel_id).send(embed=embed)


def setup(bot):
    bot.add_cog(IpcRoutes(bot))
