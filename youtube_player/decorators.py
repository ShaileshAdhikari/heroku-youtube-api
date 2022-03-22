from functools import wraps
from flask import session, jsonify

def logged_in(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        return f(*args, **kwargs) if session.get("logged_in") \
            else jsonify({
            'success': False,
            'result': {'error': 'You are not logged in'}
        }),401
    return decorated_func