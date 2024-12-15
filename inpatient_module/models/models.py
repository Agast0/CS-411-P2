from typing import List, Optional
from datetime import date, datetime
from enum import Enum


class RoomType(Enum):
    SINGLE = "Single"
    DOUBLE = "Double"
    ICU = "ICU"


class Room:
    def __init__(self,
                 room_id: int,
                 type: RoomType,  # Enum for room type
                 is_occupied: bool):
        self.room_id = room_id
        self.type = type
        self.is_occupied = is_occupied

    def to_dict(self):
        return {
            "room_id": self.room_id,
            "type": self.type.value,  # Save the enum value as string
            "is_occupied": self.is_occupied,
        }

    @staticmethod
    def from_dict(data: dict):
        return Room(
            room_id=data["room_id"],
            type=RoomType(data["type"]),
            is_occupied=data["is_occupied"]
        )


class Inpatient:
    def __init__(self,
                 id: int,
                 patient_id: int,
                 admission_date: date,
                 discharge_date: Optional[date],
                 room_id: int,  # Ensure the argument is room_id
                 staff_id: int,
                 status: Optional[str] = None,
                 notes: Optional[List[str]] = None,
                 tests: Optional[List[int]] = None):
        self.id = id
        self.patient_id = patient_id
        self.admission_date = admission_date
        self.discharge_date = discharge_date
        self.room_id = room_id  # Assign room_id to the attribute
        self.staff_id = staff_id
        self.status = status
        self.notes = notes or []
        self.tests = tests or []

    def to_dict(self):
        if isinstance(self.admission_date, str):
            self.admission_date = datetime.strptime(self.admission_date, "%Y-%m-%d").date()

        if isinstance(self.discharge_date, str):
            if self.discharge_date:
                self.discharge_date = datetime.strptime(self.discharge_date, "%Y-%m-%d").date()
            else:
                self.discharge_date = None

        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "admission_date": self.admission_date.isoformat() if self.admission_date else None,
            "discharge_date": self.discharge_date.isoformat() if self.discharge_date else None,
            "room_id": self.room_id,
            "staff_id": self.staff_id,
            "status": self.status,
            "notes": self.notes,
            "tests": self.tests,
        }

    @staticmethod
    def from_dict(data: dict):
        return Inpatient(
            id=data["id"],
            patient_id=data["patient_id"],
            admission_date=date.fromisoformat(data["admission_date"]),
            discharge_date=date.fromisoformat(data["discharge_date"]) if data["discharge_date"] else None,
            room_id=data["room_id"],  # Ensure room_id is passed
            staff_id=data["staff_id"],
            status=data.get("status"),
            notes=data.get("notes", []),
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
