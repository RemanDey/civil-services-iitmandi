"""
Admin configuration file.
Copy this to config.py if you need local defaults, then create a `.env` file for secrets and credentials.
"""
import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-to-a-random-secret")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///site.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = str(
        os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS", "False")
    ).lower() in ("1", "true", "t", "yes", "y")
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH", "")
