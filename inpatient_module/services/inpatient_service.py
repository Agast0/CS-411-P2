import json

class InpatientService:
    def __init__(self):
        self.data_file = 'inpatient_module/models/data/inpatient_records.json'

    def load_inpatients(self):
        try:
            with open(self.data_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def save_inpatients(self, inpatients):
        with open(self.data_file, 'w') as file:
            json.dump(inpatients, file)

    def add_inpatient(self, inpatient_data):
        inpatients = self.load_inpatients()
        inpatients.append(inpatient_data)
        self.save_inpatients(inpatients)
