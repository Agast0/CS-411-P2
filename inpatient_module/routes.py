from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from inpatient_module.services.inpatient_service import InpatientService

# Blueprint setup for the inpatient module
inpatient_bp = Blueprint(
    'inpatient',
    __name__,
    template_folder='templates',
    url_prefix='/inpatient'
)

# Service instance for handling business logic
inpatient_service = InpatientService()


# Endpoint to manage inpatients (view all, add, edit, delete)
@inpatient_bp.route('/manage', methods=['GET', 'POST'])
def manage_inpatient():
    if request.method == 'POST':
        try:
            # Validate and process input data
            inpatient_data = {
                "patient_id": request.form.get('patient_id', '').strip(),
                "room_id": request.form.get('room_id', '').strip(),
                "status": request.form.get('status', '').strip()
            }

            # Check for missing or invalid data
            if not inpatient_data['patient_id']:
                flash("Patient ID is required!", "danger")
                return redirect(url_for('inpatient.manage_inpatient'))

            if not inpatient_data['room_id']:
                flash("Room number is required!", "danger")
                return redirect(url_for('inpatient.manage_inpatient'))

            if not inpatient_data['status']:
                flash("Status is required!", "danger")
                return redirect(url_for('inpatient.manage_inpatient'))

            # Call the service layer to add inpatient
            inpatient_service.add_inpatient(inpatient_data)

            # Flash success message and redirect
            flash("Inpatient added successfully!", "success")
            return redirect(url_for('inpatient.manage_inpatient'))

        except Exception as e:
            # Log the error and display a user-friendly message
            print(f"Error adding inpatient: {e}")
            flash("An error occurred while adding the inpatient. Please try again.", "danger")
            return redirect(url_for('inpatient.manage_inpatient'))

    # GET request: Render the inpatient management form
    inpatients = inpatient_service.get_all_inpatients()
    rooms = inpatient_service.get_all_rooms()
    return render_template('manage_inpatient.html', inpatients=inpatients, rooms=rooms)


# Endpoint to view details of a single inpatient
@inpatient_bp.route('/<int:inpatient_id>')
def view_inpatient(inpatient_id):
    inpatient = inpatient_service.get_inpatient(inpatient_id)
    return render_template('view_inpatient.html', inpatient=inpatient)


# Endpoint to view details of a single room
@inpatient_bp.route('/room/<int:room_id>')
def view_room(room_id):
    room_inpatients = inpatient_service.get_inpatients_by_room(room_id)
    return render_template('view_room.html', room_id=room_id, inpatients=room_inpatients)


# Endpoint to assign/update a room for an inpatient
@inpatient_bp.route('/<int:inpatient_id>/assign-room', methods=['POST'])
def assign_room(inpatient_id):
    try:
        room_id = request.form.get('room_id')  # Fetch 'room_id' from form data
        if not room_id:
            return jsonify({"error": "Room number is required."}), 400

        # Call the service to change the room assignment
        inpatient_service.change_room(inpatient_id, room_id)

        flash("Patient registered successfully!", "success")

    except Exception as e:
        print(f"Error updating room: {e}")
        flash(str(e), "error")

    return redirect(url_for('inpatient.view_inpatient', inpatient_id=inpatient_id))



# Endpoint to add notes for an inpatient
@inpatient_bp.route('/<int:inpatient_id>/notes', methods=['POST'])
def add_notes(inpatient_id):
    try:
        data = request.json
        note = data.get('note')

        if not note:
            return jsonify({"error": "Note content is required."}), 400

        inpatient_service.add_notes(inpatient_id, note)
        return jsonify({"message": "Note added successfully."}), 201

    except Exception as e:
        print(f"Error adding note: {e}")
        return jsonify({"error": "Failed to add note."}), 500


# Endpoint to add treatment notes for an inpatient
@inpatient_bp.route('/<int:inpatient_id>/add-treatment-notes', methods=['POST'])
def add_treatment_notes(inpatient_id):
    try:
        data = request.form
        treatment_note = data.get('treatment_note')

        if not treatment_note:
            flash("Treatment note is required!", "danger")
            return redirect(url_for('inpatient.view_inpatient', inpatient_id=inpatient_id))

        inpatient_service.add_treatment_notes(inpatient_id, treatment_note)
        flash("Treatment note added successfully!", "success")
        return redirect(url_for('inpatient.view_inpatient', inpatient_id=inpatient_id))

    except Exception as e:
        print(f"Error adding treatment note: {e}")
        flash("Failed to add treatment note. Please try again.", "danger")
        return redirect(url_for('inpatient.view_inpatient', inpatient_id=inpatient_id))


@inpatient_bp.route('/<int:inpatient_id>/change_status', methods=['POST'])
def change_status(inpatient_id):
    """Change the status of an inpatient."""
    data = request.json
    new_status = data.get('status')
    if not new_status:
        return jsonify({'error': 'Status is required.'}), 400

    try:
        updated_inpatient = inpatient_service.change_status(inpatient_id, new_status)
        return jsonify(updated_inpatient.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404


@inpatient_bp.route('/<int:inpatient_id>/discharge', methods=['POST'])
def discharge(inpatient_id):
    try:
        inpatient = inpatient_service.discharge_inpatient(inpatient_id)
        if inpatient:
            flash(f"Patient with ID {inpatient_id} has been discharged.", "success")
            return redirect(url_for('inpatient.view_inpatient', inpatient_id=inpatient_id))
        else:
            flash("Inpatient not found.", "danger")
            return redirect(url_for('inpatient.view_inpatient', inpatient_id=inpatient_id))
    except Exception as e:
        print(f"Error discharging inpatient: {e}")
        flash("An error occurred while discharging the patient. Please try again.", "danger")
        return redirect(url_for('inpatient.view_inpatient', inpatient_id=inpatient_id))


# Endpoint to remove an inpatient
@inpatient_bp.route('/<int:inpatient_id>/remove', methods=['POST'])
def remove(inpatient_id):
    try:
        # Attempt to delete the inpatient
        success = inpatient_service.delete_inpatient(inpatient_id)

        if not success:
            flash("Inpatient not found or could not be removed.", "danger")
            return redirect(url_for('inpatient.manage_inpatient'))

        flash("Inpatient removed successfully!", "success")
        return redirect(url_for('inpatient.manage_inpatient'))

    except Exception as e:
        print(f"Error removing inpatient: {e}")
        flash("An error occurred while removing the inpatient. Please try again.", "danger")
        return redirect(url_for('inpatient.manage_inpatient'))


@inpatient_bp.route('/<int:inpatient_id>/add_test', methods=['POST'])
def add_test(inpatient_id):
    test_type = request.form.get('test_type')
    staff_id = request.form.get('staff_id')
    test_date = request.form.get('test_date')
    result = request.form.get('result')

    if not test_type or not staff_id or not test_date:
        flash("All fields are required.", "danger")
        return redirect(url_for('inpatient.view_inpatient', inpatient_id=inpatient_id))

    try:
        # Parse test_date into a date object
        test_date = date.fromisoformat(test_date)

        # Call the service to add the test
        success = inpatient_service.add_test(
            inpatient_id=inpatient_id,
            test_type=test_type,
            staff_id=int(staff_id),
            test_date=test_date,
            result=result
        )

        if not success:
            flash("Inpatient not found or test could not be added.", "danger")
            return redirect(url_for('inpatient.view_inpatient', inpatient_id=inpatient_id))

        flash(f"Test '{test_type}' added successfully!", "success")
        return redirect(url_for('inpatient.view_inpatient', inpatient_id=inpatient_id))

    except Exception as e:
        print(f"Error adding test: {e}")
        flash("An error occurred while adding the test. Please try again.", "danger")
        return redirect(url_for('inpatient.view_inpatient', inpatient_id=inpatient_id))
