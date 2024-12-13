from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from authentication_module.decorators import login_required, not_patient_required
from patient_admission_module.services.admission_service import AdmissionService
from patient_admission_module.models.models import Gender, Patient

admission_bp = Blueprint('admission', __name__, template_folder='templates', static_folder='static', url_prefix='/admission')
admission_service = AdmissionService()


# Patient Registration
@admission_bp.route('/register', methods=['GET', 'POST'])
@login_required
@not_patient_required
def register_patient():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        date_of_birth = request.form['date_of_birth']
        gender = request.form['gender']  # assuming Gender is a string here
        contact_number = request.form['contact_number']
        email = request.form['email']

        # Add the patient to the service (and store in JSON)
        new_patient = admission_service.add_patient(first_name, last_name, date_of_birth, gender, contact_number, email)

        flash("Patient registered successfully!", "success")
        return redirect(url_for('admission.view_all_patients'))

    return render_template('patient_register.html', gender_choices=Gender)


@admission_bp.route('/patient/delete/<int:patient_id>', methods=['POST'])
@login_required
@not_patient_required
def delete_patient(patient_id):
    patient = admission_service.get_patient(patient_id)
    if not patient:
        flash("Patient not found.", "error")
        return redirect(url_for('admission.view_all_patients'))

    try:
        admission_service.delete_patient(patient_id)
        flash("Patient deleted successfully!", "success")
    except Exception as e:
        flash(str(e), "error")

    return redirect(url_for('admission.view_all_patients'))



# View Patient Appointments
@admission_bp.route('/appointments/<int:patient_id>', methods=['GET'])
@login_required
def view_appointments(patient_id):
    patient = admission_service.get_patient(patient_id)
    if not patient:
        flash("Patient not found.", "error")
        return redirect(url_for('admission.view_all_patients'))

    appointments = admission_service.get_appointments_by_patient(patient_id)
    user_role = session.get('user_role')
    return render_template('view_appointments.html', patient=patient, appointments=appointments, user_role=user_role)

# Staff View All Patients
@admission_bp.route('/patients', methods=['GET'])
@login_required
@not_patient_required
def view_all_patients():
    search_query = request.args.get('search', '')  # Get search query from the URL
    patients = admission_service.get_all_patients(search_query)  # Pass search query to the service
    return render_template('staff_view_patients.html', patients=patients)


# Staff Create Appointment
@admission_bp.route('/appointment/create', methods=['GET', 'POST'])
@login_required
@not_patient_required
def create_appointment():
    if request.method == 'POST':
        date = request.form['date']
        time = request.form['time']
        patient_id = int(request.form['patient_id'])
        staff_id = int(request.form['staff_id'])

        try:
            appointment = admission_service.create_appointment(date, time, patient_id, staff_id)
            flash("Appointment created successfully!", "success")
            return redirect(url_for('admission.view_appointments', patient_id=patient_id))
        except ValueError as e:
            flash(str(e), "error")
            return redirect(url_for('admission.create_appointment'))

    patients = admission_service.get_all_patients()
    staff_members = admission_service.staff_members
    return render_template('create_appointment.html', patients=patients, staff_members=staff_members)


# Staff Manage Patient
@admission_bp.route('/patient/manage/<int:patient_id>', methods=['GET', 'POST'])
@login_required
@not_patient_required
def manage_patient(patient_id):
    patient = admission_service.get_patient(patient_id)
    if not patient:
        return redirect(url_for('admission.view_all_patients'))

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        date_of_birth = request.form['date_of_birth']
        gender = request.form['gender']  # Assuming gender is sent as a string
        contact_number = request.form['contact_number']
        email = request.form['email']

        updated_patient = admission_service.update_patient(patient_id, first_name, last_name, date_of_birth, gender,
                                                           contact_number, email)
        flash("Patient updated successfully!", "success")
        return redirect(url_for('admission.view_all_patients'))

    return render_template('manage_patient.html', patient=patient, gender_choices=Gender)

# Cancel Appointment
@admission_bp.route('/appointment/cancel/<int:appointment_id>', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    appointment = admission_service.get_appointment(appointment_id)  # Assuming this method exists
    if not appointment:
        flash("Appointment not found.", "error")
        return redirect(url_for('admission.view_all_patients'))

    try:
        admission_service.cancel_appointment(appointment_id)
        flash("Appointment canceled successfully!", "success")
    except Exception as e:
        flash(f"Error canceling appointment: {str(e)}", "error")

    patient = admission_service.get_patient(appointment.patient_id)

    return redirect(url_for('admission.view_appointments', patient=patient, patient_id=appointment.patient_id))
