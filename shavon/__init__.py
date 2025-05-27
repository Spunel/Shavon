
from shavon import settings
from shavon.utilities import dbhelpers

# Setup database
db = dbhelpers.AsyncDatabaseConnection(
    driver=settings.DB_CONNECT_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    echo=settings.SQL_ECHO
)
