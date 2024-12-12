from enum import Enum
from typing import List, Optional
from datetime import date, datetime


class Gender(Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class Role(Enum):
    RECEPTIONIST = "Receptionist"
    ADMIN = "Admin"
    DOCTOR = "Doctor"
    OTHER = "Other"


class Patient:
    def __init__(self,
                 id: int,
                 first_name: str,
                 last_name: str,
                 date_of_birth: str,  # Ensure this is a string or datetime object
                 gender: str,
                 contact_number: str,
                 email: str,
                 appointments: List['Appointment'] = None):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.contact_number = contact_number
        self.email = email
        self.appointments = appointments or []

    # In Patient class
    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "date_of_birth": self.date_of_birth,
            "gender": self.gender,
            "contact_number": self.contact_number,
            "email": self.email,
            "appointments": [appointment.to_dict() for appointment in self.appointments],
        }

    @staticmethod
    def from_dict(data: dict):
        patient = Patient(
            id=data["id"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            date_of_birth=datetime.fromisoformat(data["date_of_birth"]),  # Convert string back to datetime
            gender=data["gender"],
            contact_number=data["contact_number"],
            email=data["email"]
        )
        return patient


class Staff:
    def __init__(self,
                 id: int,
                 first_name: str,
                 last_name: str,
                 role: Role,
                 email: str,
                 contact_number: str,
                 appointments: List['Appointment'] = None):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
        self.email = email
        self.contact_number = contact_number
        self.appointments = appointments or []

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "role": self.role.value,
            "email": self.email,
            "contact_number": self.contact_number,
            "appointments": [appointment.to_dict() for appointment in self.appointments],
        }

    @staticmethod
    def from_dict(data: dict):
        staff = Staff(
            id=data["id"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            role=Role(data["role"]),
            email=data["email"],
            contact_number=data["contact_number"]
        )
        return staff


class Appointment:
    def __init__(self,
                 id: int,
                 date: str,
                 time: str,
                 patient_id: int,
                 staff_id: int):
        self.id = id
        self.date = date
        self.time = time
        self.patient_id = patient_id
        self.staff_id = staff_id

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date,
            "time": self.time,
            "patient_id": self.patient_id,
            "staff_id": self.staff_id,
        }

    @staticmethod
    def from_dict(data: dict):
        return Appointment(
            id=data["id"],
            date=data["date"],
            time=data["time"],
            patient_id=data["patient_id"],
            staff_id=data["staff_id"]
        )