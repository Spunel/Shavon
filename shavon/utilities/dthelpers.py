from typing  import Optional
from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.types import TypeDecorator


def now(tzinfo: Optional[timezone] = timezone.utc) -> datetime:
    """
    Returns a timezone-aware datetime object representing the current time.
    If timezone isn't specified, defaults to UTC.

        tzinfo: Optional[tzinfo] = UTC,
    """
    return datetime.now(tzinfo)


def fromtimestamp(
    timestamp, 
    tzinfo: Optional[timezone] = timezone.utc
) -> datetime:
    """
    Returns a timezone-aware datetime object representing the given timestamp.
    If timezone isn't specified, defaults to UTC.
        
        timestamp: int or float,
        tzinfo: Optional[tzinfo] = UTC
    """
    return datetime.fromtimestamp(timestamp, tzinfo)


class TZDateTime(TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            if not value.tzinfo or value.tzinfo.utcoffset(value) is None:
                raise TypeError("tzinfo is required")
            value = value.astimezone(timezone.utc).replace(tzinfo=None)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = value.replace(tzinfo=timezone.utc)
        return value

