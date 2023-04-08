from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from authlib.integrations.starlette_client import OAuth
from authlib.integrations.base_client.errors import UnsupportedTokenTypeError
from starlette.responses import RedirectResponse

from sqlmodel import Session

from config import settings
from core.database import SessionLocal
from core.database.models import Meta
from core.database.models.oauth import OAuth2Token
from core.database.models.users import User

from core.routes import twitch

from core.deps import get_current_user, get_db

app = FastAPI()


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
        .filter_by(name="discord", user_uuid=current_user.uuid)
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
        .filter_by(name="twitch", user_uuid=current_user.uuid)
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

# OAuth with twitch setup
oauth.register(
    name="twitch",
    client_id=settings.TWITCH_CLIENT_ID,
    client_secret=settings.TWITCH_CLIENT_SECRET,
    access_token_url="https://id.twitch.tv/oauth2/token",
    access_token_params=None,
    authorize_url="https://id.twitch.tv/oauth2/authorize",
    authorize_params=None,
    api_base_url="https://api.twitch.tv",
    client_kwargs={"scope": "channel:read:subscriptions"},
    fetch_token=fetch_twitch_token,
)


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
    token = db.query(OAuth2Token).filter_by(user_uuid=user.uuid).first()
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
    token = await oauth.twitch.authorize_access_token(request)

    try:
        if token:
            resp = await oauth.twitch.get("helix/users", token=token)
        else:
            resp = await oauth.twitch.get("helix/users")
    except UnsupportedTokenTypeError:
        raise HTTPException(status_code=400, detail="Unsupported Token-Type")

    profile = resp.json()

    # Get user
    user = db.query(User).filter_by(twitch_id=profile["id"]).first()

    # If user doesn't exist, create a new one.
    if user is None:
        user = User(
            discord_id=profile.get("id"),
            name=profile.get("display_name"),
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    if token:
        # Update token
        token_obj = db.query(OAuth2Token).filter_by(user_uuid=user.uuid, name="twitch").first()
        if token_obj is None:
            token_obj = OAuth2Token(
                user_uuid=user.uuid,
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

    request.session["user"] = user.dict()

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
    user = db.query(User).filter_by(twitch_id=profile["id"]).first()

    url = request.session.get("redirect_url")
    if url is None:
        url = settings.SITE_HOSTNAME
    else:
        del request.session["redirect_url"]

    # If user doesn't exist, nothing to do
    if user is None:
        return RedirectResponse(url=url)

    user.discord_id = profile.get("id")

    if token:
        # Update token
        token_obj = db.query(OAuth2Token).filter_by(user_uuid=user.uuid, name="discord").first()
        if token_obj is None:
            token_obj = OAuth2Token(
                user_uuid=user.uuid,
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

    request.session["user"] = user.dict()

    return RedirectResponse(url=url)


@app.get("/meta", response_model=Meta)
def meta():
    return {"version": settings.VERSION, "build": settings.BUILD}


app.include_router(twitch.router, prefix="/twitch")
