from functools import wraps
from flask import session, jsonify, redirect


def logged_in(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        return f(*args, **kwargs) if session.get("logged_in") \
            else redirect("/auth/login")
        #     jsonify({
        #     'success': False,
        #     'result': {'error': 'You are not logged in'}
        # })
    return decorated_func