from fastapi import APIRouter, Depends, HTTPException
from nextcord.ext.ipc import Client

from core.database.models.discord import DiscordServer
from core.database.models.users import User

from core.deps import get_current_user, get_ipc
from core.routes import not_authorized, not_found, forbidden

from config import settings


router = APIRouter()


@router.get("/servers", response_model=list[DiscordServer], tags=["discord"])
def get_servers(*, current_user: User = Depends(get_current_user), ipc: Client = Depends(get_ipc)):
    if not current_user:
        raise not_authorized()

    if not current_user.discord_id:
        raise HTTPException(status_code=400, detail="Discord not linked!")

    if current_user.is_superadmin:
        servers = await ipc.request(
            "get_all_servers"
        )
    else:
        servers = await ipc.request(
            "get_user_servers",
            user_id=current_user.discord_id
        )

    return [DiscordServer.parse_obj(s) for s in servers]
