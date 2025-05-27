from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv(override=True)

# Import blueprints
from shavon.blueprints import BLUEPRINTS_ENABLED

# Application settings
APP_NAME = os.getenv("APP_NAME", "Shavon")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_HOST = os.getenv("APP_HOST", "localhost")
APP_PORT = int(os.getenv("APP_PORT", 8000))
APP_DEBUG = os.getenv("APP_DEBUG", "false").lower() == "true"

# Database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "default_db")

# SQLAlchemy settings
SQL_ECHO = os.getenv("SQL_ECHO", "false").lower() == "true"
DB_DRIVER = "postgresql+asyncpg"
DB_CONNECT_URL = f"{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", 5))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", 10))

# Template settings
TEMPLATE_PATH = os.getenv("TEMPLATE_PATH", "./shavon/templates")


# Cookie configurations
# COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN", "localhost")
# COOKIE_EXPIRATION = int(os.getenv("COOKIE_EXPIRATION", 3600))  # in seconds
# JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_jwt_secret_key")
# JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# Safe Settings (available to templates)
SAFE_SETTINGS = {
    "APP_NAME": APP_NAME,
    "APP_VERSION": APP_VERSION,
}