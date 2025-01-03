import nextcord
import datetime

from core import CustomBot
from core.embeds import get_notification_embed, get_base_embed
from config import logger
from nextcord.ext import commands, ipc


def serialize_member(member: nextcord.Member) -> dict:
    return {
        "discord_id": str(member.id),
        "name": member.name,
        "mention": member.mention,
        "avatar_url": member.avatar.url if member.avatar else None,
        "is_admin": member.top_role.permissions.administrator,
    }


def serialize_channel(channel: nextcord.VoiceChannel | nextcord.TextChannel) -> dict:
    return {
        "discord_id": str(channel.id),
        "name": channel.name,
        "jump_url": channel.jump_url,
    }


def serialize_guild(guild: nextcord.Guild) -> dict:
    return {
        "discord_id": str(guild.id),
        "name": guild.name,
        "icon_url": guild.icon.url if guild.icon else None,
        "description": guild.description,
        "owner": serialize_member(guild.owner),
        "channels": serialize_channels(guild.text_channels),
        "roles": serialize_roles(guild.roles),
    }


def serialize_role(role: nextcord.Role) -> dict:
    return {
        "discord_id": str(role.id),
        "name": role.name,
        "color": role.color.to_rgb(),
        "mention": role.mention,
    }


def serialize_members(members: list[nextcord.Member]) -> list[dict]:
    return [serialize_member(m) for m in members]


def serialize_channels(
    channels: list[nextcord.TextChannel | nextcord.VoiceChannel],
) -> list[dict]:
    return [serialize_channel(c) for c in channels]


def serialize_guilds(guilds: list[nextcord.Guild]) -> list[dict]:
    return [serialize_guild(g) for g in guilds]


def serialize_roles(roles: list[nextcord.Role]) -> list[dict]:
    return [serialize_role(r) for r in roles]


class IpcRoutes(commands.Cog):
    def __init__(self, bot):
        self.bot: CustomBot = bot

    @ipc.server.route()
    async def send_live_notification(self, data) -> dict:
        embed = get_notification_embed(
            author_name=data.broadcaster_name,
            icon_url=data.twitch_icon,
            url=data.twitch_url,
            game=data.twitch_game,
            tags=data.twitch_tags,
            viewers=data.twitch_viewers,
            started=data.twitch_started,
            thumbnail=data.twitch_thumbnail,
            is_mature=data.twitch_is_mature,
        )

        embed.title = data.broadcaster_title
        embed.description = data.broadcaster_description

        channel = self.bot.get_channel(int(data.channel_discord_id))

        if not channel:
            logger.error(f"Channel not found for {data.channel_discord_id}")
            return {}

        await channel.send(embed=embed, content=data.notification_content)

    @ipc.server.route()
    async def send_new_subscription_notification(self, data) -> dict:
        embed = get_base_embed(
            author_name=data.broadcaster_name,
            icon_url=data.twitch_icon,
            url=data.twitch_url,
        )

        if data.twitch_is_gift:
            embed.title = f"{data.twitch_user_name} received a gift subscription!"
        else:
            embed.title = f"{data.twitch_user_name} just subscribed!"

        embed.add_field(name="Tier", value=data.twitch_tier)

        channel = self.bot.get_channel(int(data.channel_discord_id))

        if not channel:
            logger.error(f"Channel not found for {data.channel_discord_id}")
            return {}

        await channel.send(embed=embed, content=data.notification_content)

    @ipc.server.route()
    async def send_resubscription_notification(self, data) -> dict:
        embed = get_base_embed(
            author_name=data.broadcaster_name,
            icon_url=data.twitch_icon,
            url=data.twitch_url,
        )

        if data.twitch_is_gift:
            embed.title = f"{data.twitch_user_name} received a gift subscription!"
        else:
            embed.title = f"{data.twitch_user_name} just resubscribed!"

        embed.description = data.twitch_message_text

        embed.add_field(name="Tier", value=data.twitch_tier)
        embed.add_field(name="Total months", value=data.twitch_cumulative_months)
        if data.twitch_cumulative_months:
            embed.add_field(name="Streak months", value=data.twitch_streak_months)
        embed.add_field(name="Duration (months)", value=data.twitch_duration_months)

        channel = self.bot.get_channel(int(data.channel_discord_id))

        if not channel:
            logger.error(f"Channel not found for {data.channel_discord_id}")
            return {}

        await channel.send(embed=embed, content=data.notification_content)

    @ipc.server.route()
    async def send_gift_subscription_notification(self, data) -> dict:
        embed = get_base_embed(
            author_name=data.broadcaster_name,
            icon_url=data.twitch_icon,
            url=data.twitch_url,
        )

        username = (
            data.twitch_user_name if not data.twitch_is_anonymous else "Anonymous"
        )

        if data.twitch_total > 1:
            embed.title = f"{username} just gifted {data.twitch_total} subscriptions!"
        else:
            embed.title = f"{username} just gifted a subscription!"

        embed.add_field(name="Tier", value=data.twitch_tier)
        if not data.twitch_cumulative_months:
            embed.add_field(name="Total gifts", value=data.twitch_cumulative_total)

        channel = self.bot.get_channel(int(data.channel_discord_id))

        if not channel:
            logger.error(f"Channel not found for {data.channel_discord_id}")
            return {}

        await channel.send(embed=embed, content=data.notification_content)

    @ipc.server.route()
    async def send_cheer_notification(self, data) -> dict:
        embed = get_base_embed(
            author_name=data.broadcaster_name,
            icon_url=data.twitch_icon,
            url=data.twitch_url,
        )

        username = (
            data.twitch_user_name if not data.twitch_is_anonymous else "Anonymous"
        )

        embed.title = f"{username} just cheered {data.bits} bits!"
        embed.description = data.twitch_message

        channel = self.bot.get_channel(int(data.channel_discord_id))

        if not channel:
            logger.error(f"Channel not found for {data.channel_discord_id}")
            return {}

        await channel.send(embed=embed, content=data.notification_content)

    @ipc.server.route()
    async def send_raid_notification(self, data) -> dict:
        embed = get_base_embed(
            author_name=data.broadcaster_name,
            icon_url=data.twitch_icon,
            url=data.twitch_url,
        )

        embed.title = (
            f"{data.twitch_user_name} just raided with {data.twitch_viewers} viewers!"
        )

        channel = self.bot.get_channel(int(data.channel_discord_id))

        if not channel:
            logger.error(f"Channel not found for {data.channel_discord_id}")
            return {}

        await channel.send(embed=embed, content=data.notification_content)

    @ipc.server.route()
    async def send_hype_train_end_notification(self, data) -> dict:
        embed = get_base_embed(
            author_name=data.broadcaster_name,
            icon_url=data.twitch_icon,
            url=data.twitch_url,
        )

        embed.title = "Hype train just ended!"

        embed.add_field(name="Level", value=data.twitch_level)
        embed.add_field(name="Contributions", value=data.twitch_total)
        # embed.add_field(name="Total gifts", value=data.twitch_top_contributions)
        embed.add_field(name="Started", value=f"<t:{int(datetime.datetime.fromisoformat(data.twitch_started_at[:-1] + '+00:00').timestamp())}:f>")
        embed.add_field(name="Ended", value=f"<t:{int(datetime.datetime.fromisoformat(data.twitch_ended_at[:-1] + '+00:00').timestamp())}:f>")
        embed.add_field(name="Cooldown until", value=f"<t:{int(datetime.datetime.fromisoformat(data.twitch_cooldown_ends_at[:-1] + '+00:00').timestamp())}:R>")
        embed.add_field(name="Golden Kappa", value="Yes" if data.twitch_golden_kappa else "No")

        channel = self.bot.get_channel(int(data.channel_discord_id))

        if not channel:
            logger.error(f"Channel not found for {data.channel_discord_id}")
            return {}

        await channel.send(embed=embed, content=data.notification_content)

    @ipc.server.route()
    async def get_all_servers(self, data) -> list[dict]:
        return serialize_guilds(self.bot.guilds)

    @ipc.server.route()
    async def get_user_servers(self, data) -> list[dict]:
        def is_admin(member: nextcord.Member) -> bool:
            return (
                member.id == int(data.user_id)
                and member.top_role.permissions.administrator
            )

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
