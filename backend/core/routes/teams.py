import uuid

from fastapi import APIRouter, Depends, Path, Body
from sqlmodel import Session

from core.deps import get_db, get_current_user
from core.database.models.users import User
from core.database.models.teams import Team, TeamUpdate, TeamCreate
from core.database.models.invites import TeamInvite
from core.database.models.memberships import Membership, MembershipUpdate
from core.database.crud import teams
from core.database.crud import memberships
from core.database.crud import invites

from core.routes import not_authorized, not_found, forbidden

router = APIRouter()


def check_membership(db: Session, current_user: User,
                     team_uuid: uuid.UUID) -> Membership:
    mship = memberships.crud.get_by_team_user_uuid(db, current_user.uuid, team_uuid)

    if not current_user.is_superadmin and mship is None:
        raise forbidden()

    return mship


def check_adminship(db: Session, current_user: User,
                    team_uuid: uuid.UUID) -> Membership:
    mship = memberships.crud.get_by_team_user_uuid(db, current_user.uuid, team_uuid)

    if not current_user.is_superadmin and (mship is None or not mship.is_admin):
        raise forbidden()

    return mship


@router.get("/", response_model=list[str | Team], tags=["teams"])
def get_teams(*, db: Session = Depends(get_db),
              current_user: User | None = Depends(get_current_user)):
    if not current_user:
        return [team.name for team in teams.crud.get_multi(db)]
    elif not current_user.is_superadmin:
        return current_user.teams
    else:
        return teams.crud.get_multi(db)


@router.post("/", response_model=Team, tags=["teams"])
def create_teams(*,
                 db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user),
                 team: TeamCreate = Body(..., description="Team")
                 ):
    if not current_user:
        raise not_authorized()

    if not current_user.is_superadmin:
        raise forbidden()

    db_team = teams.crud.create(db, obj_in=team)
    return db_team


@router.get("/{team_uuid}", response_model=Team, tags=["teams"])
def get_team(*,
             db: Session = Depends(get_db),
             current_user: User = Depends(get_current_user),
             team_uuid: uuid.UUID = Path(..., description="UUID of team")
             ):
    if not current_user:
        raise not_authorized()

    team = teams.crud.get(db, team_uuid)

    if not team:
        raise not_found("Team")

    return team


@router.get("/{team_uuid}/invites", response_model=list[TeamInvite],
            tags=["teams", "invites"])
def get_invites_by_team(*,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user),
                        team_uuid: uuid.UUID = Path(..., description="UUID of team")
                        ):
    if not current_user:
        raise not_authorized()

    team = teams.crud.get(db, team_uuid)

    if not team:
        raise not_found("Team")

    check_adminship(db, current_user, team_uuid)

    return invites.crud.get_by_team_uuid(db, team_uuid)


@router.put("/{team_uuid}", response_model=Team, tags=["teams"])
def update_team(*,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user),
                team_uuid: uuid.UUID = Path(..., description="UUID of team"),
                team_update: TeamUpdate = Body(...,
                                               description="Contents to be updated")
                ):
    if not current_user:
        raise not_authorized()

    db_team = teams.crud.get(db, team_uuid)

    if not db_team:
        raise not_found("Team")

    check_adminship(db, current_user, team_uuid)

    db_team = teams.crud.update(db, db_obj=db_team, obj_in=team_update)
    return db_team


@router.delete("/{team_uuid}", response_model=Team, tags=["team"])
def delete_team(*,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db),
                team_uuid: uuid.UUID = Path(..., description="UUID of team")):
    if not current_user:
        raise not_authorized()

    db_team = teams.crud.get(db, team_uuid)

    if not db_team:
        raise not_found("Team")

    check_adminship(db, current_user, team_uuid)

    teams.crud.remove(db, uuid=team_uuid)

    return db_team


@router.get("/{team_uuid}/members", response_model=list[Membership])
def get_members(*,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db),
                team_uuid: uuid.UUID = Path(..., description="UUID of team")):
    if not current_user:
        raise not_authorized()

    db_team = teams.crud.get(db, team_uuid)

    if not db_team:
        raise not_found("Team")

    check_membership(db, current_user, team_uuid)

    db_memberships = memberships.crud.get_by_team_uuid(db, team_uuid)

    return db_memberships


# @router.get("/{team_uuid}/members/current", response_model=Membership)
# def get_current_member(*,
#                current_user: User = Depends(get_current_user),
#                db: Session = Depends(get_db),
#                team_uuid: uuid.UUID = Path(..., description="UUID of team")):
#     if not current_user:
#         raise not_authorized()
#
#     db_team = teams.crud.get(db, team_uuid)
#
#     if not db_team:
#         raise not_found("Team")
#
#     membership = check_membership(db, current_user, team_uuid)
#
#     if not membership:
#         raise not_found("Membership")
#
#     return membership


@router.get("/{team_uuid}/members/{user_uuid}", response_model=Membership)
def get_member(*,
               current_user: User = Depends(get_current_user),
               db: Session = Depends(get_db),
               team_uuid: uuid.UUID = Path(..., description="UUID of team"),
               user_uuid: uuid.UUID = Path(..., description="UUID of user")):
    if not current_user:
        raise not_authorized()

    db_team = teams.crud.get(db, team_uuid)

    if not db_team:
        raise not_found("Team")

    check_membership(db, current_user, team_uuid)

    membership = memberships.crud.get_by_team_user_uuid(db, user_uuid, team_uuid)

    if not membership:
        raise not_found("Membership")

    return membership


@router.put("/{team_uuid}/members/{user_uuid}", response_model=Membership)
def update_member(*,
                  current_user: User = Depends(get_current_user),
                  db: Session = Depends(get_db),
                  team_uuid: uuid.UUID = Path(..., description="UUID of team"),
                  user_uuid: uuid.UUID = Path(..., description="UUID of user"),
                  member_update: MembershipUpdate = Body(..., description="Content to be updated")):
    if not current_user:
        raise not_authorized()

    db_team = teams.crud.get(db, team_uuid)

    if not db_team:
        raise not_found("Team")

    check_adminship(db, current_user, team_uuid)

    db_membership = memberships.crud.get_by_team_user_uuid(db, user_uuid, team_uuid)

    if not db_membership:
        raise not_found("Membership")

    db_membership = memberships.crud.update(db, db_obj=db_membership, obj_in=member_update)

    return db_membership


@router.delete("/{team_uuid}/members/{user_uuid}", response_model=Membership)
def remove_member(*,
                  current_user: User = Depends(get_current_user),
                  db: Session = Depends(get_db),
                  team_uuid: uuid.UUID = Path(..., description="UUID of team"),
                  user_uuid: uuid.UUID = Path(..., description="UUID of user")):
    if not current_user:
        raise not_authorized()

    db_team = teams.crud.get(db, team_uuid)

    if not db_team:
        raise not_found("Team")

    if user_uuid != current_user.uuid:
        check_adminship(db, current_user, team_uuid)

    db_membership = memberships.crud.get_by_team_user_uuid(db, user_uuid, team_uuid)

    if not db_membership:
        raise not_found("Membership")

    memberships.crud.remove_by_team_user_uuid(db, user_uuid, team_uuid)

    return db_membership
