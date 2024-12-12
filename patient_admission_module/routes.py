from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from patient_admission_module.services.admission_service import AdmissionService
from patient_admission_module.models.models import Gender, Patient

admission_bp = Blueprint('admission', __name__, template_folder='templates', static_folder='static', url_prefix='/admission')
admission_service = AdmissionService()


# Patient Registration
@admission_bp.route('/register', methods=['GET', 'POST'])
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
def view_appointments(patient_id):
    patient = admission_service.get_patient(patient_id)
    if not patient:
        flash("Patient not found.", "error")
        return redirect(url_for('admission.register_patient'))

    appointments = admission_service.get_appointments_by_patient(patient_id)
    return render_template('view_appointments.html', patient=patient, appointments=appointments)

# Staff View Appointments
@admission_bp.route('/appointments/staff/<int:staff_id>', methods=['GET'])
def view_staff_appointments(staff_id):
    staff = admission_service.get_staff_by_id(staff_id)  # Assuming this method exists in AdmissionService
    if not staff:
        flash("Staff not found.", "error")
        return redirect(url_for('admission.view_all_patients'))

    appointments = admission_service.get_appointments_by_staff(staff_id)  # Assuming this method exists
    return render_template('view_staff_appointments.html', staff=staff, appointments=appointments)

# Staff View All Patients
@admission_bp.route('/patients', methods=['GET'])
def view_all_patients():
    search_query = request.args.get('search', '')  # Get search query from the URL
    patients = admission_service.get_all_patients(search_query)  # Pass search query to the service
    return render_template('staff_view_patients.html', patients=patients)


# Staff Create Appointment
@admission_bp.route('/appointment/create', methods=['GET', 'POST'])
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