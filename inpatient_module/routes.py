from flask import Blueprint, render_template, request, redirect, url_for, flash
from inpatient_module.services.inpatient_service import InpatientService

inpatient_bp = Blueprint('inpatient', __name__, template_folder='templates', url_prefix='/inpatient')
inpatient_service = InpatientService()

@inpatient_bp.route('/manage', methods=['GET', 'POST'])
def manage_inpatient():
    if request.method == 'POST':
        inpatient_data = {
            "patient_id": request.form['patient_id'],
            "room_number": request.form['room_number'],
            "status": request.form['status']
        }
        inpatient_service.add_inpatient(inpatient_data)
        flash("Inpatient added successfully!", "success")
        return redirect(url_for('inpatient.manage_inpatient'))
    return render_template('manage_inpatient.html')
