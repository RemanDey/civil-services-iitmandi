from flask import Blueprint, session, redirect, url_for
from functools import wraps

admin_bp = Blueprint("admin", __name__, url_prefix="/admin", template_folder="templates")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin.login"))
        return f(*args, **kwargs)
    return decorated_function


from admin import routes
