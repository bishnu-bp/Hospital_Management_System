import base64
import os

from Patient import Patient
from Person import Person

class Doctor(Person):
    """A class that represents a doctor and manages doctor operations."""

    def __init__(self, first_name: str, surname: str, speciality: str, username, password):
        """
        Initialize a new Doctor instance.

        Args:
            first_name (str): First name of the doctor.
            surname (str): Surname of the doctor.
            speciality (str): Doctor's speciality.
        """
        super().__init__(first_name, surname, username, password)
        self.__speciality = speciality
        self.__patients = []
        self.__appointments = {}

    def get_speciality(self) -> str:
        """Returns the speciality of the doctor."""
        return self.__speciality

    def set_speciality(self, new_speciality: str):
        """Sets the speciality of the doctor.
        
        Args:
            new_speciality (str): The new speciality to be set.
        """
        self.__speciality = new_speciality

    def _persist_credentials(self, old_username=None):
        encoded_password = base64.b64encode(self.get_password().encode("utf-8")).decode("ascii")
        file_path = "doctor.txt"
        header = "Full Name|Speciality|Username|Password"
        lines = []
        updated = False
        match_username = old_username if old_username is not None else self.get_username()

        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    raw = line.rstrip("\n")
                    parts = raw.split("|")
                    if raw == header:
                        lines.append(raw)
                        continue
                    if len(parts) < 4:
                        lines.append(raw)
                        continue
                    if len(parts) >= 5:
                        first_name, surname, speciality, username, _ = parts[:5]
                        full_name = f"{first_name} {surname}".strip()
                    else:
                        full_name, speciality, username, _ = parts[:4]
                    if (
                        full_name == self.full_name()
                        and speciality == self.__speciality
                        and username == match_username
                    ):
                        lines.append(
                            f"{full_name}|{speciality}|{self.get_username()}|{encoded_password}"
                        )
                        updated = True
                    else:
                        lines.append(raw)

        if not updated:
            lines.append(
                f"{self.full_name()}|{self.__speciality}|"
                f"{self.get_username()}|{encoded_password}"
            )

        if not lines or lines[0] != header:
            lines.insert(0, header)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    def add_patient(self, patient):
        """Adds a patient to the doctor's list of patients.
        
        Args:
            patient (Patient): The patient to be added.
        """
        self.__patients.append(patient)

    def get_total_patients(self) -> int:
        """Returns the total number of patients assigned to the doctor."""
        return len(self.__patients)

    def get_patients(self) -> list:
        """Returns the list of patients assigned to the doctor."""
        return self.__patients
    
    def add_appointment(self, appointment_date):
        month_year = appointment_date.strftime("%B %Y")
        if month_year not in self.__appointments:
            self.__appointments[month_year] = 1
        else:
            self.__appointments[month_year] += 1

    def get_appointments(self):
        return self.__appointments

    def view(self, a_list):
        """View a list of patients."""
        for index, item in enumerate(a_list):
            print(f'{index+1:^5}|{item}')

    def add_patient_symptoms(self):
        """Add symptoms for a patient assigned to this doctor."""
        patients = self.get_patients()
        if not patients:
            print("No patients assigned yet.")
            return

        self.view(patients)
        try:
            index = int(input("Enter patient ID: ")) - 1
            if index < 0 or index >= len(patients):
                print("Invalid patient ID.")
                return
            new_symptoms = input("Enter symptoms (comma separated): ")
            symptoms_list = [s.strip() for s in new_symptoms.split(",") if s.strip()]
            if not symptoms_list:
                print("No symptoms provided.")
                return

            patients[index].add_symptoms(symptoms_list)
            print("Symptoms updated.")

            all_patients = Patient.read_patient_records("patients_file.txt")
            updated = False
            for patient in all_patients:
                if patient.full_name() == patients[index].full_name():
                    patient.set_symptoms(patients[index].get_symptoms())
                    updated = True
                    break

            if updated:
                with open("patients_file.txt", "w") as f:
                    f.write("Full Name|Age|Mobile|Postcode|Address|Symptoms|Doctor\n")
                for patient in all_patients:
                    Patient.append_patient_record("patients_file.txt", patient)
        except ValueError:
            print("Invalid input.")

    def settings(self):
        """Doctor settings menu for updating credentials or logging out."""
        while True:
            print("-----Doctor Settings-----")
            print(" 1 - Change username")
            print(" 2 - Change password")
            print(" 3 - Logout")
            print(" 0 - Back")
            op = input("Choose an option: ")

            if op == '1':
                new_username = input("Enter new username: ").strip()
                if not new_username:
                    print("Username cannot be empty.")
                    continue
                old_username = self.get_username()
                self.set_username(new_username)
                self._persist_credentials(old_username=old_username)
                print("Username updated.")

            elif op == '2':
                current_password = input("Enter current password: ")
                if current_password != self.get_password():
                    print("Current password is incorrect.")
                    continue
                new_password = input("Enter new password: ")
                confirm_password = input("Re-enter new password: ")
                if new_password != confirm_password:
                    print("Passwords do not match.")
                    continue
                if not new_password:
                    print("Password cannot be empty.")
                    continue
                self.set_password(new_password)
                self._persist_credentials()
                print("Password updated.")

            elif op == '3':
                print("Logged out.")
                return True
            elif op == '0':
                return False
            else:
                print("Invalid option.")

    def __str__(self) -> str:
        """Returns a string representation of the doctor."""
        return f'{self.full_name():^30}|{self.__speciality:^15}'
