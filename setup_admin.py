"""Generate admin config for the admin panel."""
from pathlib import Path
from werkzeug.security import generate_password_hash

username = input("Admin username [admin]: ").strip() or "admin"
password = input("Admin password: ").strip()
while not password:
    password = input("Admin password (cannot be empty): ").strip()

secret = input("Flask secret key (leave blank for auto-generated): ").strip()
if not secret:
    import secrets
    secret = secrets.token_hex(32)

hash_str = generate_password_hash(password)

content = f'''SECRET_KEY="{secret}"
SQLALCHEMY_DATABASE_URI=sqlite:///site.db
SQLALCHEMY_TRACK_MODIFICATIONS=False
ADMIN_USERNAME="{username}"
ADMIN_PASSWORD_HASH="{hash_str}"
'''

Path(".env").write_text(content)

print(".env created successfully!")
print(f"Username: {username}")
print("You can now run the app and log in at /admin/login")
