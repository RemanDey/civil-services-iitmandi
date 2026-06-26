import os
from pathlib import Path


def load_env_file(env_path=".env"):
    env_file = Path(env_path)
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if value and ((value[0] == value[-1] == '"') or (value[0] == value[-1] == "'")):
            value = value[1:-1]
        if key and key not in os.environ:
            os.environ[key] = value


load_env_file()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "a-random-secret")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///site.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = str(
        os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS", "False")
    ).lower() in ("1", "true", "t", "yes", "y")
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH", "")
