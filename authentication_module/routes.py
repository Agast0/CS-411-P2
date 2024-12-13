from flask import Blueprint, render_template, request, redirect, url_for, flash, session, get_flashed_messages
from authentication_module.services.authentication import AuthenticationService
from authentication_module.decorators import login_required, not_patient_required, patient_required

auth_bp = Blueprint('auth', __name__, template_folder='templates', static_folder='static', url_prefix='/auth')

auth_service = AuthenticationService()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        auth_result = auth_service.login(username, password)

        if auth_result["authenticated"]:
            session.pop('_flashes', None)
            session['username'] = username
            session['user_authenticated'] = True
            session['user_role'] = auth_result["role"]  # Store the user's role in the session
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
    user_role = session.get('user_role')
    return render_template('login_success.html', user_role=user_role)

@auth_bp.route('/logout', methods=  ['GET'])
@login_required
def logout():
    session.pop('user_authenticated', None)
    session.pop('username', None)
    session.pop('user_role', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/patient-login', methods=['GET', 'POST'])
@login_required
@patient_required
def patient_login():
    if request.method == 'POST':
        patient_id = request.form['patient_id']
        entered_password = request.form['password']

        # Fetch the username (patient ID) and password from the session
        username = session.get('username')

        # Verify the entered password
        if auth_service.login(username, entered_password)["authenticated"]:
            # If password is correct, redirect to the patient's appointments
            return redirect(url_for('admission.view_appointments', patient_id=patient_id))
        else:
            # If password is incorrect, show a flash message
            flash('Invalid password. Please try again.', 'danger')

    return render_template('patient_login.html')