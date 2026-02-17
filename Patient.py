import os

from Person import Person

DISCHARGED_FILE = "discharged_patient.txt"
DISCHARGED_HEADER = "Full Name|Age|Mobile|Postcode|Address|Symptoms|Doctor"

class Patient(Person):
    """Patient class"""

    def __init__(self, first_name, surname, age, mobile, postcode, address, symptoms, doctor='None'):
        """
        Args:
            first_name (string): First name
            surname (string): Surname
            age (int): Age
            mobile (string): Mobile number
            postcode (string): Postcode
            address (string): Address 
            doctor (string): Doctor's full name (default is 'None')
        """
        
        self.__first_name = first_name
        self.__surname = surname
        self.__age = age
        self.__mobile = mobile
        self.__postcode = postcode
        self.__address = address
        self.__symptoms = symptoms if isinstance(symptoms, list) else symptoms.split(', ')
        self.__doctor = doctor
        self.appointments = []

    def get_first_name(self):
        """Returns the first name of the person."""
        return self.__first_name

    def set_first_name(self, new_first_name):
        """Sets the first name of the person."""
        self.__first_name = new_first_name

    def get_surname(self):
        """Returns the surname of the person."""
        return self.__surname

    def set_surname(self, new_surname):
        """Sets the surname of the person."""
        self.__surname = new_surname

    def full_name(self):
        """Returns the full name of the person."""
        return f"{self.__first_name} {self.__surname}"
    
    def get_doctor(self):
        """Returns the doctor's full name linked to the patient."""
        return self.__doctor

    # def link(self, doctor):
    #     """Links the patient to a doctor by setting the doctor's full name.
        
    #     Args:
    #         doctor (string): The doctor's full name
    #     """
    #     self.__doctor = doctor
    def link(self, doctor, appointment_date):
        self.__doctor = doctor
        self.appointment_date = appointment_date

    def print_symptoms(self):
        """Prints all the symptoms of the patient."""
        print(", ".join(self.__symptoms))

    def set_symptoms(self, symptoms):
        """Sets the symptoms of the patient."""
        self.__symptoms = symptoms

    def add_symptoms(self, new_symptoms):
        """Adds new symptoms to the existing symptoms.
        
        Args:
            new_symptoms (string): New symptoms to be added
        """
        if isinstance(new_symptoms, list):
            self.__symptoms.extend(new_symptoms)
        else:
            self.__symptoms.append(new_symptoms)

    def get_symptoms(self):
        """Returns the symptoms of the patient."""
        return self.__symptoms
    
    def add_appointment(self, time):
        self.appointments.append(time)
        self.status = "Approved"

    @staticmethod
    def read_patient_records(patients_file: str) -> list:
        """Read patient records from a file.
        
        Args:
            patients_file (str): The file containing patient records.

        Returns:
            list: List of Patient instances.
        """
        patient_list = []

        try:
            with open(patients_file, 'r') as fd:
                next(fd)  # Skip header line
                for line in fd:
                    data = line.split('|')
                    firstname = data[0].strip().split(" ")
                    firstname = firstname[0]
                    surname = data[0].strip().split(" ")
                    surname = surname[1]
                    patient = Patient(
                        firstname.strip(),  # first_name
                        surname.strip(),  # surname
                        int(data[1].strip()),  # age
                        data[2].strip(),  # mobile
                        data[3].strip(),  # postcode
                        data[4].strip(),  # address
                        data[5].strip().split(', '),  # symptoms
                        data[6].strip())
                    patient_list.append(patient)
        except FileNotFoundError:
            print("File does not exist")
        return patient_list
        
    @staticmethod
    def append_patient_record(patients_file: str, patient):
        """Append a single patient record to the file.
        
        Args:
            patients_file (str): The file to append patient record to.
            patient: The Patient instance to append.
        """
        try:
            with open(patients_file, 'a') as file:
                file.write(patient.to_file_format() + "\n")
        except IOError as e:
            print(f"An error occurred while appending to the file: {e}")

    @staticmethod
    def append_discharged_patient(patient):
        """Append a discharged patient record to discharged_patient.txt file.
        
        Args:
            patient: The Patient instance to append to discharged patients file.
        """
        try:
            if not os.path.exists(DISCHARGED_FILE) or os.path.getsize(DISCHARGED_FILE) == 0:
                with open(DISCHARGED_FILE, "w", encoding="utf-8") as file:
                    file.write(DISCHARGED_HEADER + "\n")
            else:
                with open(DISCHARGED_FILE, "r", encoding="utf-8") as file:
                    existing = file.read().splitlines()
                if existing and existing[0].strip() != DISCHARGED_HEADER:
                    with open(DISCHARGED_FILE, "w", encoding="utf-8") as file:
                        file.write(DISCHARGED_HEADER + "\n" + "\n".join(existing) + "\n")

            with open(DISCHARGED_FILE, "a", encoding="utf-8") as file:
                file.write(patient.to_file_format() + "\n")
        except IOError as e:
            print(f"An error occurred while saving discharged patient: {e}")

    @staticmethod
    def read_discharged_patients() -> list:
        """Read discharged patient records from discharged_patient.txt file.
        
        Returns:
            list: List of discharged Patient instances.
        """
        patient_list = []

        try:
            with open(DISCHARGED_FILE, 'r') as fd:
                for line in fd:
                    line = line.strip()
                    if not line or line == DISCHARGED_HEADER:
                        continue
                    data = line.split('|')
                    if len(data) < 7:
                        continue
                    firstname = data[0].strip().split(" ")
                    firstname = firstname[0]
                    surname = data[0].strip().split(" ")
                    surname = surname[1] if len(surname) > 1 else ""
                    patient = Patient(
                        firstname.strip(),
                        surname.strip(),
                        int(data[1].strip()),
                        data[2].strip(),
                        data[3].strip(),
                        data[4].strip(),
                        data[5].strip().split(', '),
                        data[6].strip())
                    patient_list.append(patient)
        except FileNotFoundError:
            print("No discharged patients file found")
        return patient_list

    def to_file_format(self):
        """Returns a clean file format for storage (no centered spacing)."""
        return f"{self.full_name()}|{self.__age}|{self.__mobile}|{self.__postcode}|{self.__address}|{', '.join(self.__symptoms)}|{self.get_doctor()}"
            
    def __str__(self):
        """Returns a string representation of the patient."""
        return (f'{self.full_name():^30}|{self.__age:^5}|{self.__mobile:^15}|'
                f'{self.__postcode:^10}|{self.__address:^15}|{", ".join(self.__symptoms):^40}|{self.get_doctor():^10}')
