from flask import Blueprint, render_template, request, redirect, url_for, flash, session, get_flashed_messages
from authentication_module.services.authentication import AuthenticationService
from authentication_module.decorators import login_required

auth_bp = Blueprint('auth', __name__, template_folder='templates', static_folder='static', url_prefix='/auth')

auth_service = AuthenticationService()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']


        if auth_service.login(username, password):
            session.pop('_flashes', None)
            session['user_authenticated'] = True  # Set session variable
            return redirect(url_for('auth.login_success'))
        else:
            flash('Invalid credentials', 'danger')

    return render_template('login.html')

@auth_bp.route('/login/success', methods=['GET'])
@login_required
def login_success():
    if not session.get('user_authenticated'):
        flash('You need to log in first.', 'danger')
        return redirect(url_for('auth.login'))
    return render_template('login_success.html')

@auth_bp.route('/logout', methods=  ['GET'])
@login_required
def logout():
    session.pop('user_authenticated', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))
