import datetime
from nextcord import Embed


def get_notification_embed(author_name: str, icon_url: str, url: str) -> Embed:
    embed = Embed()

    embed.set_author(
        name=author_name,
        icon_url=icon_url,
        url=url
    )

    embed.timestamp = datetime.datetime.utcnow()

    return embed

