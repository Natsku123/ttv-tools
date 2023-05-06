import os
import asyncio
import uuid
import redis

import requests
from celery import Celery
from celery.schedules import crontab

from sqlmodel import Session, select
from nextcord.ext import ipc

from config import settings
from core.database.models.twitch import *
from core.database.models.users import UserUpdate
from core.database.models.eventsubs import EventSubscription
from core.database.crud.eventsubs import crud as eventsub_crud
from core.database.crud.users import crud as user_crud
from core.database.crud.server import crud as server_crud
from core.database import engine

app = Celery(__name__)
app.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379")
app.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379")

TWITCH_MESSAGE_ID_SET_KEY = "twitchmessageids"


def get_twitch_access_token() -> str:
    token_res = requests.post("https://id.twitch.tv/oauth2/token", headers={
        "Content-Type": "application/x-www-form-urlencoded"
    }, params={
        "client_id": settings.TWITCH_CLIENT_ID,
        "client_secret": settings.TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }).json()
    return token_res["access_token"]


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):

    # Update all users twice a day
    sender.add_periodic_task(
        crontab(hour="6,18"),
        update_users.s(update_all=True),
    )


@app.task
def update_users(update_all: bool = False, token: str = None, user_uuids: list[uuid.UUID] = None, twitch_ids: list[str] = None, discord_ids: list[str] = None):

    if not user_uuids:
        user_uuids = []
    if not twitch_ids:
        twitch_ids = []
    if not discord_ids:
        discord_ids = []

    if not token:
        token = get_twitch_access_token()

    twitch_headers = {
        "Authorization": f"Bearer {token}"
    }

    with Session(engine) as session:
        if not update_all:
            users_by_uuid = [user_crud.get(session, x) for x in user_uuids]
            users_by_twitch = [user_crud.get_by_twitch_id(session, x) for x in twitch_ids]
            users_by_discord = [user_crud.get_by_discord_id(session, x) for x in discord_ids]

            users = users_by_uuid + users_by_twitch + users_by_discord
        else:
            users = user_crud.get_multi(session)

        users_twitch_ids = list(set([x.twitch_id for x in users if x]))

        user_data = requests.get(
            "https://api.twitch.tv/helix/users",
            headers=twitch_headers,
            params={
                "id": users_twitch_ids
            }).json()

        for ud in user_data:
            user = user_crud.get_by_twitch_id(session, ud["id"])

            if user:
                user_update = UserUpdate(**{
                    "name": ud["display_name"],
                    "login_name": ud["login"],
                    "icon_url": ud["profile_image_url"],
                    "offline_image_url": ud["offline_image_url"],
                    "description": ud["description"]
                })

                user_crud.update(session, user, user_update)


def get_event_condition(e: EventSubscription) -> dict:
    with Session(engine) as session:
        user = user_crud.get(session, e.user_uuid)

    match e.event:
        case "channel.update":
            return {
                "broadcaster_user_id": user.twitch_id
            }
        case "channel.follow":
            return {
                "broadcaster_user_id": user.twitch_id,
                "moderator_user_id": user.twitch_id
            }
        case "channel.subscribe":
            return {
                "broadcaster_user_id": user.twitch_id
            }
        case "channel.subscription.end":
            return {
                "broadcaster_user_id": user.twitch_id
            }
        case "channel.subscription.gift":
            return {
                "broadcaster_user_id": user.twitch_id
            }
        case "channel.subscription.message":
            return {
                "broadcaster_user_id": user.twitch_id
            }
        case "channel.cheer":
            return {
                "broadcaster_user_id": user.twitch_id
            }
        case "channel.raid":
            # TODO add from_broadcaster_user_id also?
            return {
                "to_broadcaster_user_id": user.twitch_id
            }
        case "channel.ban":
            return {
                "broadcaster_user_id": user.twitch_id
            }
        case "channel.unban":
            return {
                "broadcaster_user_id": user.twitch_id
            }
        case "channel.moderator.add":
            return {
                "broadcaster_user_id": user.twitch_id
            }
        case "channel.moderator.remove":
            return {
                "broadcaster_user_id": user.twitch_id
            }
        case "channel.channel_points_custom_reward.add":
            return {
                "broadcaster_user_id": user.twitch_id
            }
        case "channel.channel_points_custom_reward.update":
            return {
                "broadcaster_user_id": user.twitch_id
            }
        case "channel.channel_points_custom_reward.remove":
            return {
                "broadcaster_user_id": user.twitch_id
            }
        case "channel.channel_points_custom_reward_redemption.add":
            # TODO reward id check!
            return {
                "broadcaster_user_id": user.twitch_id
            }
        case "channel.channel_points_custom_reward_redemption.update":
            # TODO reward id check!
            return {
                "broadcaster_user_id": user.twitch_id
            }
        case "channel.poll.begin":
            return {
                "broadcaster_user_id": user.twitch_id
            }
        case "channel.poll.progress":
            return {
                "broadcaster_user_id": user.twitch_id
            }
        case "channel.poll.end":
            return {
                "broadcaster_user_id": user.twitch_id
            }
        case "channel.prediction.begin":
            return {
                "broadcaster_user_id": user.twitch_id
            }
        case "channel.prediction.progress":
            return {
                "broadcaster_user_id": user.twitch_id
            }
        case "channel.prediction.lock":
            return {
                "broadcaster_user_id": user.twitch_id
            }
        case "channel.prediction.end":
            return {
                "broadcaster_user_id": user.twitch_id
            }
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
            return {
                "broadcaster_user_id": user.twitch_id
            }
        case "channel.goal.progress":
            return {
                "broadcaster_user_id": user.twitch_id
            }
        case "channel.goal.end":
            return {
                "broadcaster_user_id": user.twitch_id
            }
        case "channel.hype_train.begin":
            return {
                "broadcaster_user_id": user.twitch_id
            }
        case "channel.hype_train.progress":
            return {
                "broadcaster_user_id": user.twitch_id
            }
        case "channel.hype_train.end":
            return {
                "broadcaster_user_id": user.twitch_id
            }
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
            return {
                "broadcaster_user_id": user.twitch_id
            }
        case "stream.offline":
            return {
                "broadcaster_user_id": user.twitch_id
            }
        case "user.authorization.grant":
            return {
                "client_id": settings.TWITCH_CLIENT_ID
            }
        case "user.authorization.revoke":
            return {
                "client_id": settings.TWITCH_CLIENT_ID
            }
        case "user.update":
            return {
                "user_id": user.twitch_id
            }


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


@app.task
def create_twitch_eventsub(eventsub: dict):
    eventsub: EventSubscription = EventSubscription.parse_obj(eventsub)

    token = get_twitch_access_token()

    twitch_headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": settings.TWITCH_CLIENT_ID,
        "Content-Type": "application/json",
    }

    resp = requests.post(
        "https://api.twitch.tv/helix/eventsub/subscriptions",
        headers=twitch_headers,
        json={
            "type": eventsub.event,
            "version": get_event_version(eventsub),
            "condition": get_event_condition(eventsub),
            "transport": {
                "method": "webhook",
                "callback": f"{settings.API_HOSTNAME}/twitch/event-sub/callback",
                "secret": settings.TWITCH_WEBHOOK_SECRET
            }
        }
    ).json()

    with Session(engine) as session:
        eventsub_crud.update_twitch_id(session, eventsub, resp["data"][0]["id"])


@app.task
def delete_twitch_eventsub(eventsub: dict):
    eventsub: EventSubscription = EventSubscription.parse_obj(eventsub)

    token = get_twitch_access_token()

    twitch_headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": settings.TWITCH_CLIENT_ID,
    }

    requests.delete(
        f"https://api.twitch.tv/helix/eventsub/subscriptions?id={eventsub.twitch_id}",
        headers=twitch_headers,
    )

    with Session(engine) as session:
        eventsub_crud.remove(session, uuid=eventsub.uuid)


@app.task
def process_notification(message_id: str, data: dict):
    loop = asyncio.get_event_loop()
    ipc_client = ipc.Client(
        host=settings.IPC_HOST, port=settings.IPC_PORT,
        secret_key=settings.IPC_SECRET
    )

    data = TwitchEvent.parse_obj(data)

    r = redis.Redis(host="redis", port=6379, decode_responses=True)

    # Add message id to already processed set and check if it already exists
    result = r.sadd(TWITCH_MESSAGE_ID_SET_KEY, message_id)

    # Stop handling as message id already in set
    if result == 0:
        return

    with Session(engine) as session:

        if hasattr(data, "broadcaster_user_id"):
            user = user_crud.get_by_twitch_id(session, data.broadcaster_user_id)
        else:
            user = None

        if user:

            if isinstance(data, StreamOnlineEvent):
                eventsubs = eventsub_crud.get_multi_by_user_uuid_and_event(session, user.uuid, "stream.online")
                for eventsub in eventsubs:
                    loop.run_until_complete(ipc_client.request(
                        "send_live_notification",
                        broadcaster_title=eventsub.custom_title if eventsub.custom_title else "Hey I'm live!",
                        broadcaster_description=eventsub.custom_description if eventsub.custom_description else f"Hey {data.broadcaster_user_name} is now live!",
                        channel_discord_id=eventsub.channel_discord_id,
                        server_discord_id=eventsub.server_discord_id,
                        broadcaster_name=data.broadcaster_user_name,
                        twitch_icon=user.icon_url,
                        twitch_url=f"https://twitch.tv/{data.broadcaster_user_login}"
                    ))

