import uuid

from fastapi import APIRouter, Depends, Path, Body
from sqlmodel import Session

from core.deps import get_db, get_current_user
from core.database.models.users import User
from core.database.models.teams import Team, TeamUpdate, TeamCreate
from core.database.crud import teams
from core.database.crud import memberships

from core.routes import not_authorized, not_found, forbidden

router = APIRouter()


@router.get("/", response_model=list[str | Team], tags=["teams"])
def get_teams(*, db: Session = Depends(get_db), current_user: User | None = Depends(get_current_user)):
    if not current_user:
        return [team.name for team in teams.crud.get_multi(db)]
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


@router.put("/{team_uuid}", response_model=Team, tags=["teams"])
def update_team(*,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user),
                team_uuid: uuid.UUID = Path(..., description="UUID of team"),
                team_update: TeamUpdate = Body(..., description="Contents to be updated")
                ):
    if not current_user:
        raise not_authorized()

    mship = memberships.crud.get_by_team_user_uuid(db, current_user.uuid, team_uuid)

    if not current_user.is_superadmin and (mship is None or not mship.is_admin):
        raise forbidden()

    db_team = teams.crud.get(db, team_uuid)

    if not db_team:
        raise not_found("Team")

    db_team = teams.crud.update(db, db_obj=db_team, obj_in=team_update)
    return db_team


@router.delete("/{team_uuid}", response_model=Team, tags=["team"])
def delete_team(*,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db),
                team_uuid: uuid.UUID = Path(..., description="UUID of team")):
    if not current_user:
        raise not_authorized()

    mship = memberships.crud.get_by_team_user_uuid(db, current_user.uuid, team_uuid)

    if not current_user.is_superadmin and (mship is None or not mship.is_admin):
        raise forbidden()

    db_team = teams.crud.get(db, team_uuid)

    if not db_team:
        raise not_found("Team")

    teams.crud.remove(db, team_uuid)

    return db_team
