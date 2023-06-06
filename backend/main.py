from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from authlib.integrations.starlette_client import OAuth
from authlib.integrations.base_client.errors import UnsupportedTokenTypeError, \
    OAuthError
from starlette.responses import RedirectResponse

from sqlmodel import Session

from config import settings
from core.database import SessionLocal
from core.database.models import Meta
from core.database.models.oauth import OAuth2Token
from core.database.models.users import User

from core.routes import twitch, users, teams, invites, eventsubs, discord

from core.deps import get_current_user, get_db

app = FastAPI(root_path=settings.ROOT_PATH)


def custom_openapi():

    # Return "cached" API schema
    if app.openapi_schema:
        return app.openapi_schema

    # Generate OpenAPI Schema
    openapi_schema = get_openapi(
        title="TTV Tools",
        version=f"{settings.VERSION}:{settings.BUILD}",
        routes=app.routes,
    )

    # Make fields that are not required nullable
    for name, component in openapi_schema["components"]["schemas"].items():
        if (
            "required" in component
            and component["required"]
            and "properties" in component
            and component["properties"]
        ):
            for f_name, field in component["properties"].items():
                if f_name not in component["required"]:
                    field["nullable"] = True

                # Update field
                component["properties"][f_name] = field
        # Update component
        openapi_schema["components"]["schemas"][name] = component

    # Save schema, so it doesn't have to be generated every time
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def update_token(name, token, refresh_token=None, access_token=None):

    db = SessionLocal()
    if refresh_token:
        item = (
            db.query(OAuth2Token)
            .filter_by(name=name, refresh_token=refresh_token)
            .first()
        )
    elif access_token:
        item = (
            db.query(OAuth2Token)
            .filter_by(name=name, access_token=access_token)
            .first()
        )
    else:
        db.close()
        return

    # update old token
    item.access_token = token["access_token"]
    item.refresh_token = token.get("refresh_token")
    item.expires_at = token["expires_at"]
    db.add(item)
    db.commit()

    db.close()


oauth = OAuth(update_token=update_token)


def fetch_discord_token(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    token = (
        db.query(OAuth2Token)
        .filter_by(name="discord", user_id=current_user.uuid)
        .first()
    )
    if token:
        return token.to_token()


def fetch_twitch_token(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    token = (
        db.query(OAuth2Token)
        .filter_by(name="twitch", user_id=current_user.uuid)
        .first()
    )
    if token:
        return token.to_token()


# OAuth with discord setup
oauth.register(
    name="discord",
    client_id=settings.DISCORD_CLIENT_ID,
    client_secret=settings.DISCORD_CLIENT_SECRET,
    access_token_url="https://discord.com/api/oauth2/token",
    access_token_params=None,
    authorize_url="https://discord.com/api/oauth2/authorize",
    authorize_params=None,
    api_base_url="https://discord.com/api/v6",
    client_kwargs={"scope": "identify guilds"},
    fetch_token=fetch_discord_token,
)


def _fix_token_response(resp):
    data = resp.json()
    data["scope"] = " ".join(data["scope"])
    resp.json = lambda: data
    return resp
#.register_compliance_hook(
#    'access_token_response', _fix_token_response)


# OAuth with twitch setup
client = oauth.register(
    name="twitch",
    client_id=settings.TWITCH_CLIENT_ID,
    client_secret=settings.TWITCH_CLIENT_SECRET,
    #access_token_url=f"{settings.TWITCH_ID_URL}/token",
    #access_token_params={"client_id": settings.TWITCH_CLIENT_ID, "client_secret": settings.TWITCH_CLIENT_SECRET},
    #access_token_params=None,
    #authorize_url=f"{settings.TWITCH_ID_URL}/authorize",
    #authorize_params=None,
    #userinfo_endpoint="https://id.twitch.tv/oauth2/userinfo",
    server_metadata_url=f"{settings.TWITCH_ID_URL}/.well-known/openid-configuration",
    api_base_url=settings.TWITCH_API_URL,
    client_kwargs={"scope": "channel:read:subscriptions"},
    token_endpoint_auth_method="client_secret_post",
    fetch_token=fetch_twitch_token,
)


async def twitch_get(url: str, token: dict = None):
    if token:
        return await oauth.twitch.get(f"{settings.TWITCH_API_URL}/{url}", token=token,
                                      headers={'Client-Id': settings.TWITCH_CLIENT_ID})
    else:
        return await oauth.twitch.get(f"{settings.TWITCH_API_URL}/{url}",
                                      headers={'Client-Id': settings.TWITCH_CLIENT_ID})

@app.get("/twitch/login", tags=["oauth"], responses={302: {}})
async def twitch_login(request: Request, redirect: str = None):
    redirect_uri = settings.REDIRECT_URL + "/twitch/authorize"

    if redirect is None:
        redirect = settings.SITE_HOSTNAME

    request.session["redirect_url"] = redirect

    return await oauth.twitch.authorize_redirect(request, redirect_uri)


@app.get("/discord/login", tags=["oauth"], responses={302: {}})
async def discord_login(request: Request, redirect: str = None):
    redirect_uri = settings.REDIRECT_URL + "/discord/authorize"

    if redirect is None:
        redirect = settings.SITE_HOSTNAME

    request.session["redirect_url"] = redirect

    return await oauth.discord.authorize_redirect(request, redirect_uri)

@app.get("/logout", tags=["oauth"], responses={307: {}})
async def logout(request: Request):
    redirect_url = settings.SITE_HOSTNAME
    request.session.pop("user", None)
    return RedirectResponse(url=redirect_url)


@app.get(
    "/user_update", tags=["oauth"], responses={401: {"description": "Unauthorized"}}
)
async def user_update(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    token = db.query(OAuth2Token).filter_by(user_id=user.uuid).first()
    if token is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"status": "user updated"}


@app.get(
    "/twitch/authorize",
    tags=["oauth"],
    responses={400: {"description": "Unsupported Token-Type"}},
)
async def twitch_authorize(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.twitch.authorize_access_token(request)
    except OAuthError as e:
        raise HTTPException(status_code=500, detail=f"{e.error}")

#    user = token.get("userinfo")

    try:
        resp = await twitch_get("users", token)
    except UnsupportedTokenTypeError:
        raise HTTPException(status_code=400, detail=f"Unsupported Token-Type")

    profile = resp.json()

    profile = profile["data"][0]

    # Get user
    user = db.query(User).filter_by(twitch_id=profile["id"]).first()

    # If user doesn't exist, create a new one.
    if user is None:
        user = User(
            twitch_id=profile.get("id"),
            name=profile.get("display_name"),
            login_name=profile.get("login"),
            icon_url=profile.get("profile_image_url"),
            offline_image_url=profile.get("offline_image_url"),
            description=profile.get("description"),
            is_superadmin=(profile.get("id") and profile.get("id") == settings.OWNER_TWITCH_ID)
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    if token:
        # Update token
        token_obj = db.query(OAuth2Token).filter_by(user_id=user.uuid, name="twitch").first()
        if token_obj is None:
            token_obj = OAuth2Token(
                user_id=user.uuid,
                name="twitch",
                token_type=token.get("token_type"),
                access_token=token.get("access_token"),
                refresh_token=token.get("refresh_token"),
                expires_at=token.get("expires_at"),
            )
        else:
            token_obj.token_type = (token.get("token_type"),)
            token_obj.access_token = (token.get("access_token"),)
            token_obj.refresh_token = (token.get("refresh_token"),)
            token_obj.expires_at = token.get("expires_at")

        db.add(token_obj)
    db.commit()
    db.refresh(user)

    request.session["user"] = user.jsonable()

    url = request.session.get("redirect_url")
    if url is None:
        url = settings.SITE_HOSTNAME
    else:
        del request.session["redirect_url"]

    return RedirectResponse(url=url)


@app.get(
    "/discord/authorize",
    tags=["oauth"],
    responses={400: {"description": "Unsupported Token-Type"}},
)
async def discord_authorize(request: Request, db: Session = Depends(get_db)):
    token = await oauth.discord.authorize_access_token(request)

    try:
        if token:
            resp = await oauth.discord.get("users/@me", token=token)
        else:
            resp = await oauth.discord.get("users/@me")
    except UnsupportedTokenTypeError:
        raise HTTPException(status_code=400, detail="Unsupported Token-Type")

    profile = resp.json()

    # Get user
    user = db.query(User).filter_by(discord_id=profile["id"]).first()

    url = request.session.get("redirect_url")
    if url is None:
        url = settings.SITE_HOSTNAME
    else:
        del request.session["redirect_url"]

    # If user doesn't exist, nothing to do
    if user is None:
        return RedirectResponse(url=url)

    user.discord_id = profile.get("id")

    db.add(user)

    if token:
        # Update token
        token_obj = db.query(OAuth2Token).filter_by(user_id=user.uuid, name="discord").first()
        if token_obj is None:
            token_obj = OAuth2Token(
                user_id=user.uuid,
                name="discord",
                token_type=token.get("token_type"),
                access_token=token.get("access_token"),
                refresh_token=token.get("refresh_token"),
                expires_at=token.get("expires_at"),
            )
        else:
            token_obj.token_type = (token.get("token_type"),)
            token_obj.access_token = (token.get("access_token"),)
            token_obj.refresh_token = (token.get("refresh_token"),)
            token_obj.expires_at = token.get("expires_at")

        db.add(token_obj)

    db.commit()
    db.refresh(user)

    request.session["user"] = user.jsonable()

    return RedirectResponse(url=url)


@app.get("/meta", response_model=Meta)
def meta():
    return {"version": settings.VERSION, "build": settings.BUILD}


app.include_router(twitch.router, prefix="/twitch")
app.include_router(users.router, prefix="/users")
app.include_router(teams.router, prefix="/teams")
app.include_router(invites.router, prefix="/invites")
app.include_router(eventsubs.router, prefix="/eventsubs")
app.include_router(discord.router, prefix="/discord")
