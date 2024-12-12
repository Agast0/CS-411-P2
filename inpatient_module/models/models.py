from typing import List, Optional
from datetime import date
from enum import Enum


class RoomType(Enum):
    SINGLE = "Single"
    DOUBLE = "Double"
    ICU = "ICU"


class Room:
    def __init__(self,
                 id: int,
                 number: str,
                 type: RoomType,  # Enum for room type
                 is_occupied: bool):
        self.id = id
        self.number = number
        self.type = type
        self.is_occupied = is_occupied

    def to_dict(self):
        return {
            "id": self.id,
            "number": self.number,
            "type": self.type.value,  # Save the enum value as string
            "is_occupied": self.is_occupied,
        }

    @staticmethod
    def from_dict(data: dict):
        return Room(
            id=data["id"],
            number=data["number"],
            type=RoomType(data["type"]),
            is_occupied=data["is_occupied"]
        )


class InpatientRecord:
    def __init__(self,
                 id: int,
                 patient_id: int,
                 admission_date: date,
                 discharge_date: Optional[date],
                 room_id: int,
                 staff_id: int,  # Refers to staff handling the patient
                 treatment_notes: Optional[str] = None,
                 tests: Optional[List[int]] = None):  # List of test IDs
        self.id = id
        self.patient_id = patient_id
        self.admission_date = admission_date
        self.discharge_date = discharge_date
        self.room_id = room_id
        self.staff_id = staff_id
        self.treatment_notes = treatment_notes
        self.tests = tests or []  # Initialize as an empty list if not provided

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "admission_date": self.admission_date.isoformat(),
            "discharge_date": self.discharge_date.isoformat() if self.discharge_date else None,
            "room_id": self.room_id,
            "staff_id": self.staff_id,
            "treatment_notes": self.treatment_notes,
            "tests": self.tests,
        }

    @staticmethod
    def from_dict(data: dict):
        return InpatientRecord(
            id=data["id"],
            patient_id=data["patient_id"],
            admission_date=date.fromisoformat(data["admission_date"]),
            discharge_date=date.fromisoformat(data["discharge_date"]) if data["discharge_date"] else None,
            room_id=data["room_id"],
            staff_id=data["staff_id"],
            treatment_notes=data.get("treatment_notes"),
            tests=data.get("tests", [])
        )


class Test:
    def __init__(self,
                 id: int,
                 patient_id: int,
                 staff_id: int,  # Refers to staff handling the test
                 test_type: str,  # e.g., "Blood Test", "MRI"
                 date: date,
                 result: Optional[str] = None):
        self.id = id
        self.patient_id = patient_id
        self.staff_id = staff_id
        self.test_type = test_type
        self.date = date
        self.result = result

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "staff_id": self.staff_id,
            "test_type": self.test_type,
            "date": self.date.isoformat(),
            "result": self.result,
        }

    @staticmethod
    def from_dict(data: dict):
        return Test(
            id=data["id"],
            patient_id=data["patient_id"],
            staff_id=data["staff_id"],
            test_type=data["test_type"],
            date=date.fromisoformat(data["date"]),
            result=data.get("result")
        )
