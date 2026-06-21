"""
Admin configuration file.
Copy this to config.py and run `python setup_admin.py` to generate credentials.
"""
import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-to-a-random-secret")
    SQLALCHEMY_DATABASE_URI = "sqlite:///site.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_USERNAME = "admin"
    # Generated with: python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your-password'))"
    ADMIN_PASSWORD_HASH = "scrypt:32768:8:1$..."
