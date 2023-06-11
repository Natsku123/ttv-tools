import json
import hmac
import hashlib
import requests

from fastapi import APIRouter, Header, Response, Request, Depends, Query

from core.database.models.twitch import get_model_by_subscription_type
from core.database.models.users import User

from core.deps import get_current_user
from core.twitch_tools import get_twitch_headers
from core.routes import not_authorized

from config import settings

from worker import process_notification

router = APIRouter()

HMAC_PREFIX = 'sha256='


@router.get("/users/")
async def get_twitch_users(current_user: User = Depends(get_current_user), login: list[str] = Query(description="Twitch usernames")):
    if not current_user:
        raise not_authorized()

    twitch_headers = get_twitch_headers()

    return requests.get(
        f"{settings.TWITCH_API_URL}/users",
        headers=twitch_headers,
        params={
            "login": login
        }).json()


@router.post("/event-sub/callback")
async def event_sub_callback(
        request: Request,
        Twitch_Eventsub_Message_Id: str = Header(),
        Twitch_Eventsub_Message_Retry: str = Header(),
        Twitch_Eventsub_Message_Type: str = Header(),
        Twitch_Eventsub_Message_Signature: str = Header(),
        Twitch_Eventsub_Message_Timestamp: str = Header(),
        Twitch_Eventsub_Subscription_Type: str = Header(),
        Twitch_Eventsub_Subscription_Version: str = Header()

):
    if Twitch_Eventsub_Message_Type not in ["notification", "webhook_callback_verification", "revocation"]:
        return Response(content="Invalid Message Type!", status_code=400)

    body = await request.body()

    message = Twitch_Eventsub_Message_Id.encode() + Twitch_Eventsub_Message_Timestamp.encode() + body

    original_hmac = HMAC_PREFIX + hmac.new(settings.TWITCH_WEBHOOK_SECRET.encode(), message, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(original_hmac, Twitch_Eventsub_Message_Signature):
        return Response(content="Forbidden", status_code=403)

    json_body = json.loads(body)

    if Twitch_Eventsub_Message_Type == "notification" and 'event' in json_body:
        event = get_model_by_subscription_type(Twitch_Eventsub_Subscription_Type, json_body['event'])

        process_notification.delay(Twitch_Eventsub_Message_Id, Twitch_Eventsub_Subscription_Type, event.dict())
    elif Twitch_Eventsub_Message_Type == "webhook_callback_verification":
        return Response(content=json_body["challenge"], status_code=200, media_type="text/plain")
    elif Twitch_Eventsub_Message_Type == "revocation":
        return Response(status_code=200, content="Revocation complete")

    return {"status": "ok"}
