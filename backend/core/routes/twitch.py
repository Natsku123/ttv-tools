import json
import hmac
import hashlib

from fastapi import APIRouter, Header, Response, Request

from core.database.models.twitch import get_model_by_subscription_type

from config import settings

from worker import process_notification

router = APIRouter()

HMAC_PREFIX = 'sha256='


#class TwitchEventSubscriptionCondition(BaseModel):
#    broadcaster_user_id: str


#class TwitchEventSubscriptionTransport(BaseModel):
#    method: str
#    callback: str


#class TwitchEventSubscription(BaseModel):
#    id: str
#    status: str
#    type: str
#    version: str
#    cost: int
#    condition: TwitchEventSubscriptionCondition
#    transport: TwitchEventSubscriptionTransport
#    created_at: datetime


#class TwitchEventNotificationEvent(BaseModel):
#    user_id: str
#    user_login: str
#    user_name: str
#    broadcaster_user_id: str
#    broadcaster_user_login: str
#    broadcaster_user_name: str
#    followed_at: datetime | None


#class TwitchEventNotification(BaseModel):
#    subscription: TwitchEventSubscription
#    event: TwitchEventNotificationEvent

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

        process_notification.delay(Twitch_Eventsub_Message_Id, event.dict())
    elif Twitch_Eventsub_Message_Type == "webhook_callback_verification":
        return Response(content=json_body["challenge"], status_code=200, media_type="text/plain")
    elif Twitch_Eventsub_Message_Type == "revocation":
        return Response(status_code=200, content="Revocation complete")

    return {"status": "ok"}
