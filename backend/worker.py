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
from core.database.models.user import UserUpdate
from core.database.models.eventsubs import EventSubscription
from core.database.crud.eventsubs import crud as eventsub_crud
from core.database.crud.user import crud as user_crud
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
                eventsubs = eventsub_crud.get_multi_by_user_uuid_and_event(session, user.uuid, "StreamOnlineEvent")
                for eventsub in eventsubs:
                    server = server_crud.get(session, eventsub.server_uuid)
                    loop.run_until_complete(ipc_client.request(
                        "send_live_notification",
                        broadcaster_title=eventsub.custom_title if eventsub.custom_title else "Hey I'm live!",
                        broadcaster_description=eventsub.custom_description if eventsub.custom_description else f"Hey {data.broadcaster_user_name} is now live!",
                        discord_channel_id=server.discord_channel_id,
                        broadcaster_name=data.broadcaster_user_name,
                        twitch_icon=user.icon_url,
                        twitch_url=f"https://twitch.tv/{data.broadcaster_user_login}"
                    ))

