import uuid

from fastapi import APIRouter, Depends, Path, Body
from sqlmodel import Session

from core.deps import get_db, get_current_user
from core.database.models.users import User
from core.database.models.eventsubs import EventSubscription, EventSubscriptionCreate, \
    EventSubscriptionUpdate
from core.database.crud import eventsubs, memberships

from worker import create_twitch_eventsub, delete_twitch_eventsub

from core.routes import not_authorized, not_found, forbidden

router = APIRouter()


def check_feature_availability(db: Session, current_user: User) -> None:
    mships = memberships.crud.get_by_user_uuid(db, current_user.uuid)

    if len(mships) == 0 and not current_user.is_superadmin:
        raise forbidden()


@router.get("/", response_model=list[EventSubscription], tags=["eventsubs"])
def get_eventsubs(*, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    if not current_user:
        raise not_authorized()

    check_feature_availability(db, current_user)

    return eventsubs.crud.get_multi_by_user_uuid(db, current_user.uuid)


@router.get("/user/{user_uuid}", response_model=list[EventSubscription],
            tags=["eventsubs"])
def get_eventsubs_by_user(*, db: Session = Depends(get_db),
                          current_user: User = Depends(get_current_user),
                          user_uuid: uuid.UUID = Path(..., description="UUID of user")):
    if not current_user:
        raise not_authorized()

    if not current_user.is_superadmin:
        raise forbidden()

    return eventsubs.crud.get_multi_by_user_uuid(db, user_uuid)


@router.post("/", response_model=EventSubscription, tags=["eventsubs"])
def create_eventsub(*,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user),
                    eventsub: EventSubscriptionCreate = Body(...,
                                                             description="Eventsubscription")
                    ):
    if not current_user:
        raise not_authorized()

    check_feature_availability(db, current_user)

    if not current_user.is_superadmin and current_user.uuid != eventsub.user_uuid:
        raise forbidden()

    db_eventsub = eventsubs.crud.create(db, obj_in=eventsub)

    create_twitch_eventsub.delay(db_eventsub.dict())

    return db_eventsub


@router.get("/{eventsub_uuid}", response_model=EventSubscription, tags=["eventsubs"])
def get_eventsub(*,
                 db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user),
                 eventsub_uuid: uuid.UUID = Path(...,
                                                 description="UUID of Event subscription")
                 ):
    if not current_user:
        raise not_authorized()

    check_feature_availability(db, current_user)

    eventsub = eventsubs.crud.get(db, eventsub_uuid)

    if not eventsub:
        raise not_found("Event Subscription")

    if not current_user.is_superadmin and current_user.uuid != eventsub.user_uuid:
        raise forbidden()

    return eventsub


@router.put("/{eventsub_uuid}", response_model=EventSubscription, tags=["eventsubs"])
def update_eventsub(*,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user),
                    eventsub_uuid: uuid.UUID = Path(...,
                                                    description="UUID of Event subscription"),
                    eventsub_update: EventSubscriptionUpdate = Body(...,
                                                                    description="Contents to be updated")
                    ):
    if not current_user:
        raise not_authorized()

    check_feature_availability(db, current_user)

    db_eventsub = eventsubs.crud.get(db, eventsub_uuid)

    if not db_eventsub:
        raise not_found("Event Subscription")

    if not current_user.is_superadmin and current_user.uuid != db_eventsub.user_uuid:
        raise forbidden()

    db_eventsub = eventsubs.crud.update(db, db_obj=db_eventsub, obj_in=eventsub_update)
    return db_eventsub


@router.delete("/{eventsub_uuid}", response_model=EventSubscription, tags=["eventsubs"])
def delete_eventsub(*,
                    current_user: User = Depends(get_current_user),
                    db: Session = Depends(get_db),
                    eventsub_uuid: uuid.UUID = Path(...,
                                                    description="UUID of Event Subscription")):
    if not current_user:
        raise not_authorized()

    db_eventsub = eventsubs.crud.get(db, eventsub_uuid)

    if not db_eventsub:
        raise not_found("Event Subscription")

    if not current_user.is_superadmin and current_user.uuid != db_eventsub.user_uuid:
        raise forbidden()

    #eventsubs.crud.remove(db, uuid=eventsub_uuid)
    delete_twitch_eventsub.delay(db_eventsub.dict())

    return db_eventsub
