import json
from typing import List, Optional
from datetime import date, datetime
from patient_admission_module.services.admission_service import AdmissionService
from inpatient_module.models.models import Inpatient, Room, Test


class InpatientService:
    def __init__(self):
        self.admission_service = AdmissionService()  # Initialize AdmissionService to validate patient IDs
        self.inpatients_file_path = 'inpatient_module/models/data/inpatient_records.json'
        self.rooms_file_path = 'inpatient_module/models/data/rooms.json'
        self.inpatients = self.load_data(self.inpatients_file_path)
        self.rooms = self.load_data(self.rooms_file_path)
        self.tests = self.load_data('inpatient_module/models/data/tests.json')
        self.next_inpatient_id = self.get_next_id(self.inpatients)

    def load_data(self, file_path: str):
        """Load data from a JSON file"""
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def save_data(self, file_path: str, data: List[dict]):
        """Save data to a JSON file"""
        json.dump(data, file, indent=4)

    def get_next_id(self, data: List[dict]) -> int:
        """Get the next available ID by finding the max ID in the data."""
        print("Loaded inpatient data:", data)  # Debugging line to inspect the data
        max_id = 0
        for item in data:
            try:
                max_id = max(max_id, item['id'])
            except KeyError:
                continue  # Skip items without the 'id' key
        return max_id + 1 if max_id > 0 else 1

    def get_inpatients_by_room(self, room_id: str) -> List[Inpatient]:
        """
        Get all inpatients assigned to a specific room.
        :param room_id: The ID of the room.
        :return: A list of Inpatient objects assigned to the room.
        """
        inpatients_in_room = [
            Inpatient(**inpatient) for inpatient in self.inpatients if inpatient['room_id'] == room_id
        ]
        return inpatients_in_room

    def add_inpatient(self, patient_id: int, room_id: str, status: str) -> Optional[Inpatient]:
        """Add an inpatient if the patient ID is valid."""
        # Validate that the patient ID exists using the AdmissionService
        patient = self.admission_service.get_patient(patient_id)
        if not patient:
            raise ValueError(f"Patient with ID {patient_id} does not exist.")

        # Proceed with adding the inpatient
        inpatient = Inpatient(
            id=self.next_inpatient_id,
            patient_id=patient_id,
            room_id=room_id,
            status=status,
            admission_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        self.next_inpatient_id += 1
        self.inpatients.append(inpatient.to_dict())  # Append the new inpatient to the list
        self.save_data(self.inpatients_file_path, self.inpatients)  # Save updated list to file

        return inpatient

    def get_inpatient(self, inpatient_id: int) -> Optional[Inpatient]:
        """Get an inpatient by their ID, including their actual tests."""
        for inpatient in self.inpatients:
            if inpatient['id'] == inpatient_id:
                # Create the Inpatient object
                inpatient_obj = Inpatient(**inpatient)

                # Assuming there's a separate collection of tests stored in self.tests
                if 'tests' in inpatient:
                    # Replace foreign key IDs with actual Test objects
                    inpatient_obj.tests = []
                    for test_data in inpatient['tests']:
                        # Print test_data to debug
                        print(test_data)

                        # Check if test_data is an integer (i.e., a test ID)
                        if isinstance(test_data, int):
                            # If it's just a test ID, fetch the corresponding test details from the database or storage
                            test_data = self.get_test_by_id(test_data)  # Assuming you have a method to fetch the test

                        # Now, test_data should be a dictionary, and we can call from_dict safely
                        if isinstance(test_data, Test):
                            test_data = test_data.to_dict()  # Convert it to a dictionary if it's already a Test object

                        test_obj = Test.from_dict(test_data)

                        inpatient_obj.tests.append(test_obj)

                return inpatient_obj

        return None

    def get_test_by_id(self, test_id: int) -> dict:
        """Retrieve test data by its ID."""
        for test in self.tests:
            if test['id'] == test_id:
                return test
        return {}  # Return an empty dictionary if the test ID is not found

    def get_all_inpatients(self) -> List[Inpatient]:
        """Get all inpatients."""
        return [Inpatient(**inpatient) for inpatient in self.inpatients]

    def update_inpatient(self, inpatient_id: int, room_id: Optional[str] = None, status: Optional[str] = None) -> \
            Optional[Inpatient]:
        """Update inpatient details."""
        inpatient = self.get_inpatient(inpatient_id)
        if inpatient:
            inpatient.room_id = room_id or inpatient.room_id
            inpatient.status = status or inpatient.status

            # Update the inpatient record and save
            for i, inp in enumerate(self.inpatients):
                if inp['id'] == inpatient_id:
                    self.inpatients[i] = inpatient.to_dict()
            self.save_data(self.inpatients_file_path, self.inpatients)

        return inpatient

    def delete_inpatient(self, inpatient_id: int) -> bool:
        """Delete an inpatient record."""
        inpatient = self.get_inpatient(inpatient_id)
        if inpatient:
            self.inpatients = [inp for inp in self.inpatients if inp['id'] != inpatient_id]
            self.save_data(self.inpatients_file_path, self.inpatients)
            return True
        return False

    def get_all_rooms(self) -> List[Room]:
        """Get all rooms."""
        # Assuming rooms are stored in a list of dicts, convert each dict to a Room object.
        print("Rooms:", self.rooms)  # Debugging line to inspect the rooms data
        return [Room(**room) for room in self.rooms]

    def add_treatment_notes(self, inpatient_id: int, treatment_note: str):
        """Add treatment notes to an inpatient's record."""
        inpatient = self.get_inpatient(inpatient_id)
        if not inpatient:
            raise ValueError(f"Inpatient with ID {inpatient_id} does not exist.")

        if not hasattr(inpatient, 'treatment_notes') or inpatient.treatment_notes is None:
            inpatient.treatment_notes = []

        inpatient.treatment_notes.append(treatment_note)

        for i, inp in enumerate(self.inpatients):
            if inp['id'] == inpatient_id:
                self.inpatients[i] = inpatient.to_dict()
        self.save_data(self.inpatients_file_path, self.inpatients)

    def change_status(self, inpatient_id: int, new_status: str) -> Optional[Inpatient]:
        inpatient = self.get_inpatient(inpatient_id)
        if not inpatient:
            raise ValueError(f"Inpatient with ID {inpatient_id} does not exist.")

        inpatient.status = new_status

        for i, inp in enumerate(self.inpatients):
            if inp['id'] == inpatient_id:
                self.inpatients[i] = inpatient.to_dict()
        self.save_data(self.inpatients_file_path, self.inpatients)

        return inpatient

    def discharge_inpatient(self, inpatient_id: int) -> Optional[Inpatient]:
        inpatient = self.get_inpatient(inpatient_id)
        if inpatient:
            inpatient.status = 'discharged'

            # Update the inpatient record and save
            for i, inp in enumerate(self.inpatients):
                if inp['id'] == inpatient_id:
                    self.inpatients[i] = inpatient.to_dict()
            self.save_data(self.inpatients_file_path, self.inpatients)

            return inpatient
        return None

    def add_test(self, inpatient_id: int, test_type: str, staff_id: int, test_date: date,
                 result: Optional[str] = None) -> bool:
        """Add a test to an inpatient's record."""
        inpatient = self.get_inpatient(inpatient_id)
        if inpatient:
            # Create a new Test object
            test_id = self.generate_test_id()  # Assume there's a method to generate unique test IDs
            new_test = Test(
                id=test_id,
                patient_id=inpatient_id,
                staff_id=staff_id,
                test_type=test_type,
                date=test_date,
                result=result
            )

            # Add the test to the inpatient's record (assuming tests are stored in a list)
            if 'tests' not in inpatient:
                inpatient['tests'] = []  # Initialize the tests list if not already present

            inpatient['tests'].append(new_test.to_dict())  # Store the test as a dict

            # Save the updated inpatient data
            self.save_data(self.inpatients_file_path, self.inpatients)
            return True

        return False

    def generate_test_id(self) -> int:
        """Generate a unique test ID. This could be a simple counter or a more complex approach."""
        # Placeholder logic for generating unique test IDs
        return len(self.inpatients) + 1  # For simplicity, using the number of inpatients as the ID

    def get_room(self, room_id):
        print(f"Looking for room with ID: {room_id}")

        # Loop through all rooms and print each room's details
        for room in self.rooms:
            print(f"Checking room: {room}", "comparing", room["room_id"], room_id, "result", room["room_id"] == room_id, "type", type(room["room_id"]), type(room_id))

            if room["room_id"] == room_id:
                print(f"Found room: {room}")
                return room
        # If no room is found, raise an exception
        raise ValueError(f"Room with ID {room_id} does not exist.")

    def change_room(self, inpatient_id: int, new_room_id: int) -> Optional[Inpatient]:
        # Get the inpatient
        inpatient = self.get_inpatient(inpatient_id)
        if not inpatient:
            raise ValueError(f"Inpatient with ID {inpatient_id} does not exist.")

        # Get the current room
        current_room = self.get_room(inpatient.room_id)
        if not current_room:
            raise ValueError(f"Current room with ID {inpatient.room_id} does not exist.")

        # Get the new room
        new_room = self.get_room(int(new_room_id))
        if not new_room:
            raise ValueError(f"New room with ID {new_room_id} does not exist.")

        # Update inpatient's room assignment
        inpatient.room_id = new_room_id

        # Update inpatient record in the data
        for i, inp in enumerate(self.inpatients):
            if inp["id"] == inpatient_id:
                self.inpatients[i] = inpatient.to_dict()
        #
        # Save updated room and inpatient data
        self.save_data(self.inpatients_file_path, self.inpatients)

        return inpatient

