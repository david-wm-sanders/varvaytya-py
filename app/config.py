import os
import pathlib

APP_DIR = pathlib.Path(__file__).parent


class ConfigurationError(Exception):
    """Exception raised if a variable was required and not in environment."""

    pass


class Config:
    # Load app SECRET_KEY so that tools, such as CSRF protection, are usable
    SECRET_KEY = os.environ.get("SECRET_KEY")
    if not SECRET_KEY:
        raise ConfigurationError("No 'SECRET_KEY' set")

    # Load DATABASE_URI from environment or use a sqlite db if environment variable is not set
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI") or f"sqlite:///{APP_DIR / 'app.db'}"

    # Disable app signalling on db changes
    SQLALCHEMY_TRACK_MODIFICATIONS = False
