# Importing the required modules
import base64
import os

from Admin import Admin
from Doctor import Doctor
from Patient import Patient
from Person import Person

ADMIN_FILE = "admin.txt"# default password is 123
DOCTOR_FILE = "doctor.txt"
DOCTOR_HEADER = "Full Name|Speciality|Username|Password"


def encode_password(password: str) -> str:
    return base64.b64encode(password.encode("utf-8")).decode("ascii")


def decode_password(encoded_password: str) -> str:
    try:
        return base64.b64decode(encoded_password.encode("ascii")).decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        return ""


def load_admin() -> Admin:
    default_admin = Admin("admin", "123", "B1 1AB")

    if not os.path.exists(ADMIN_FILE) or os.path.getsize(ADMIN_FILE) == 0:
        with open(ADMIN_FILE, "w", encoding="utf-8") as f:
            f.write(
                f"{default_admin.get_username()}|{encode_password(default_admin.get_password())}|B1 1AB\n"
            )
        return default_admin

    with open(ADMIN_FILE, "r", encoding="utf-8") as f:
        line = f.readline().strip()
        if not line:
            return default_admin
        parts = line.split("|")
        if len(parts) < 2:
            return default_admin
        username = parts[0].strip()
        password = decode_password(parts[1].strip())
        address = parts[2].strip() if len(parts) > 2 and parts[2].strip() else "B1 1AB"
        if not username or not password:
            return default_admin
        return Admin(username, password, address)


def load_doctors() -> list:
    default_doctors = [
        Doctor("John", "Smith", "Internal Med.", "john", "123"),
        Doctor("Jane", "Smith", "Pediatrics", "jane", "123"),
        Doctor("Jon", "Carlos", "Cardiology", "jon", "123"),
    ]

    if not os.path.exists(DOCTOR_FILE) or os.path.getsize(DOCTOR_FILE) == 0:
        with open(DOCTOR_FILE, "w", encoding="utf-8") as f:
            f.write(f"{DOCTOR_HEADER}\n")
            for doctor in default_doctors:
                f.write(
                    f"{doctor.full_name()}|{doctor.get_speciality()}|"
                    f"{doctor.get_username()}|{encode_password(doctor.get_password())}\n"
                )
        return default_doctors

    doctors = []
    with open(DOCTOR_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line == DOCTOR_HEADER:
                continue
            parts = [part.strip() for part in line.split("|")]
            if len(parts) < 4:
                continue
            if len(parts) >= 5:
                first_name, surname, speciality, username, encoded_password = parts[:5]
                password = decode_password(encoded_password)
            else:
                full_name, speciality, username, encoded_password = parts[:4]
                password = decode_password(encoded_password)
                name_parts = full_name.split()
                if not name_parts:
                    continue
                first_name = name_parts[0]
                surname = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

            if not all([first_name, speciality, username, password]):
                continue
            doctors.append(Doctor(first_name, surname, speciality, username, password))

    return doctors if doctors else default_doctors

def main():
    # Initializing the actors
    admin = load_admin()

    # Initializing doctors
    doctors = load_doctors()


    patients = [
        Patient('Sara', 'Smith', 20, '07012345678', 'B1 234', 'Kathmandu', 'Fever, Cough'),
        Patient('Mike', 'Jones', 37, '07555551234', 'L2 2AB', 'Kathmandu', 'Headache, Nausea'),
        Patient('David', 'Smith', 15, '07123456789', 'C1 ABC', 'Kathmandu', 'Fever, Sore Throat'),
        Patient('Nabin', 'Oli', 30, '07123456789', 'C1 ABC', 'Kathmandu', 'Chest Pain, Shortness of Breath'),
        Patient('Nabraj', 'Oli', 25, '07123456789', 'C1 ABC', 'Kathmandu', 'Back Pain')
    ]
    f = open("patients_file.txt", "r")
    check = f.read()
    f.close()
    if check:
        patients = Patient.read_patient_records("patients_file.txt")
    else:
        patients = []
    
    # Load discharged patients
    discharged_patients = Patient.read_discharged_patients()
    
    for patient in patients:
        if patient.get_doctor()!="None":
            doctor_name = patient.get_doctor()
            for doctor in doctors:
                if doctor.full_name() == doctor_name:
                    doctor.add_patient(patient)
                else:
                    pass
        else:
            pass

    # Keep trying to login until the login details are correct
    logged_in_user = None
    user_type = None
    while True:
        try:
            print("-----Login-----")
            username = input('Enter the username: ')
            password = input('Enter the password: ')
            
            # Check admin login
            if admin.get_username() == username and admin.get_password() == password:
                logged_in_user = admin
                user_type = 'admin'
                break
            
            # Check doctor logins
            for doctor in doctors:
                if doctor.get_username() == username and doctor.get_password() == password:
                    logged_in_user = doctor
                    user_type = 'doctor'
                    break
            
            if logged_in_user:
                break
            
            print('Incorrect username or password.')
        except Exception as e:
            print(f"An error occurred during login: {e}")

    running = True
    
    # Admin menu
    if user_type == 'admin':
        while running:
            try:
                # Print the menu
                print('\nChoose the operation:')
                print(' 1 - Doctors management')
                print(' 2 - Patients management')
                print(' 3 - Management Reports')
                print(' 4 - Setting')

                # Get the option
                op = input('Please enter your choice: ')

                if op == '1':
                    admin.doctor_management(doctors)

                elif op == '2':
                    admin.patient_management(patients, doctors, discharged_patients)
                elif op == '3':
                    admin.get_management_report(doctors, patients)
                elif op == '4':
                    if admin.settings():
                        running = False
                else:
                    # The user did not enter an option that exists in the menu
                    print('Invalid option. Try again')

            except ValueError:
                print("Invalid input. Please enter a valid number.")
            except IndexError:
                print("Index out of range. Please enter a valid option.")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
    
    # Doctor menu
    elif user_type == 'doctor':
        while running:
            try:
                print(f"\nWelcome Dr. {logged_in_user.full_name()}")
                print('\nChoose the operation:')
                print(' 1- View my patients')
                print(' 2- View patient symptoms')
                print(' 3- Add patient symptoms')
                print(' 4- Settings')

                op = input('Please enter your choice: ')

                if op == '1':
                    print(f"Patients under Dr. {logged_in_user.full_name()}:")
                    doctor_patients = logged_in_user.get_patients()
                    if doctor_patients:
                        logged_in_user.view(doctor_patients)
                    else:
                        print("No patients assigned yet.")

                elif op == '2':
                    doctor_patients = logged_in_user.get_patients()
                    if doctor_patients:
                        logger = True
                        logged_in_user.view(doctor_patients)
                        try:
                            index = int(input("Enter patient ID: ")) - 1
                            if 0 <= index < len(doctor_patients):
                                print(f"Symptoms of {doctor_patients[index].full_name()}:")
                                doctor_patients[index].print_symptoms()
                            else:
                                print("Invalid patient ID.")
                        except ValueError:
                            print("Invalid input.")
                    else:
                        print("No patients assigned yet.")
                elif op == '3':
                    logged_in_user.add_patient_symptoms()
                elif op == '4':
                    # Logout
                    if logged_in_user.settings():
                        running = False
                else:
                    print('Invalid option. Try again')

            except Exception as e:
                print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()