import base64
import datetime
import os

import matplotlib.pyplot as plt

from Doctor import Doctor
from Patient import Patient
from Person import Person

APPOINTMENT_HEADER = "Patient Name|Doctor Name|Appointment DateTime"

class Admin(Person):
    def __init__(self, username, password, address='None'):
        self.__username = username
        self.__password = password
        self.__address = address

    def get_username(self):
        return self.__username

    def get_password(self):
        return self.__password

    def _persist_credentials(self):
        encoded_password = base64.b64encode(self.__password.encode("utf-8")).decode("ascii")
        with open("admin.txt", "w", encoding="utf-8") as f:
            f.write(f"{self.__username}|{encoded_password}|{self.__address}\n")

    def _ensure_appointment_header(self, appointment_file: str):
        if not os.path.exists(appointment_file) or os.path.getsize(appointment_file) == 0:
            with open(appointment_file, "w", encoding="utf-8") as f:
                f.write(APPOINTMENT_HEADER + "\n")
            return

        with open(appointment_file, "r", encoding="utf-8") as f:
            existing = f.read().splitlines()

        if existing and existing[0].strip() != APPOINTMENT_HEADER:
            with open(appointment_file, "w", encoding="utf-8") as f:
                f.write(APPOINTMENT_HEADER + "\n" + "\n".join(existing) + "\n")

    def view(self,a_list):
        for index, item in enumerate(a_list):
            print(f'{index+1:^5}|{item}')

    def find_index(self, index, items):
        try:
            index = int(index)
            if index in range(len(items)):
                return True
            else:
                print("Invalid index.")
        except ValueError:
            print("Invalid index.")

        return False 

    # def login(self):
    #     """Admin login."""
    #     print("-----Login-----")
    #     username = input('Enter the username: ')
    #     password = input('Enter the password: ')
    #     return self.__username == username and self.__password == password

    def get_doctor_details(self):
        """Get doctor details from input. Type 0 to cancel."""
        
        first_name = input('Enter the first name (0 to cancel): ')
        if first_name == '0':
            return None

        surname = input('Enter the surname (0 to cancel): ')
        if surname == '0':
            return None

        speciality = input('Enter the speciality (0 to cancel): ')
        if speciality == '0':
            return None

        return first_name, surname, speciality
    
    def add_patients(self, patients):
        """Add a patient to the system."""
        print("-----Add Patient-----")
        try:
            f_name = input("Enter patient first name: ")
            l_name = input("Enter patient surname: ")
            age = int(input("Enter age: "))
            mobile = input("Enter the mobile number: ")
            postcode = input("Enter the postcode: ")
            symptoms = input("Enter the symptoms: ")
            address = input("Enter the address: ")
            new_patient = Patient(f_name, l_name, age, mobile, postcode, address, symptoms)
            patients.append(new_patient)
            Patient.append_patient_record('patients_file.txt', new_patient)
            self.view(patients)
        except Exception as e:
            print(f"An error occurred while admitting the patient: {e}")
    
    def add_view_symptoms(self, patients):
        """Add or view symptoms of a patient."""
        print("-----Add/View Symptoms for Patient-----")
        try:
            self.view(patients)
            index = int(input("Enter index of patient: ")) - 1
            if 0 <= index < len(patients):
                print("What do you want to do? ")
                print(" 1. Add symptoms to patient ")
                print(" 2. View symptoms of patient ")
                op = input("Enter your choice: ")
                if op == '1':
                    print("Welcome to Symptoms addition window")
                    new_symptoms = input(f"Enter the symptoms that need to be added for {patients[index].get_first_name()}: ")
                    patients[index].add_symptoms(new_symptoms)
                    print("Successfully Added!")
                    self.view(patients)
                    # Save updated patient to file
                    with open('patients_file.txt', 'w') as f:
                        f.write("Full Name|Age|Mobile|Postcode|Address|Symptoms|Doctor\n")
                        for patient in patients:
                            Patient.append_patient_record('patients_file.txt', patient)
                elif op == '2':
                    print("Symptoms of the patient:")
                    patients[index].print_symptoms()
                else:
                    print("Invalid input!")
            else:
                print("Invalid index. Please enter a valid index.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            
    def assign_doctor_patient(self, patients, doctors):
        print("-----Assign Doctor to Patient-----")
        print("-----Patients-----")
        print(f'{"ID":^5}|{"Full Name":^30}|{"Age":^5}|{"Mobile":^15}|'
                f'{"Postcode":^10}|{"Address":^15}|{"Symptoms":^40}|{"Doctor Name":^10}')
        self.view(patients)
        try:
            patient_index = int(input('Please enter the patient ID: ')) - 1
            if not self.find_index(patient_index, patients):
                print('The ID entered was not found.')
                return
        except ValueError:
            print('The ID entered is incorrect')
            return
        
        # Check if doctor is already assigned
        if patients[patient_index].get_doctor() != "None":
            print(f"This patient is already assigned to Dr. {patients[patient_index].get_doctor()}.")
            relocate_choice = input("Do you want to relocate the doctor? (yes/no): ").lower()
            if relocate_choice == 'yes':
                print("Please use the 'Relocate Doctor for Patient' option (Option 9) to change the assigned doctor.")
                return
            else:
                return
        
        print("-----Doctors Select-----")
        print('Select the doctor that fits these symptoms:')
        patients[patient_index].print_symptoms()
        print('--------------------------------------------------')
        print('ID |          Full Name           |  Speciality')
        self.view(doctors)
        try:
            doctor_index = int(input('Please enter the doctor ID: ')) - 1
            if self.find_index(doctor_index, doctors):
                # Get appointment date and time
                appointment_year = int(input("\nEnter the appointment year (e.g., 2026): "))
                appointment_month = int(input("Enter the appointment month (e.g., 2): "))
                appointment_day = int(input("Enter the appointment day (e.g., 12): "))
                appointment_hour = int(input("Enter the appointment hour (0-23, e.g., 12): "))
                appointment_minute = int(input("Enter the appointment minute (0-59, e.g., 00): "))
                
                # Validate hour and minute
                if appointment_hour < 0 or appointment_hour > 23:
                    print("Invalid hour. Please enter a value between 0 and 23.")
                    return
                if appointment_minute < 0 or appointment_minute > 59:
                    print("Invalid minute. Please enter a value between 0 and 59.")
                    return
                
                appointment_date = datetime.datetime(appointment_year, appointment_month, appointment_day, appointment_hour, appointment_minute)
                patients[patient_index].link(doctors[doctor_index].full_name(), appointment_date)
                doctors[doctor_index].add_patient(patients[patient_index].full_name())
                doctors[doctor_index].add_appointment(appointment_date)
                print(f'The patient is now assigned to the doctor on {appointment_date.strftime("%Y/%m/%d %H:%M")}.')
                
                # Save appointment to year-specific file
                appointment_file = f"{appointment_year}_appointments.txt"
                try:
                    self._ensure_appointment_header(appointment_file)
                    with open(appointment_file, 'a') as f:
                        f.write(f"{patients[patient_index].full_name()}|{doctors[doctor_index].full_name()}|{appointment_date.strftime('%Y/%m/%d %H:%M')}\n")
                except IOError as e:
                    print(f"Error saving appointment: {e}")
                
                # Save updated patient to file
                with open('patients_file.txt', 'w') as f:
                    f.write("Full Name|Age|Mobile|Postcode|Address|Symptoms|Doctor\n")
                for patient in patients:
                    Patient.append_patient_record('patients_file.txt', patient)
            else:
                print('The ID entered was not found.')
        except ValueError:
            print('The ID entered is incorrect')
                
    def relocate_update_appointment_doctor_patient(self, patients, doctors):
        """Relocate doctor or update appointment for a patient."""
        print("-----Relocate or Update Appointment for Doctor-----")
        print("-----List of Patients-----")
        print(f'{"ID":^5}|{"Full Name":^30}|{"Age":^5}|{"Mobile":^15}|'
                f'{"Postcode":^10}|{"Address":^15}|{"Symptoms":^40}|{"Doctor Name":^10}')
        self.view(patients)
        
        if not patients:
            print("No patients available.")
            return
        
        try:
            patient_index = int(input('Please enter the patient ID: ')) - 1
            if not self.find_index(patient_index, patients):
                print('The ID entered was not found.')
                return
            
            # Check if patient has a doctor assigned
            if patients[patient_index].get_doctor() == "None":
                print("This patient has no doctor assigned yet. Please use Option 3 to assign a doctor.")
                return
            
            print(f"Current doctor: Dr. {patients[patient_index].get_doctor()}")
            print("\nWhat would you like to do?")
            print(" 1 - Relocate to a different doctor")
            print(" 2 - Update appointment only")
            choice = input("Enter your choice (1 or 2): ")
            
            if choice == '1':
                # Relocate doctor
                print("-----List of Doctors-----")
                print('ID |          Full Name           |  Speciality')
                self.view(doctors)
                try:
                    new_doctor_index = int(input('Please enter the new doctor ID: ')) - 1
                    if not self.find_index(new_doctor_index, doctors):
                        print('The doctor ID entered was not found.')
                        return
                    
                    old_doctor_name = patients[patient_index].get_doctor()
                    new_doctor_name = doctors[new_doctor_index].full_name()
                    
                    # Get appointment date and time
                    appointment_year = int(input("\nEnter the appointment year (e.g., 2026): "))
                    appointment_month = int(input("Enter the appointment month (e.g., 2): "))
                    appointment_day = int(input("Enter the appointment day (e.g., 12): "))
                    appointment_hour = int(input("Enter the appointment hour (0-23, e.g., 12): "))
                    appointment_minute = int(input("Enter the appointment minute (0-59, e.g., 00): "))
                    
                    # Validate hour and minute
                    if appointment_hour < 0 or appointment_hour > 23:
                        print("Invalid hour. Please enter a value between 0 and 23.")
                        return
                    if appointment_minute < 0 or appointment_minute > 59:
                        print("Invalid minute. Please enter a value between 0 and 59.")
                        return
                    
                    appointment_date = datetime.datetime(appointment_year, appointment_month, appointment_day, appointment_hour, appointment_minute)
                    
                    # Update patient's doctor and appointment
                    patients[patient_index].link(new_doctor_name, appointment_date)
                    doctors[new_doctor_index].add_patient(patients[patient_index].full_name())
                    
                    print(f'Successfully relocated from Dr. {old_doctor_name} to Dr. {new_doctor_name} on {appointment_date.strftime("%Y/%m/%d %H:%M")}.')
                    
                    # Save appointment to year-specific file
                    appointment_file = f"{appointment_year}_appointments.txt"
                    try:
                        self._ensure_appointment_header(appointment_file)
                        with open(appointment_file, 'a') as f:
                            f.write(f"{patients[patient_index].full_name()}|{new_doctor_name}|{appointment_date.strftime('%Y/%m/%d %H:%M')}\n")
                    except IOError as e:
                        print(f"Error saving appointment: {e}")
                    
                    # Save updated patient to file
                    with open('patients_file.txt', 'w') as f:
                        f.write("Full Name|Age|Mobile|Postcode|Address|Symptoms|Doctor\n")
                    for patient in patients:
                        Patient.append_patient_record('patients_file.txt', patient)
                        
                except ValueError:
                    print('Invalid input. Please enter valid numbers.')
            
            elif choice == '2':
                # Update appointment only
                try:
                    appointment_year = int(input("\nEnter the new appointment year (e.g., 2026): "))
                    appointment_month = int(input("Enter the new appointment month (e.g., 2): "))
                    appointment_day = int(input("Enter the new appointment day (e.g., 12): "))
                    appointment_hour = int(input("Enter the new appointment hour (0-23, e.g., 12): "))
                    appointment_minute = int(input("Enter the new appointment minute (0-59, e.g., 00): "))
                    
                    # Validate hour and minute
                    if appointment_hour < 0 or appointment_hour > 23:
                        print("Invalid hour. Please enter a value between 0 and 23.")
                        return
                    if appointment_minute < 0 or appointment_minute > 59:
                        print("Invalid minute. Please enter a value between 0 and 59.")
                        return
                    
                    appointment_date = datetime.datetime(appointment_year, appointment_month, appointment_day, appointment_hour, appointment_minute)
                    doctor_name = patients[patient_index].get_doctor()
                    
                    patients[patient_index].appointment_date = appointment_date
                    print(f'Appointment updated to {appointment_date.strftime("%Y/%m/%d %H:%M")} with Dr. {doctor_name}.')
                    
                    # Save updated appointment to year-specific file
                    appointment_file = f"{appointment_year}_appointments.txt"
                    try:
                        self._ensure_appointment_header(appointment_file)
                        with open(appointment_file, 'a') as f:
                            f.write(f"{patients[patient_index].full_name()}|{doctor_name}|{appointment_date.strftime('%Y/%m/%d %H:%M')} (Updated)\n")
                    except IOError as e:
                        print(f"Error saving appointment: {e}")
                except ValueError:
                    print('Invalid input. Please enter valid numbers.')
            else:
                print('Invalid choice. Please enter 1 or 2.')
        
        except ValueError:
            print('Invalid input. Please enter valid numbers.')
    
    def update_patients_details(self, patients):
        """Update details of a patient."""
        print("-----Update Patient Details-----")
        self.view(patients)
        try:
            patient_index = int(input('Please enter the patient ID: ')) - 1
            if not self.find_index(patient_index, patients):
                print('The ID entered was not found.')
                return
            
            print('Choose the field to be updated:')
            print(' 1 First name')
            print(' 2 Surname')
            print(' 3 Age')
            print(' 4 Mobile')
            print(' 5 Postcode')
            print(' 6 Address')
            print(' 7 Symptoms')
            op = input('Input: ')
            
            if op == '1':
                new_first_name = input("Enter first name: ")
                patients[patient_index].set_first_name(new_first_name)
                print(f"{new_first_name} is updated succesfully!!!")
            elif op == '2':
                new_surname = input("Enter surname: ")
                patients[patient_index].set_surname(new_surname)
            elif op == '3':
                try:
                    new_age = int(input("Enter age: "))
                    patients[patient_index].set_age(new_age)
                except ValueError:
                    print("Invalid age. Please enter a valid number.")
            elif op == '4':
                new_mobile = input("Enter mobile number: ")
                patients[patient_index].set_mobile(new_mobile)
            elif op == '5':
                new_postcode = input("Enter postcode: ")
                patients[patient_index].set_postcode(new_postcode)
            elif op == '6':
                new_address = input("Enter address: ")
                patients[patient_index].set_address(new_address)
            elif op == '7':
                new_symptoms = input("Enter symptoms (comma separated): ")
                patients[patient_index].set_symptoms([symptom.strip() for symptom in new_symptoms.split(',')])
            else:
                print("Invalid option.")
            
            # Save updated patient to file
            with open('patients_file.txt', 'w') as f:
                f.write("Full Name|Age|Mobile|Postcode|Address|Symptoms|Doctor\n")
            for patient in patients:
                Patient.append_patient_record('patients_file.txt', patient)
                
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    
    def patient_management(self, patients, doctors, discharged_patients):
        """Manage patient-related operations."""
        print("-----Patient Management-----")
        print('Choose the operation:')
        print(' 1 - Add patient')
        print(' 2 - View or Add symptoms to patient')
        print(' 3 - Assign doctor to patient')
        print(' 4 - Discharge patient')
        print(' 5 - View patients')
        print(' 6 - View discharged patients')
        print(' 7 - View Group of patients by family')
        print(' 8 - Update patient details')
        print(' 9 - Relocate or update appointment doctor for patient')
        print(' 0 - Back')

        op = input('Which operation do you want: ')
        
        if op == '1':
            self.add_patients(patients)
            
        if op == '2':
            self.add_view_symptoms(patients)
                
        if op == '3':  
            self.assign_doctor_patient(patients, doctors)
        if op == '4':
            self.discharge(patients, discharged_patients)  
        if op == '5':
            self.view_patient(patients)
        if op == '6':
            self.view_discharge(discharged_patients)
        if op == '7':
            self.same_family(patients)
        if op == '8':
            self.update_patients_details(patients)
        if op == '9':
            self.relocate_update_appointment_doctor_patient(patients, doctors)

    def doctor_management(self, doctors):
        """Manage doctor-related operations."""
        print("-----Doctor Management-----")
        print('Choose the operation:')
        print(' 1 - Register')
        print(' 2 - View')
        print(' 3 - Update')
        print(' 4 - Delete')
        print(' 0 - Back')

        op = input('Which operation do you want: ')

        if op == '1':
            print("-----Register-----")
            details = self.get_doctor_details()
            if details is None:
                print ("Registration Cancelled")
                return
            first_name, surname, speciality = details
            
            name_exists = any(first_name == doctor.get_first_name() and surname == doctor.get_surname() for doctor in doctors)
            if name_exists:
                print('Name already exists.')
            else:
                doctors.append(Doctor(first_name, surname, speciality))
                print('Doctor registered.')

        elif op == '2':
            print("-----List of Doctors-----")
            print('ID   |          Full name           |  Speciality')
            self.view(doctors)

        elif op == '3':
            while True:
                print("-----Update Doctor`s Details-----")
                print('ID   |          Full name           |  Speciality')
                self.view(doctors)
                try:
                    index = int(input('Enter the ID of the doctor: ')) - 1
                    if self.find_index(index, doctors):
                        break
                    else:
                        print("Doctor not found")
                except ValueError:
                    print('The ID entered is incorrect')

            print('Choose the field to be updated:')
            print(' 1 First name')
            print(' 2 Surname')
            print(' 3 Speciality')
            try:
                op = int(input('Input: '))
                if op == 1:
                    new_first_name = input("Enter first name: ")
                    doctors[index].set_first_name(new_first_name)
                    print(f"{new_first_name} is updated succesfully!!!")
                elif op == 2:
                    new_surname = input("Enter surname: ")
                    doctors[index].set_surname(new_surname)
                elif op == 3:
                    speciality = input("Enter speciality: ")
                    doctors[index].set_speciality(speciality)
                else:
                    print("Error: Invalid option")
            except ValueError:
                print("Please enter a valid number.")

        elif op == '4':
            print("-----Delete Doctor-----")
            print('ID |          Full Name           |  Speciality')
            self.view(doctors)
            try:
                doctor_index = int(input('Enter the ID of the doctor to be deleted: ')) - 1
                if self.find_index(doctor_index, doctors):
                    del doctors[doctor_index]
                    print("Doctor deleted.")
                else:
                    print('The ID entered is incorrect')
            except ValueError:
                print('The ID entered is incorrect')

        else:
            print('Invalid operation chosen. Check your input!')

    def view_patient(self, patients):
        """View list of patients."""
        print("-----View Patients-----")
        # print('ID |          Full Name           |      Doctor`s Full Name      | Age |    Mobile     | Postcode |    Address    |                Symptoms                ')
        print(f'{"ID":^5}|{"Full Name":^30}|{"Age":^5}|{"Mobile":^15}|'
                f'{"Postcode":^10}|{"Address":^15}|{"Symptoms":^40}|{"Doctor Name":^10}')
        self.view(patients)

    def discharge(self, patients, discharged_patients):
        """Discharge a patient."""
        print("-----Discharge Patient-----")
        try:
            self.view(patients)
            patient_index = int(input('Please enter the patient ID: ')) - 1
            if self.find_index(patient_index, patients):
                discharged_patients.append(patients[patient_index])
                
                # Save discharged patient to discharged_patient.txt using static method
                Patient.append_discharged_patient(patients[patient_index])
                
                print(f"{patients[patient_index].full_name()} has been discharged.")
                del patients[patient_index]
                
                # Update patients_file.txt to remove the discharged patient
                with open('patients_file.txt', 'w') as f:
                    f.write("Full Name|Age|Mobile|Postcode|Address|Symptoms|Doctor\n")
                for patient in patients:
                    Patient.append_patient_record('patients_file.txt', patient)
            else:
                print('The ID entered is incorrect')
        except ValueError:
            print('Invalid patient ID.')

    def view_discharge(self, discharged_patients):
        """View list of discharged patients."""
        print("-----Discharged Patients-----")
        print(f'{"ID":^5}|{"Full Name":^30}|{"Age":^5}|{"Mobile":^15}|'
                f'{"Postcode":^10}|{"Address":^15}|{"Symptoms":^40}|{"Doctor name":^10}')
        self.view(discharged_patients)

    def same_family(self, patients):
        """Group patients by family (surname)."""
        same_family = {}
        for patient in patients:
            patient_surname = patient.get_surname()
            same_family.setdefault(patient_surname, []).append(patient)

        for family_name, family_members in same_family.items():
            print(f"Family Name: {family_name}")
            for patient in family_members:
                print(patient)

    def update_details(self,admin):
        """Update admin details."""
        print('Choose the field to be updated:')
        print(' 1 Username')
        print(' 2 Password')
        print(' 3 Address')
        try:
            op = int(input('Input: '))
            if op == 1:
                self.__username = input("Enter new username: ")
                print(f"{self.__username} as username updated")
            elif op == 2:
                new_password = input('Enter the new password: ')
                if new_password == input('Enter the new password again: '):
                    self.__password = new_password
                    print("Password Changed!")
            elif op == 3:
                self.__address = input("Enter new address: ")
                print(f"{self.__address} as new address updated")
            else:
                print("Invalid input")
        except ValueError:
            print("Please enter a valid input.")

    def settings(self):
        """Admin settings menu for updating credentials or logging out."""
        while True:
            print("-----Admin Settings-----")
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
                self.__username = new_username
                self._persist_credentials()
                print("Username updated.")

            elif op == '2':
                current_password = input("Enter current password: ")
                if current_password != self.__password:
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
                self.__password = new_password
                self._persist_credentials()
                print("Password updated.")

            elif op == '3':
                print("Logged out.")
                return True
            elif op == '0':
                return False
            else:
                print("Invalid option.")

    def get_management_report(self, doctors, patients):
        """Generate management reports."""
        print("-----Management Reports-----")
        print('Choose the operation:')
        print(' 1 - Total number of doctors in the system')
        print(' 2 - Total number of patients per doctor')
        print(' 3 - Total number of appointments per month per doctor')
        print(' 4 - Total number of patients based on illness type')
        print(' 5 - Total appointments')
        print(' 6 - View all appointments by year and month')
        print(' 0 - Back')
        op = input('Choose an option: ')
        try:
            if op == '1':
                total_doctors = len(doctors)
                print(f"\nThe total number of doctors: {total_doctors}")
                
                # Count doctors by speciality
                speciality_counts = {}
                for doctor in doctors:
                    speciality = doctor.get_speciality()
                    speciality_counts[speciality] = speciality_counts.get(speciality, 0) + 1
                
                # Create visualization
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
                
                # Bar chart for total doctors
                ax1.bar(['Total Doctors'], [total_doctors], color='#3498db', width=0.5)
                ax1.set_ylabel('Count', fontsize=12)
                ax1.set_title('Total Number of Doctors', fontsize=14, fontweight='bold')
                ax1.set_ylim(0, total_doctors + 2)
                for i, v in enumerate([total_doctors]):
                    ax1.text(i, v + 0.1, str(v), ha='center', va='bottom', fontsize=12, fontweight='bold')
                
                # Pie chart for specialties
                if speciality_counts:
                    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
                    ax2.pie(speciality_counts.values(), labels=speciality_counts.keys(), autopct='%1.1f%%',
                        startangle=90, colors=colors[:len(speciality_counts)])
                    ax2.set_title('Doctors by Speciality', fontsize=14, fontweight='bold')
                
                plt.tight_layout()
                plt.show()
                
            elif op == '2':
                print("\nTotal number of patients per doctor:")
                doctor_names = []
                total_patients_list = []
                
                for doctor in doctors:
                    total_patients = doctor.get_total_patients()
                    doctor_names.append(doctor.full_name())
                    total_patients_list.append(total_patients)
                    print(f"  {doctor.full_name()}: {total_patients} patients")
                
                if doctor_names:
                    # Create bar chart with colors
                    plt.figure(figsize=(12, 6))
                    colors = plt.cm.viridis(range(len(doctor_names)))
                    bars = plt.bar(doctor_names, total_patients_list, color=colors, edgecolor='black', linewidth=1.2)
                    
                    # Add value labels on top of bars
                    for bar in bars:
                        height = bar.get_height()
                        plt.text(bar.get_x() + bar.get_width()/2., height,
                                f'{int(height)}', ha='center', va='bottom', fontsize=10, fontweight='bold')
                    
                    plt.xlabel('Doctors', fontsize=12, fontweight='bold')
                    plt.ylabel('Number of Patients', fontsize=12, fontweight='bold')
                    plt.title('Total Patients per Doctor', fontsize=14, fontweight='bold')
                    plt.xticks(rotation=45, ha='right')
                    plt.grid(axis='y', alpha=0.3, linestyle='--')
                    plt.tight_layout()
                    plt.show()

            elif op == '3':
                print("\nTotal number of appointments per month per doctor:")
                
                # Read appointments from year-specific files
                import glob
                appointments_data = {}
                
                appointment_files = glob.glob('*_appointments.txt')
                for file in appointment_files:
                    try:
                        with open(file, 'r') as f:
                            for line in f:
                                if line.strip() == APPOINTMENT_HEADER:
                                    continue
                                data = line.strip().split('|')
                                if len(data) >= 3:
                                    doctor_name = data[1].strip()
                                    appointment_datetime = data[2].strip().split()[0]  # Get date part
                                    year_month = '/'.join(appointment_datetime.split('/')[:2])
                                    
                                    if doctor_name not in appointments_data:
                                        appointments_data[doctor_name] = {}
                                    appointments_data[doctor_name][year_month] = appointments_data[doctor_name].get(year_month, 0) + 1
                    except FileNotFoundError:
                        continue
                
                if appointments_data:
                    # Print summary
                    for doctor_name, months in appointments_data.items():
                        print(f"\n{doctor_name}:")
                        for month, count in sorted(months.items()):
                            month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                                        'July', 'August', 'September', 'October', 'November', 'December']
                            year, month_num = month.split('/')
                            month_name = month_names[int(month_num)]
                            print(f"  - {month_name} {year}: {count} appointments")
                    
                    # Create visualization
                    fig, ax = plt.subplots(figsize=(14, 8))
                    
                    # Get all unique months
                    all_months = sorted(set(month for months in appointments_data.values() for month in months.keys()))
                    
                    # Prepare data for grouped bar chart
                    x = range(len(all_months))
                    width = 0.8 / len(appointments_data) if appointments_data else 0.8
                    
                    for i, (doctor_name, months) in enumerate(appointments_data.items()):
                        counts = [months.get(month, 0) for month in all_months]
                        offset = width * i - (width * (len(appointments_data) - 1) / 2)
                        bars = ax.bar([pos + offset for pos in x], counts, width, label=doctor_name)
                        
                        # Add value labels
                        for bar in bars:
                            height = bar.get_height()
                            if height > 0:
                                ax.text(bar.get_x() + bar.get_width()/2., height,
                                    f'{int(height)}', ha='center', va='bottom', fontsize=8)
                    
                    # Format x-axis labels
                    month_labels = []
                    for month in all_months:
                        year, month_num = month.split('/')
                        month_names = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                        month_labels.append(f"{month_names[int(month_num)]} {year}")
                    
                    ax.set_xlabel('Month', fontsize=12, fontweight='bold')
                    ax.set_ylabel('Number of Appointments', fontsize=12, fontweight='bold')
                    ax.set_title('Total Appointments per Month per Doctor', fontsize=14, fontweight='bold')
                    ax.set_xticks(x)
                    ax.set_xticklabels(month_labels, rotation=45, ha='right')
                    ax.legend()
                    ax.grid(axis='y', alpha=0.3, linestyle='--')
                    plt.tight_layout()
                    plt.show()
                else:
                    print("\nNo appointments found.")

            elif op == '4':
                symptom_counts = {}
                for patient in patients:
                    for symptom in patient.get_symptoms():
                        symptom = symptom.strip()
                        if symptom:
                            symptom_counts[symptom] = symptom_counts.get(symptom, 0) + 1

                if symptom_counts:
                    # Print the total number of patients with each symptom
                    print("\nTotal number of patients per symptom:")
                    for symptom, total in sorted(symptom_counts.items(), key=lambda x: x[1], reverse=True):
                        print(f'  {symptom}: {total} patients')

                    # Prepare data for visualization
                    symptom_names = list(symptom_counts.keys())
                    pt_wt_symp = list(symptom_counts.values())

                    # Create a more appealing visualization
                    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
                    
                    # Horizontal bar chart
                    colors = plt.cm.plasma(range(len(symptom_names)))
                    bars = ax1.barh(symptom_names, pt_wt_symp, color=colors, edgecolor='black', linewidth=1.2)
                    ax1.set_xlabel('Number of Patients', fontsize=12, fontweight='bold')
                    ax1.set_ylabel('Symptoms', fontsize=12, fontweight='bold')
                    ax1.set_title('Patients by Symptom Type', fontsize=14, fontweight='bold')
                    ax1.grid(axis='x', alpha=0.3, linestyle='--')
                    
                    # Add value labels
                    for i, (bar, count) in enumerate(zip(bars, pt_wt_symp)):
                        ax1.text(count + 0.1, bar.get_y() + bar.get_height()/2,
                                str(count), va='center', fontsize=10, fontweight='bold')
                    
                    # Pie chart
                    colors_pie = plt.cm.Set3(range(len(symptom_names)))
                    wedges, texts, autotexts = ax2.pie(pt_wt_symp, labels=symptom_names, autopct='%1.1f%%',
                                                        startangle=90, colors=colors_pie)
                    ax2.set_title('Distribution of Symptoms', fontsize=14, fontweight='bold')
                    
                    # Make percentage text bold
                    for autotext in autotexts:
                        autotext.set_color('white')
                        autotext.set_fontweight('bold')
                    
                    plt.tight_layout()
                    plt.show()
                else:
                    print("\nNo symptoms data available.")
                    
            elif op == '5':
                print("-----View All Appointments-----")
                try:
                    import glob
                    appointments = {}
                    
                    # Read appointments from all year-specific files
                    appointment_files = glob.glob('*_appointments.txt')
                    
                    if not appointment_files:
                        print("No appointment files found.")
                        return
                    
                    for file in appointment_files:
                        try:
                            with open(file, 'r') as f:
                                for line in f:
                                    data = line.strip().split('|')
                                    if len(data) >= 3:
                                        patient_name = data[0].strip()
                                        doctor_name = data[1].strip()
                                        appointment_datetime = data[2].strip()
                                        
                                        # Parse date to get year and month
                                        # Format: YYYY/MM/DD HH:MM or YYYY/MM/DD HH:MM (Updated)
                                        date_part = appointment_datetime.split()[0]  # Get YYYY/MM/DD
                                        year_month = '/'.join(date_part.split('/')[:2])  # Get YYYY/MM
                                        
                                        # Group by year/month
                                        if year_month not in appointments:
                                            appointments[year_month] = []
                                        appointments[year_month].append({
                                            'patient': patient_name,
                                            'doctor': doctor_name,
                                            'datetime': appointment_datetime
                                        })
                        except FileNotFoundError:
                            continue
                    
                    if not appointments:
                        print("No appointments found.")
                        return
                    
                    # Display appointments grouped by year and month
                    for year_month in sorted(appointments.keys()):
                        year, month = year_month.split('/')
                        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                                    'July', 'August', 'September', 'October', 'November', 'December']
                        month_name = month_names[int(month)]
                        
                        print(f"\n{month_name} {year}")
                        print("=" * 80)
                        print(f'{"Patient Name":^30}|{"Doctor Name":^30}|{"Appointment Date/Time":^18}')
                        print("-" * 80)
                        
                        for appointment in appointments[year_month]:
                            print(f'{appointment["patient"]:^30}|{appointment["doctor"]:^30}|{appointment["datetime"]:^18}')
                            
                except Exception as e:
                    print(f"Error reading appointments: {e}")
            elif op == '6':
                print("-----View All Appointments by Year and Month-----")
                try:
                    import glob
                    appointments = {}
                    
                    # Read appointments from all year-specific files
                    appointment_files = glob.glob('*_appointments.txt')
                    
                    if not appointment_files:
                        print("No appointment files found.")
                        return
                    
                    for file in appointment_files:
                        try:
                            with open(file, 'r') as f:
                                for line in f:
                                    data = line.strip().split('|')
                                    if len(data) >= 3:
                                        patient_name = data[0].strip()
                                        doctor_name = data[1].strip()
                                        appointment_datetime = data[2].strip()
                                        
                                        # Parse date to get year and month
                                        # Format: YYYY/MM/DD HH:MM or YYYY/MM/DD HH:MM (Updated)
                                        date_part = appointment_datetime.split()[0]  # Get YYYY/MM/DD
                                        year_month = '/'.join(date_part.split('/')[:2])  # Get YYYY/MM
                                        
                                        # Group by year/month
                                        if year_month not in appointments:
                                            appointments[year_month] = []
                                        appointments[year_month].append({
                                            'patient': patient_name,
                                            'doctor': doctor_name,
                                            'datetime': appointment_datetime
                                        })
                        except FileNotFoundError:
                            continue
                    
                    if not appointments:
                        print("No appointments found.")
                        return
                    
                    # Display appointments grouped by year and month
                    for year_month in sorted(appointments.keys()):
                        year, month = year_month.split('/')
                        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                                    'July', 'August', 'September', 'October', 'November', 'December']
                        month_name = month_names[int(month)]
                        
                        print(f"\n{month_name} {year}")
                        print("=" * 80)
                        print(f'{"Patient Name":^30}|{"Doctor Name":^30}|{"Appointment Date/Time":^18}')
                        print("-" * 80)
                        
                        for appointment in appointments[year_month]:
                            print(f'{appointment["patient"]:^30}|{appointment["doctor"]:^30}|{appointment["datetime"]:^18}')
                            
                except Exception as e:
                    print(f"Error reading appointments: {e}")
            elif op == '0':
                return
            else:
                print("Invalid option selected.")
                
        except Exception as e:
            print(f"Error generating report: {e}")