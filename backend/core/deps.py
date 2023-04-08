from fastapi import Depends, HTTPException, Request
from sqlmodel import Session

from core.database import engine
from core.database.crud.user import crud
from core.database.models.users import User


def get_db():
    with Session(engine) as session:
        yield session


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
