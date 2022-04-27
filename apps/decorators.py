from functools import wraps
from flask import render_template
from flask_login import current_user


def check_for_admin(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        return f(*args, **kwargs) if current_user.email == 'admin@admin.com' \
            else render_template("home/not-admin.html")

    return decorated_func
