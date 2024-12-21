import datetime

import nextcord
from nextcord import Embed


def get_notification_embed(
    *,
    author_name: str,
    icon_url: str,
    url: str,
    game: str | None = None,
    tags: list[str] | None = None,
    viewers: int | None,
    started: str | None,
    thumbnail: str | None,
    is_mature: bool | None,
) -> Embed:
    embed = Embed(colour=nextcord.Color.from_rgb(145, 70, 255))

    embed.set_author(name=author_name, icon_url=icon_url, url=url)

    embed.url = url

    if game:
        embed.add_field(name="Game", value=game)

    if viewers:
        embed.add_field(name="Viewers", value=viewers)

    if started:
        embed.add_field(
            name="Started",
            value=f"<t:{int(datetime.datetime.fromisoformat(started[:-1] + '+00:00').timestamp())}:f>",
        )

    if thumbnail:
        embed.set_image(thumbnail)

    if is_mature is not None:
        embed.add_field(name="Mature?", value="Yes" if is_mature else "No")

    if tags and len(tags) > 0:
        embed.add_field(name="Tags", value=", ".join(tags))

    embed.timestamp = datetime.datetime.now(datetime.UTC)

    return embed


def get_base_embed(
    *,
    author_name: str,
    icon_url: str,
    url: str,
) -> Embed:
    embed = Embed(colour=nextcord.Color.from_rgb(145, 70, 255))

    embed.set_author(name=author_name, icon_url=icon_url, url=url)

    embed.timestamp = datetime.datetime.now(datetime.UTC)

    return embed
