from fastapi import Depends, HTTPException, Request
from nextcord.ext import ipc
from sqlmodel import Session

from core.database import engine
from core.database.crud.users import crud
from core.database.models.users import User

from config import settings


def get_db():
    with Session(engine) as session:
        yield session


def get_ipc():
    ipc_client = ipc.Client(
        host=settings.IPC_HOST, port=settings.IPC_PORT,
        secret_key=settings.IPC_SECRET
    )
    return ipc_client


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    req_user = request.session.get("user", None)

    if req_user is None:
        raise HTTPException(status_code=401, detail="Not authorized")
    if "id" not in req_user:
        raise HTTPException(status_code=400, detail="Invalid session")

    user = crud.get(db, id=req_user["id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
