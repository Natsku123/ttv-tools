import datetime
import pytz

from config import settings


def timezoned() -> datetime.datetime:
    return datetime.datetime.now().astimezone(pytz.timezone(settings.TIME_ZONE))


# Based on Postgres and MySQL
INTEGER_SIZE = 2147483647
