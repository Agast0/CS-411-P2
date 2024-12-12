from functools import wraps
from flask import session, redirect, url_for, flash
from authentication_module.services.authentication import AuthenticationService

auth_service = AuthenticationService()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not auth_service.is_authenticated():
            flash('You need to log in first.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
