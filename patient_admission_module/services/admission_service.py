import json
from datetime import date, datetime
from typing import Optional, List

from patient_admission_module.models.models import Patient, Gender, Appointment, Staff


class AdmissionService:
    def __init__(self):
        self.patients_file_path = 'patient_admission_module/models/data/patients.json'
        self.appointments_file_path = 'patient_admission_module/models/data/appointments.json'
        self.staff_file_path = 'patient_admission_module/models/data/staff.json'

        self.patients = self.load_data(self.patients_file_path)
        self.appointments = self.load_data(self.appointments_file_path)
        self.staff_members = self.load_data(self.staff_file_path)

        self.next_patient_id = self.get_next_id(self.patients)
        self.next_appointment_id = self.get_next_id(self.appointments)
        self.next_staff_id = self.get_next_id(self.staff_members)

    def load_data(self, file_path: str):
        """Load data from a JSON file"""
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def save_data(self, file_path: str, data: List[dict]):
        """Save data to a JSON file"""
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def get_next_id(self, data: List[dict]) -> int:
        """Get the next available ID by finding the max ID in the data."""
        if data:
            return max(item['id'] for item in data) + 1
        return 1

    # Patient Operations
    def add_patient(self, first_name: str, last_name: str, date_of_birth: str, gender: str, contact_number: str, email: str) -> Patient:
        patient = Patient(
            id=self.next_patient_id,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            gender=gender,
            contact_number=contact_number,
            email=email
        )
        self.next_patient_id += 1

        self.patients.append(patient.to_dict())  # Append new patient to the list
        self.save_data(self.patients_file_path, self.patients)  # Save the updated list to file

        return patient

    def get_patient(self, patient_id: int) -> Optional[Patient]:
        for patient in self.patients:
            if patient['id'] == patient_id:
                return Patient(**patient)
        return None

    def get_all_patients(self, search_query: str = '') -> List[Patient]:
        # Convert all patient records, and filter if search_query is provided
        filtered_patients = [
            patient for patient in self.patients
            if search_query.lower() in patient['first_name'].lower() or
               search_query.lower() in patient['last_name'].lower() or
               search_query.lower() in patient['email'].lower()
        ]

        return [Patient(**patient) for patient in filtered_patients]

    def update_patient(self, patient_id: int, first_name: Optional[str] = None, last_name: Optional[str] = None,
                       date_of_birth: Optional[date] = None, gender: Optional[Gender] = None,
                       contact_number: Optional[str] = None, email: Optional[str] = None) -> Optional[Patient]:
        patient = self.get_patient(patient_id)
        if patient:
            patient.first_name = first_name or patient.first_name
            patient.last_name = last_name or patient.last_name
            patient.date_of_birth = date_of_birth or patient.date_of_birth
            patient.gender = gender or patient.gender
            patient.contact_number = contact_number or patient.contact_number
            patient.email = email or patient.email

            # Update the patient in the list and save
            for i, p in enumerate(self.patients):
                if p['id'] == patient_id:
                    self.patients[i] = patient.to_dict()  # Ensure to_dict() converts the Patient to a dict format
            self.save_data(self.patients_file_path, self.patients)

        return patient

    def delete_patient(self, patient_id: int) -> bool:
        patient = self.get_patient(patient_id)
        if patient:
            self.patients = [p for p in self.patients if p['id'] != patient_id]
            self.appointments = [appt for appt in self.appointments if appt['patient_id'] != patient_id]
            self.save_data(self.patients_file_path, self.patients)
            self.save_data(self.appointments_file_path, self.appointments)
            return True
        return False

    # Staff Operations
    def get_staff(self, staff_id: int) -> Optional[Staff]:
        for staff in self.staff_members:
            if staff['id'] == staff_id:
                return Staff(**staff)
        return None

    # Appointment Operations
    def create_appointment(self, date: date, time: str, patient_id: int, staff_id: int) -> Optional[Appointment]:
        patient = self.get_patient(patient_id)
        staff = self.get_staff(staff_id)

        if not patient:
            raise ValueError(f"Patient with ID {patient_id} does not exist.")
        if not staff:
            raise ValueError(f"Staff with ID {staff_id} does not exist.")

        appointment = Appointment(
            id=self.next_appointment_id,
            date=date,
            time=time,
            patient_id=patient_id,
            staff_id=staff_id
        )
        self.next_appointment_id += 1

        self.appointments.append(appointment.to_dict())  # Append new appointment
        self.save_data(self.appointments_file_path, self.appointments)  # Save updated appointments

        # Optionally, you can add the appointment to the patient and staff lists as well
        return appointment

    def get_appointment(self, appointment_id: int) -> Optional[Appointment]:
        for appointment in self.appointments:
            if appointment['id'] == appointment_id:
                return Appointment(**appointment)
        return None

    def update_appointment(self, appointment_id: int, date: Optional[date] = None, time: Optional[str] = None,
                           patient_id: Optional[int] = None, staff_id: Optional[int] = None) -> Optional[Appointment]:
        appointment = self.get_appointment(appointment_id)
        if appointment:
            appointment.date = date or appointment.date
            appointment.time = time or appointment.time
            if patient_id and self.get_patient(patient_id):
                appointment.patient_id = patient_id
            if staff_id and self.get_staff(staff_id):
                appointment.staff_id = staff_id

            # Update the appointment in the list and save
            for i, appt in enumerate(self.appointments):
                if appt['id'] == appointment_id:
                    self.appointments[i] = appointment.to_dict()
            self.save_data(self.appointments_file_path, self.appointments)

        return appointment

    def delete_appointment(self, appointment_id: int) -> bool:
        appointment = self.get_appointment(appointment_id)
        if appointment:
            self.appointments = [appt for appt in self.appointments if appt['id'] != appointment_id]
            self.save_data(self.appointments_file_path, self.appointments)
            return True
        return False

    def get_appointments_by_patient(self, patient_id: int) -> List[Appointment]:
        return [Appointment(**appointment) for appointment in self.appointments if appointment['patient_id'] == patient_id]

    def get_appointments_by_staff(self, staff_id: int) -> List[Appointment]:
        return [Appointment(**appointment) for appointment in self.appointments if appointment['staff_id'] == staff_id]