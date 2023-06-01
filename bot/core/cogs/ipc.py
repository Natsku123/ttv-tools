import nextcord

from core import CustomBot
from core.embeds import get_notification_embed
from config import logger
from nextcord.ext import commands, ipc


def serialize_member(member: nextcord.Member) -> dict:
    return {
        "discord_id": member.id,
        "name": member.name,
        "mention": member.mention,
        "avatar_url": member.avatar.url if member.avatar else None,
        "is_admin": member.top_role.permissions.administrator
    }


def serialize_channel(channel: nextcord.VoiceChannel | nextcord.TextChannel) -> dict:
    return {
        "discord_id": channel.id,
        "name": channel.name,
        "jump_url": channel.jump_url
    }


def serialize_guild(guild: nextcord.Guild) -> dict:
    return {
        "discord_id": guild.id,
        "name": guild.name,
        "icon_url": guild.icon.url if guild.icon else None,
        "description": guild.description,
        "owner": serialize_member(guild.owner),
        "channels": serialize_channels(guild.text_channels)
    }


def serialize_members(members: list[nextcord.Member]) -> list[dict]:
    return [serialize_member(m) for m in members]


def serialize_channels(channels: list[nextcord.TextChannel | nextcord.VoiceChannel]) -> list[dict]:
    return [serialize_channel(c) for c in channels]


def serialize_guilds(guilds: list[nextcord.Guild]) -> list[dict]:
    return [serialize_guild(g) for g in guilds]


class IpcRoutes(commands.Cog):
    def __init__(self, bot):
        self.bot: CustomBot = bot

    @ipc.server.route()
    async def send_live_notification(self, data) -> None:
        embed = get_notification_embed(
            author_name=data.broadcaster_name,
            icon_url=data.twitch_icon,
            url=data.twitch_url,
            game=data.twitch_game,
            tags=data.twitch_tags,
            viewers=data.twitch_viewers,
            started=data.twitch_started,
            thumbnail=data.twitch_thumbnail,
            is_mature=data.twitch_is_mature
        )

        embed.title = data.broadcaster_title
        embed.description = data.broadcaster_description

        channel = self.bot.get_channel(int(data.channel_discord_id))

        if not channel:
            logger.error(f"Channel not found for {data.channel_discord_id}")
            return

        await channel.send(embed=embed)

    @ipc.server.route()
    async def get_all_servers(self, data) -> list[dict]:
        return serialize_guilds(self.bot.guilds)

    @ipc.server.route()
    async def get_user_servers(self, data) -> list[dict]:
        def is_admin(member: nextcord.Member) -> bool:
            return member.id == int(data.user_id) and member.top_role.permissions.administrator

        members = filter(is_admin, self.bot.get_all_members())
        guilds = [m.guild for m in members]

        return serialize_guilds(guilds)

    @ipc.server.route()
    async def get_member(self, data) -> dict:
        guild: nextcord.Guild = self.bot.get_guild(int(data.server_id))
        if guild:
            member: nextcord.Member = guild.get_member(int(data.user_id))

            return serialize_member(member)
        return {}

    @ipc.server.route()
    async def get_server(self, data) -> dict:
        guild = self.bot.get_guild(int(data.server_id))
        if guild:
            return serialize_guild(guild)
        return {}


def setup(bot):
    bot.add_cog(IpcRoutes(bot))
