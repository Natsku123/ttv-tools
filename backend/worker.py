import json
import os
import asyncio
import uuid
import redis

import requests
from celery import Celery, Task
from celery.schedules import crontab

from sqlmodel import Session, select
from sqlalchemy.orm import scoped_session

from celery.utils.log import get_task_logger

from config import settings
from core.database.models.twitch import *
from core.database.models.users import UserUpdate
from core.database.models.eventsubs import EventSubscription
from core.database.crud.eventsubs import crud as eventsub_crud
from core.database.crud.users import crud as user_crud
from core.database.crud.server import crud as server_crud
from core.database import engine, SessionLocal
from core.twitch_tools import get_twitch_access_token

from core.ipc.client import Client

app = Celery(__name__)
app.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379")
app.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379")

TWITCH_MESSAGE_ID_SET_KEY = "twitchmessageids"

db_session = scoped_session(SessionLocal)
logger = get_task_logger(__name__)


class SqlAlchemyTask(Task):
    """An abstract Celery Task that ensures that the connection the
    database is closed on task completion"""

    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        db_session.remove()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Update all users twice a day
    sender.add_periodic_task(
        crontab(hour="6,18", minute="0"),
        update_users.s(update_all=True),
    )


@app.task(base=SqlAlchemyTask)
def update_users(
    update_all: bool = False,
    token: str = None,
    user_uuids: list[uuid.UUID] = None,
    twitch_ids: list[str] = None,
    discord_ids: list[str] = None,
):
    if not user_uuids:
        user_uuids = []
    if not twitch_ids:
        twitch_ids = []
    if not discord_ids:
        discord_ids = []

    if not token:
        token = get_twitch_access_token()

    twitch_headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": settings.TWITCH_CLIENT_ID,
    }

    if not update_all:
        users_by_uuid = [user_crud.get(db_session, x) for x in user_uuids]
        users_by_twitch = [
            user_crud.get_by_twitch_id(db_session, x) for x in twitch_ids
        ]
        users_by_discord = [
            user_crud.get_by_discord_id(db_session, x) for x in discord_ids
        ]

        users = users_by_uuid + users_by_twitch + users_by_discord
    else:
        users = user_crud.get_multi(db_session)

    if len(users) > 0:
        users_twitch_ids = list(set([x.twitch_id for x in users if x]))

        user_data = requests.get(
            f"{settings.TWITCH_API_URL}/users",
            headers=twitch_headers,
            params={"id": users_twitch_ids},
        ).json()

        if "data" not in user_data:
            return user_data

        for ud in user_data["data"]:
            user = user_crud.get_by_twitch_id(db_session, ud["id"])

            if user:
                user_update = UserUpdate(
                    **{
                        "name": ud["display_name"],
                        "login_name": ud["login"],
                        "icon_url": ud["profile_image_url"],
                        "offline_image_url": ud["offline_image_url"],
                        "description": ud["description"],
                    }
                )

                user_crud.update(db_session, db_obj=user, obj_in=user_update)


def get_event_condition(session: Session, e: EventSubscription) -> dict:
    user = user_crud.get(session, e.user_uuid)

    match e.event:
        case "channel.update":
            return {"broadcaster_user_id": str(user.twitch_id)}
        case "channel.follow":
            return {
                "broadcaster_user_id": str(user.twitch_id),
                "moderator_user_id": str(user.twitch_id),
            }
        case "channel.subscribe":
            return {"broadcaster_user_id": str(user.twitch_id)}
        case "channel.subscription.end":
            return {"broadcaster_user_id": str(user.twitch_id)}
        case "channel.subscription.gift":
            return {"broadcaster_user_id": str(user.twitch_id)}
        case "channel.subscription.message":
            return {"broadcaster_user_id": str(user.twitch_id)}
        case "channel.cheer":
            return {"broadcaster_user_id": str(user.twitch_id)}
        case "channel.raid":
            # TODO add from_broadcaster_user_id also?
            return {"to_broadcaster_user_id": str(user.twitch_id)}
        case "channel.ban":
            return {"broadcaster_user_id": str(user.twitch_id)}
        case "channel.unban":
            return {"broadcaster_user_id": str(user.twitch_id)}
        case "channel.moderator.add":
            return {"broadcaster_user_id": str(user.twitch_id)}
        case "channel.moderator.remove":
            return {"broadcaster_user_id": str(user.twitch_id)}
        case "channel.channel_points_custom_reward.add":
            return {"broadcaster_user_id": str(user.twitch_id)}
        case "channel.channel_points_custom_reward.update":
            return {"broadcaster_user_id": str(user.twitch_id)}
        case "channel.channel_points_custom_reward.remove":
            return {"broadcaster_user_id": str(user.twitch_id)}
        case "channel.channel_points_custom_reward_redemption.add":
            # TODO reward id check!
            return {"broadcaster_user_id": str(user.twitch_id)}
        case "channel.channel_points_custom_reward_redemption.update":
            # TODO reward id check!
            return {"broadcaster_user_id": str(user.twitch_id)}
        case "channel.poll.begin":
            return {"broadcaster_user_id": str(user.twitch_id)}
        case "channel.poll.progress":
            return {"broadcaster_user_id": str(user.twitch_id)}
        case "channel.poll.end":
            return {"broadcaster_user_id": str(user.twitch_id)}
        case "channel.prediction.begin":
            return {"broadcaster_user_id": str(user.twitch_id)}
        case "channel.prediction.progress":
            return {"broadcaster_user_id": str(user.twitch_id)}
        case "channel.prediction.lock":
            return {"broadcaster_user_id": str(user.twitch_id)}
        case "channel.prediction.end":
            return {"broadcaster_user_id": str(user.twitch_id)}
        case "channel.charity_campaign.donate":
            # TODO
            return {}
        case "channel.charity_campaign.start":
            # TODO
            return {}
        case "channel.charity_campaign.progress":
            # TODO
            return {}
        case "channel.charity_campaign.stop":
            # TODO
            return {}
        case "drop.entitlement.grant":
            # TODO
            return {}
        case "extension.bits_transaction.create":
            # TODO
            return {}
        case "channel.goal.begin":
            return {"broadcaster_user_id": str(user.twitch_id)}
        case "channel.goal.progress":
            return {"broadcaster_user_id": str(user.twitch_id)}
        case "channel.goal.end":
            return {"broadcaster_user_id": str(user.twitch_id)}
        case "channel.hype_train.begin":
            return {"broadcaster_user_id": str(user.twitch_id)}
        case "channel.hype_train.progress":
            return {"broadcaster_user_id": str(user.twitch_id)}
        case "channel.hype_train.end":
            return {"broadcaster_user_id": str(user.twitch_id)}
        case "channel.shield_mode.begin":
            # TODO
            return {}
        case "channel.shield_mode.end":
            # TODO
            return {}
        case "channel.shoutout.create":
            # TODO
            return {}
        case "channel.shoutout.receive":
            # TODO
            return {}
        case "stream.online":
            return {"broadcaster_user_id": str(user.twitch_id)}
        case "stream.offline":
            return {"broadcaster_user_id": str(user.twitch_id)}
        case "user.authorization.grant":
            return {"client_id": settings.TWITCH_CLIENT_ID}
        case "user.authorization.revoke":
            return {"client_id": settings.TWITCH_CLIENT_ID}
        case "user.update":
            return {"user_id": str(user.twitch_id)}


def get_event_version(e: EventSubscription) -> int:
    match e.event:
        case "channel.update":
            return 1
        case "channel.follow":
            return 2
        case "channel.subscribe":
            return 1
        case "channel.subscription.end":
            return 1
        case "channel.subscription.gift":
            return 1
        case "channel.subscription.message":
            return 1
        case "channel.cheer":
            return 1
        case "channel.raid":
            return 1
        case "channel.ban":
            return 1
        case "channel.unban":
            return 1
        case "channel.moderator.add":
            return 1
        case "channel.moderator.remove":
            return 1
        case "channel.channel_points_custom_reward.add":
            return 1
        case "channel.channel_points_custom_reward.update":
            return 1
        case "channel.channel_points_custom_reward.remove":
            return 1
        case "channel.channel_points_custom_reward_redemption.add":
            return 1
        case "channel.channel_points_custom_reward_redemption.update":
            return 1
        case "channel.poll.begin":
            return 1
        case "channel.poll.progress":
            return 1
        case "channel.poll.end":
            return 1
        case "channel.prediction.begin":
            return 1
        case "channel.prediction.progress":
            return 1
        case "channel.prediction.lock":
            return 1
        case "channel.prediction.end":
            return 1
        case "channel.charity_campaign.donate":
            return 1
        case "channel.charity_campaign.start":
            return 1
        case "channel.charity_campaign.progress":
            return 1
        case "channel.charity_campaign.stop":
            return 1
        case "drop.entitlement.grant":
            return 1
        case "extension.bits_transaction.create":
            return 1
        case "channel.goal.begin":
            return 1
        case "channel.goal.progress":
            return 1
        case "channel.goal.end":
            return 1
        case "channel.hype_train.begin":
            return 1
        case "channel.hype_train.progress":
            return 1
        case "channel.hype_train.end":
            return 1
        case "channel.shield_mode.begin":
            return 1
        case "channel.shield_mode.end":
            return 1
        case "channel.shoutout.create":
            return 1
        case "channel.shoutout.receive":
            return 1
        case "stream.online":
            return 1
        case "stream.offline":
            return 1
        case "user.authorization.grant":
            return 1
        case "user.authorization.revoke":
            return 1
        case "user.update":
            return 1


def ipc_request(loop, *args, **kwargs):
    ipc_client = Client(
        host=settings.IPC_HOST, port=settings.IPC_PORT, secret_key=settings.IPC_SECRET
    )
    loop.run_until_complete(ipc_client.request(*args, **kwargs))
    loop.run_until_complete(ipc_client.close())


@app.task(base=SqlAlchemyTask)
def create_twitch_eventsub(eventsub: dict):
    eventsub: EventSubscription = EventSubscription.parse_obj(eventsub)

    token = get_twitch_access_token()

    twitch_headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": settings.TWITCH_CLIENT_ID,
        "Content-Type": "application/json",
    }

    twitch_payload = {
        "type": eventsub.event,
        "version": get_event_version(eventsub),
        "condition": get_event_condition(db_session, eventsub),
        "transport": {
            "method": "webhook",
            "callback": f"{settings.API_HOSTNAME}/twitch/event-sub/callback",
            "secret": settings.TWITCH_WEBHOOK_SECRET,
        },
    }

    resp = requests.post(
        f"{settings.TWITCH_API_URL}/eventsub/subscriptions",
        headers=twitch_headers,
        json=twitch_payload,
    )

    if resp.status_code >= 400:
        raise Exception(f"Invalid response from Twitch {resp.status_code=} {resp.text}")

    eventsub_crud.update_twitch_id(
        db_session, db_obj=eventsub, twitch_id=resp.json()["data"][0]["id"]
    )


@app.task(base=SqlAlchemyTask)
def delete_twitch_eventsub(eventsub: dict):
    eventsub: EventSubscription = EventSubscription.parse_obj(eventsub)

    if eventsub.twitch_id:
        token = get_twitch_access_token()

        twitch_headers = {
            "Authorization": f"Bearer {token}",
            "Client-Id": settings.TWITCH_CLIENT_ID,
        }

        requests.delete(
            f"{settings.TWITCH_API_URL}/eventsub/subscriptions?id={eventsub.twitch_id}",
            headers=twitch_headers,
        )

    eventsub_crud.remove(db_session, uuid=eventsub.uuid)


@app.task(base=SqlAlchemyTask)
def process_notification(message_id: str, subscription_type, data: dict):
    loop = asyncio.get_event_loop()

    data = get_model_by_subscription_type(subscription_type, data)

    r = redis.Redis(host="redis", port=6379, decode_responses=True)

    # Add message id to already processed set and check if it already exists
    result = r.sadd(TWITCH_MESSAGE_ID_SET_KEY, message_id)

    # Stop handling as message id already in set
    if result == 0:
        return

    if hasattr(data, "broadcaster_user_id"):
        user = user_crud.get_by_twitch_id(db_session, data.broadcaster_user_id)
    else:
        user = None

    if user:
        sent = []
        if isinstance(data, StreamOnlineEvent):
            eventsubs = eventsub_crud.get_multi_by_user_uuid_and_event(
                db_session, user.uuid, "stream.online"
            )
            sent += [
                f"{user.name} =[stream.online]=> {x.channel_discord_id}"
                for x in eventsubs
            ]

            token = get_twitch_access_token()

            twitch_headers = {
                "Authorization": f"Bearer {token}",
                "Client-Id": settings.TWITCH_CLIENT_ID,
            }

            # channel_info = requests.get(
            #    f"{settings.TWITCH_API_URL}/channels",
            #    headers=twitch_headers,
            #    params={
            #        "broadcaster_id": user.twitch_id
            #    }).json()

            streams = requests.get(
                f"{settings.TWITCH_API_URL}/streams",
                headers=twitch_headers,
                params={"user_id": user.twitch_id, "type": "live"},
            ).json()

            # if isinstance(channel_info, list) and len(channel_info) > 0:
            #    default_title = channel_info[0]["title"]
            #    game = channel_info[0]["game_name"]
            #    tags = channel_info[0]["tags"]
            # else:
            #    default_title = "Hey I'm live!"
            #    game = None
            #    tags = None
            default_description = f"Hey {data.broadcaster_user_name} is now live!"

            if "data" in streams and len(streams["data"]) > 0:
                default_title = streams["data"][0]["title"]
                game = streams["data"][0]["game_name"]
                tags = streams["data"][0]["tags"]
                viewers = streams["data"][0]["viewer_count"]
                started = streams["data"][0]["started_at"]
                thumbnail = streams["data"][0]["thumbnail_url"].format(
                    width=1280 // 2, height=720 // 2
                )
                is_mature = streams["data"][0]["is_mature"]
            else:
                default_title = "Hey I'm live!"
                game = None
                tags = None
                viewers = None
                started = None
                thumbnail = None
                is_mature = None

            for eventsub in eventsubs:
                ipc_request(
                    loop,
                    "send_live_notification",
                    broadcaster_title=eventsub.custom_title
                    if eventsub.custom_title
                    else default_title,
                    broadcaster_description=eventsub.custom_description
                    if eventsub.custom_description
                    else default_description,
                    notification_content=eventsub.message,
                    channel_discord_id=eventsub.channel_discord_id,
                    server_discord_id=eventsub.server_discord_id,
                    broadcaster_name=data.broadcaster_user_name,
                    twitch_icon=user.icon_url,
                    twitch_url=f"https://twitch.tv/{data.broadcaster_user_login}",
                    twitch_game=game,
                    twitch_tags=tags,
                    twitch_viewers=viewers,
                    twitch_started=started,
                    twitch_thumbnail=thumbnail,
                    twitch_is_mature=is_mature,
                )
        elif isinstance(data, ChannelSubscribeEvent):
            eventsubs = eventsub_crud.get_multi_by_user_uuid_and_event(
                db_session, user.uuid, "channel.subscribe"
            )
            sent += [
                f"{user.name} =[channel.subscribe]=> {x.channel_discord_id}"
                for x in eventsubs
            ]

            for eventsub in eventsubs:
                ipc_request(
                    loop,
                    "send_new_subscription_notification",
                    notification_content=eventsub.message,
                    channel_discord_id=eventsub.channel_discord_id,
                    server_discord_id=eventsub.server_discord_id,
                    broadcaster_name=data.broadcaster_user_name,
                    twitch_icon=user.icon_url,
                    twitch_url=f"https://twitch.tv/{data.broadcaster_user_login}",
                    twitch_user_name=data.user_name,
                    twitch_tier=data.tier,
                    twitch_is_gift=data.is_gift,
                )
        elif isinstance(data, ChannelSubscriptionMessageEvent):
            eventsubs = eventsub_crud.get_multi_by_user_uuid_and_event(
                db_session, user.uuid, "channel.subscription.message"
            )
            sent += [
                f"{user.name} =[channel.subscription.message]=> {x.channel_discord_id}"
                for x in eventsubs
            ]

            for eventsub in eventsubs:
                ipc_request(
                    loop,
                    "send_resubscription_notification",
                    notification_content=eventsub.message,
                    channel_discord_id=eventsub.channel_discord_id,
                    server_discord_id=eventsub.server_discord_id,
                    broadcaster_name=data.broadcaster_user_name,
                    twitch_icon=user.icon_url,
                    twitch_url=f"https://twitch.tv/{data.broadcaster_user_login}",
                    twitch_user_name=data.user_name,
                    twitch_tier=data.tier,
                    twitch_is_gift=data.is_gift,
                    twitch_message_text=data.message.text,
                    twitch_message_emotes=data.message.emotes,
                    twitch_cumulative_months=data.cumulative_months,
                    twitch_streak_months=data.streak_months,
                    twitch_duration_months=data.duration_months,
                )
        elif isinstance(data, ChannelSubscriptionGiftEvent):
            eventsubs = eventsub_crud.get_multi_by_user_uuid_and_event(
                db_session, user.uuid, "channel.subscription.gift"
            )
            sent += [
                f"{user.name} =[channel.subscription.gift]=> {x.channel_discord_id}"
                for x in eventsubs
            ]

            for eventsub in eventsubs:
                ipc_request(
                    loop,
                    "send_gift_subscription_notification",
                    notification_content=eventsub.message,
                    channel_discord_id=eventsub.channel_discord_id,
                    server_discord_id=eventsub.server_discord_id,
                    broadcaster_name=data.broadcaster_user_name,
                    twitch_icon=user.icon_url,
                    twitch_url=f"https://twitch.tv/{data.broadcaster_user_login}",
                    twitch_user_name=data.user_name,
                    twitch_tier=data.tier,
                    twitch_total=data.total,
                    twitch_cumulative_total=data.cumulative_total,
                    twitch_is_anonymous=data.is_anonymous
                )
        elif isinstance(data, ChannelCheerEvent):
            eventsubs = eventsub_crud.get_multi_by_user_uuid_and_event(
                db_session, user.uuid, "channel.cheer"
            )
            sent += [
                f"{user.name} =[channel.cheer]=> {x.channel_discord_id}"
                for x in eventsubs
            ]

            for eventsub in eventsubs:
                ipc_request(
                    loop,
                    "send_cheer_notification",
                    notification_content=eventsub.message,
                    channel_discord_id=eventsub.channel_discord_id,
                    server_discord_id=eventsub.server_discord_id,
                    broadcaster_name=data.broadcaster_user_name,
                    twitch_icon=user.icon_url,
                    twitch_url=f"https://twitch.tv/{data.broadcaster_user_login}",
                    twitch_user_name=data.user_name,
                    twitch_message=data.message,
                    twitch_bits=data.bits
                )
        elif isinstance(data, ChannelRaidEvent):
            eventsubs = eventsub_crud.get_multi_by_user_uuid_and_event(
                db_session, user.uuid, "channel.raid"
            )
            sent += [
                f"{user.name} =[channel.raid]=> {x.channel_discord_id}"
                for x in eventsubs
            ]

            for eventsub in eventsubs:
                ipc_request(
                    loop,
                    "send_raid_notification",
                    notification_content=eventsub.message,
                    channel_discord_id=eventsub.channel_discord_id,
                    server_discord_id=eventsub.server_discord_id,
                    broadcaster_name=data.to_broadcaster_user_name,
                    twitch_icon=user.icon_url,
                    twitch_url=f"https://twitch.tv/{data.to_broadcaster_user_login}",
                    twitch_user_name=data.from_broadcaster_user_name,
                    twitch_viewers=data.viewers
                )
        elif isinstance(data, HypeTrainEndEvent):
            eventsubs = eventsub_crud.get_multi_by_user_uuid_and_event(
                db_session, user.uuid, "channel.hype_train.end"
            )
            sent += [
                f"{user.name} =[channel.hype_train.end]=> {x.channel_discord_id}"
                for x in eventsubs
            ]

            for eventsub in eventsubs:
                ipc_request(
                    loop,
                    "send_hype_train_end_notification",
                    notification_content=eventsub.message,
                    channel_discord_id=eventsub.channel_discord_id,
                    server_discord_id=eventsub.server_discord_id,
                    broadcaster_name=data.broadcaster_user_name,
                    twitch_icon=user.icon_url,
                    twitch_url=f"https://twitch.tv/{data.broadcaster_user_login}",
                    twitch_user_name=data.from_broadcaster_user_name,
                    twitch_level=data.level,
                    twitch_total=data.total,
                    twitch_top_contributions=[x.dict() for x in data.top_contributions],
                    twitch_started_at=data.started_at,
                    twitch_ended_at=data.ended_at,
                    twitch_cooldown_ends_at=data.cooldown_ends_at,
                    twitch_golden_kappa=data.is_golden_kappa_train
                )
        else:
            return f"Unknown type for: {data.json()}"

        return sent
    else:
        return "No user found..."
