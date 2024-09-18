import uuid

from fastapi import APIRouter, Depends, Path, Body
from sqlmodel import Session

from core.database.models.readonly import TeamRead, MembershipRead, UserRead
from core.deps import get_db, get_current_user
from core.database.models.users import User, UserUpdate
from core.database.crud import users, memberships

from core.routes import not_authorized, not_found, forbidden

router = APIRouter()


@router.get("/", response_model=UserRead, tags=["users"])
def users_root(*, current_user: User | UserRead = Depends(get_current_user)) -> UserRead:
    if not current_user:
        raise not_authorized()

    return current_user


@router.get("/all", response_model=list[UserRead], tags=["users"])
def get_users(
    *, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[UserRead]:
    if not current_user:
        raise not_authorized()

    if not current_user.is_superadmin:
        raise forbidden()

    return users.crud.get_multi(db)


@router.get("/{user_uuid}", response_model=UserRead, tags=["users"])
def get_user(
    *,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    user_uuid: uuid.UUID = Path(..., description="UUID of user"),
) -> UserRead:
    if not current_user:
        raise not_authorized()

    if not current_user.is_superadmin and user_uuid != current_user.uuid:
        raise forbidden()

    user = users.crud.get(db, user_uuid)

    if not user:
        raise not_found("User")

    return user


@router.put("/{user_uuid", response_model=UserRead, tags=["users"])
def update_user(
    *,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    user_uuid: uuid.UUID = Path(..., description="UUID of user"),
    user_update: UserUpdate = Body(..., description="Contents to be updated"),
) -> UserRead:
    if not current_user:
        raise not_authorized()

    if not current_user.is_superadmin or user_uuid != current_user.uuid:
        raise forbidden()

    db_user = users.crud.get(db, user_uuid)

    if not db_user:
        raise not_found("User")

    if not current_user.is_superadmin and user_update.is_superadmin:
        raise forbidden()

    db_user = users.crud.update(db, db_obj=db_user, obj_in=user_update)
    return db_user


@router.delete("/{user_uuid}", response_model=UserRead, tags=["users"])
def delete_user(
    *,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    user_uuid: uuid.UUID = Path(..., description="UUID of user"),
) -> UserRead:
    if not current_user:
        raise not_authorized()

    if not current_user.is_superadmin or user_uuid != current_user.uuid:
        raise forbidden()

    db_user = users.crud.get(db, user_uuid)

    if not db_user:
        raise not_found("User")

    users.crud.remove(db, uuid=user_uuid)

    return db_user


@router.get("/teams", response_model=list[TeamRead], tags=["users"])
def get_teams(
    *, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[TeamRead]:
    if not current_user:
        raise not_authorized()

    return memberships.crud.get_by_user_uuid(db, current_user.uuid)
