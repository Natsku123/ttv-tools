from sqlmodel import create_engine
from sqlalchemy.orm import sessionmaker

from config import settings
from core.database.models.all import (
    OAuth2Token,
    EventSubscription,
    Server,
    Team,
    User,
    Membership,
    TeamInvite
)

SQLALCHEMY_DATABASE_URL = "postgresql://{username}:{password}@{server}/{db}" \
    .format(
    username=settings.DATABASE_USER,
    password=settings.DATABASE_PASSWORD,
    server=settings.DATABASE_SERVER,
    db=settings.DATABASE_NAME
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)
