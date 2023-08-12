import uuid

from fastapi import APIRouter, Depends, Path, Body
from sqlmodel import Session

from core.deps import get_db, get_current_user
from core.database.models.users import User
from core.database.models.teams import Team
from core.database.models.invites import TeamInvite, TeamInviteCreate, TeamInviteUpdate
from core.database.models.memberships import Membership, MembershipCreate
from core.database.crud import teams
from core.database.crud import memberships
from core.database.crud import invites

from core.routes import not_authorized, not_found, forbidden

router = APIRouter()


def check_invite_permissions(
        db: Session,
        current_user: User,
        invite: TeamInvite | TeamInviteCreate
) -> tuple[Team, Membership]:
    db_team = teams.crud.get(db, invite.team_uuid)

    if not db_team:
        raise not_found("Team")

    mship = memberships.crud.get_by_team_user_uuid(db, current_user.uuid,
                                                   invite.team_uuid)

    if not current_user.is_superadmin and (mship is None or not mship.is_admin):
        raise forbidden()

    return db_team, mship


@router.get("/", response_model=list[TeamInvite], tags=["invites"])
def get_invites(*, db: Session = Depends(get_db),
                current_user: User | None = Depends(get_current_user)):
    if not current_user:
        raise not_authorized()

    if not current_user.is_superadmin:
        raise forbidden()

    return invites.crud.get_multi(db)


@router.post("/", response_model=TeamInvite, tags=["invites"])
def create_invite(*,
                  db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user),
                  invite: TeamInviteCreate = Body(..., description="Invite")
                  ):
    if not current_user:
        raise not_authorized()

    _, db_mship = check_invite_permissions(db, current_user, invite)

    if not current_user.is_superadmin and not db_mship.allowed_invites:
        raise forbidden()

    db_invite = invites.crud.create(db, obj_in=invite)
    return db_invite


@router.get("/{invite_uuid}", response_model=TeamInvite, tags=["invites"])
def get_invite(*,
               db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user),
               invite_uuid: uuid.UUID = Path(..., description="UUID of invite")
               ):
    if not current_user:
        raise not_authorized()

    invite = invites.crud.get(db, invite_uuid)

    if not invite:
        raise not_found("Invite")

    check_invite_permissions(db, current_user, invite)

    return invite


@router.put("/{invite_uuid}", response_model=TeamInvite, tags=["invites"])
def update_invite(*,
                  db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user),
                  invite_uuid: uuid.UUID = Path(..., description="UUID of invite"),
                  invite_update: TeamInviteUpdate = Body(...,
                                                         description="Contents to be updated")
                  ):
    if not current_user:
        raise not_authorized()

    db_invite = invites.crud.get(db, invite_uuid)

    if not db_invite:
        raise not_found("Invite")

    check_invite_permissions(db, current_user, db_invite)

    db_invite = invites.crud.update(db, db_obj=db_invite, obj_in=invite_update)
    return db_invite


@router.delete("/{invite_uuid}", response_model=TeamInvite, tags=["invites"])
def delete_invite(*,
                  current_user: User = Depends(get_current_user),
                  db: Session = Depends(get_db),
                  invite_uuid: uuid.UUID = Path(..., description="UUID of invite")):
    if not current_user:
        raise not_authorized()

    db_invite = invites.crud.get(db, invite_uuid)

    if not db_invite:
        raise not_found("Invite")

    check_invite_permissions(db, current_user, db_invite)

    invites.crud.remove(db, uuid=invite_uuid)

    return db_invite


@router.post("/{invite_uuid}/redeem", response_model=TeamInvite, tags=["invites"])
def redeem_invite(*,
                  current_user: User = Depends(get_current_user),
                  db: Session = Depends(get_db),
                  invite_uuid: uuid.UUID = Path(..., description="UUID of invite")):
    if not current_user:
        raise not_authorized()

    db_invite = invites.crud.get(db, invite_uuid)

    if not db_invite:
        raise not_found("Invite")

    if not db_invite.user_twitch_id == current_user.twitch_id:
        raise forbidden()

    team = teams.crud.get(db, db_invite.team_uuid)

    is_first = len(team.members) == 0

    membership = MembershipCreate(**{
        "team_uuid": db_invite.team_uuid,
        "user_uuid": current_user.uuid,
        "is_admin": is_first,
        "allowed_invites": is_first
    })

    memberships.crud.create(db, obj_in=membership)

    db_invite = invites.crud.remove(db, uuid=invite_uuid)

    return db_invite
