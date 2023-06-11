from fastapi import Depends, HTTPException, Request
from sqlmodel import Session

from core.database import engine
from core.database.crud.users import crud
from core.database.models.users import User

from core.ipc.client import Client

from config import settings


def get_db():
    with Session(engine) as session:
        yield session


async def get_ipc():
    #async with Client(host=settings.IPC_HOST, port=settings.IPC_PORT, secret_key=settings.IPC_SECRET) as ipc_client:
    #    yield ipc_client
    ipc_client = Client(host=settings.IPC_HOST, port=settings.IPC_PORT, secret_key=settings.IPC_SECRET)
    yield ipc_client
    await ipc_client.close()


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    req_user = request.session.get("user", None)

    if req_user is None:
        raise HTTPException(status_code=401, detail="Not authorized")
    if "uuid" not in req_user:
        raise HTTPException(status_code=400, detail="Invalid session")

    user = crud.get(db, uuid=req_user["uuid"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
