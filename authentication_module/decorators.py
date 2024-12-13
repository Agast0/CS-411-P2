from functools import wraps
from flask import session, redirect, url_for, flash
from authentication_module.services.authentication import AuthenticationService

auth_service = AuthenticationService()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_info = auth_service.is_authenticated()
        if not auth_info.get("authenticated"):
            flash('You need to log in first.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def patient_required(f):
    """
    Ensure that the logged-in user is a patient.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_info = auth_service.is_authenticated()
        print(auth_info.get("role"))
        if not auth_info.get("authenticated"):
            flash('You need to log in first.', 'danger')
            return redirect(url_for('auth.login'))
        if auth_info.get("role") != 'patient':
            flash('You must be a patient to access this page.', 'danger')
            return redirect(url_for('auth.login_success'))  # Redirect to a page suitable for non-patients
        return f(*args, **kwargs)
    return decorated_function

def not_patient_required(f):
    """
    Ensure that the logged-in user is NOT a patient.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_info = auth_service.is_authenticated()
        if not auth_info.get("authenticated"):
            flash('You need to log in first.', 'danger')
            return redirect(url_for('auth.login'))
        if auth_info.get("role") == 'patient':
            flash('Patients cannot access this page.', 'danger')
            return redirect(url_for('auth.login_success'))  # Redirect to a page suitable for non-patients
        return f(*args, **kwargs)
    return decorated_function
