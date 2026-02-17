import os
import sys
import time

from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import (QMainWindow, QMessageBox, QTableWidgetItem, QHeaderView,
                              QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                              QPushButton, QFormLayout, QComboBox, QDialogButtonBox,
                              QWidget, QTableWidget, QAction, QInputDialog, QTextBrowser,
                              QProgressBar)
from PyQt5.QtCore import Qt

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from Main import load_admin, load_doctors
from Patient import Patient
from Doctor import Doctor


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGIN_UI = os.path.join(BASE_DIR, "Gui_files", "login_window.ui")
ADMIN_UI = os.path.join(BASE_DIR, "Gui_files", "adminWindow.ui")
DOCTOR_UI = os.path.join(BASE_DIR, "Gui_files", "doctor_window.ui")


class LoadingScreen(QDialog):
    """Loading screen with progress bar."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Loading...")
        self.setFixedSize(500, 300)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Container widget with styling
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: #f6f7fb;
                border-radius: 15px;
                border: 3px solid #e6e9f2;
            }
        """)
        
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(40, 40, 40, 40)
        container_layout.setSpacing(20)
        
        # Logo/Icon placeholder
        icon_label = QLabel("🏥")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("""
            font-size: 48pt;
            background: transparent;
            border: none;
        """)
        container_layout.addWidget(icon_label)
        
        # Title label
        self.title_label = QLabel("Hospital Management System")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 18pt;
            font-weight: bold;
            color: #111827;
            background: transparent;
            border: none;
            letter-spacing: 1px;
        """)
        container_layout.addWidget(self.title_label)
        
        # Subtitle
        subtitle_label = QLabel("Please wait while we load your data...")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("""
            font-size: 9pt;
            color: #6b7280;
            background: transparent;
            border: none;
            margin-bottom: 10px;
        """)
        container_layout.addWidget(subtitle_label)
        
        # Status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            font-size: 11pt;
            color: #1f2937;
            font-weight: 600;
            background: transparent;
            border: none;
            margin-top: 5px;
        """)
        container_layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #e6e9f2;
                border-radius: 10px;
                text-align: center;
                background-color: #ffffff;
                height: 30px;
                font-size: 11pt;
                font-weight: bold;
                color: #111827;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 10px;
            }
        """)
        container_layout.addWidget(self.progress_bar)
        
        # Version/Copyright label
        version_label = QLabel("Version 1.0.0 © 2026")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("""
            font-size: 8pt;
            color: #9ca3af;
            background: transparent;
            border: none;
            margin-top: 10px;
        """)
        container_layout.addWidget(version_label)
        
        main_layout.addWidget(container)
        self.setLayout(main_layout)
    
    def update_progress(self, value, status):
        """Update progress bar value and status text."""
        self.progress_bar.setValue(value)
        self.status_label.setText(status)
        QtWidgets.QApplication.processEvents()  # Force UI update

# Prevent matplotlib from closing the application when figure windows are closed
import matplotlib
rcParams = matplotlib.rcParams
rcParams['figure.raise_window'] = False


class DoctorDialog(QDialog):
    """Dialog for adding/editing doctor information."""
    def __init__(self, doctor=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Doctor Details")
        self.setMinimumWidth(400)
        
        layout = QFormLayout()
        
        self.first_name_input = QLineEdit()
        self.surname_input = QLineEdit()
        self.speciality_input = QLineEdit()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        
        layout.addRow("First Name:", self.first_name_input)
        layout.addRow("Surname:", self.surname_input)
        layout.addRow("Speciality:", self.speciality_input)
        layout.addRow("Username:", self.username_input)
        layout.addRow("Password:", self.password_input)
        
        if doctor:
            self.first_name_input.setText(doctor.get_first_name())
            self.surname_input.setText(doctor.get_surname())
            self.speciality_input.setText(doctor.get_speciality())
            self.username_input.setText(doctor.get_username())
            self.username_input.setEnabled(False)
            self.password_input.setPlaceholderText("Leave empty to keep current password")
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(buttons)
        self.setLayout(layout)
    
    def get_data(self):
        return {
            'first_name': self.first_name_input.text().strip(),
            'surname': self.surname_input.text().strip(),
            'speciality': self.speciality_input.text().strip(),
            'username': self.username_input.text().strip(),
            'password': self.password_input.text().strip()
        }


class PatientDialog(QDialog):
    """Dialog for adding/editing patient information."""
    def __init__(self, patient=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Patient Details")
        self.setMinimumWidth(450)
        
        layout = QFormLayout()
        
        self.first_name_input = QLineEdit()
        self.surname_input = QLineEdit()
        self.age_input = QLineEdit()
        self.mobile_input = QLineEdit()
        self.postcode_input = QLineEdit()
        self.address_input = QLineEdit()
        self.symptoms_input = QLineEdit()
        
        layout.addRow("First Name:", self.first_name_input)
        layout.addRow("Surname:", self.surname_input)
        layout.addRow("Age:", self.age_input)
        layout.addRow("Mobile:", self.mobile_input)
        layout.addRow("Postcode:", self.postcode_input)
        layout.addRow("Address:", self.address_input)
        layout.addRow("Symptoms:", self.symptoms_input)
        
        if patient:
            self.first_name_input.setText(patient.get_first_name())
            self.surname_input.setText(patient.get_surname())
            self.age_input.setText(str(patient._Patient__age))
            self.mobile_input.setText(patient._Patient__mobile)
            self.postcode_input.setText(patient._Patient__postcode)
            self.address_input.setText(patient._Patient__address)
            self.symptoms_input.setText(", ".join(patient.get_symptoms()))
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(buttons)
        self.setLayout(layout)
    
    def get_data(self):
        return {
            'first_name': self.first_name_input.text().strip(),
            'surname': self.surname_input.text().strip(),
            'age': self.age_input.text().strip(),
            'mobile': self.mobile_input.text().strip(),
            'postcode': self.postcode_input.text().strip(),
            'address': self.address_input.text().strip(),
            'symptoms': self.symptoms_input.text().strip()
        }


class DoctorWindow(QMainWindow):
    def __init__(self, doctor, patients, parent=None):
        super().__init__(parent)
        uic.loadUi(DOCTOR_UI, self)
        self._doctor = doctor
        self._patients = patients
        self._populate_dashboard()
        self._connect_menu_actions()

    def closeEvent(self, event):
        """Handle close event to properly quit the application."""
        QtWidgets.QApplication.quit()
        event.accept()

    def _get_patient_appointment(self, patient_name):
        """Get appointment information for a specific patient.
        
        Args:
            patient_name (str): Full name of the patient
            
        Returns:
            str: Appointment date/time or None if no appointment found
        """
        import glob
        
        appointment_files = glob.glob('*_appointments.txt')
        for file in appointment_files:
            try:
                with open(file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if '|' in line:
                            parts = line.split('|')
                            if len(parts) >= 3:
                                file_patient_name = parts[0].strip()
                                doctor_name = parts[1].strip()
                                appointment_datetime = parts[2].strip()
                                
                                # Check if this is the patient and doctor matches
                                if (file_patient_name == patient_name and 
                                    doctor_name == self._doctor.full_name()):
                                    return appointment_datetime
            except FileNotFoundError:
                continue
        return None

    def _connect_menu_actions(self):
        """Connect menu actions."""
        self.menuHome.aboutToShow.connect(self._show_dashboard)
        self.menuMyPatients.aboutToShow.connect(self._show_my_patients)
        self.menuSettings.aboutToShow.connect(self._show_settings)

    def _show_dashboard(self):
        """Return to dashboard view."""
        current_geometry = self.geometry()
        uic.loadUi(DOCTOR_UI, self)
        self._connect_menu_actions()
        self._populate_dashboard()
        self.setGeometry(current_geometry)

    def _populate_dashboard(self):
        """Populate doctor dashboard with patient information."""
        # Update welcome label
        self.welcomeLabel.setText(f"Welcome, Dr. {self._doctor.full_name()}")
        
        # Get doctor's patients
        doctor_patients = [p for p in self._patients if p.get_doctor() == self._doctor.full_name()]
        
        # Update patient count
        self.lcdNumber.display(len(doctor_patients))
        
        # Populate patients table
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        self.tableWidget.setRowCount(len(doctor_patients))
        for row_index, patient in enumerate(doctor_patients):
            self.tableWidget.setItem(row_index, 0, QTableWidgetItem(str(row_index + 1)))
            self.tableWidget.setItem(row_index, 1, QTableWidgetItem(patient.full_name()))
            self.tableWidget.setItem(row_index, 2, QTableWidgetItem(patient._Patient__mobile))
            self.tableWidget.setItem(row_index, 3, QTableWidgetItem(patient._Patient__address))
            
            # Get symptoms
            symptoms = patient.get_symptoms()
            symptoms_str = ', '.join(symptoms) if symptoms else 'None'
            self.tableWidget.setItem(row_index, 4, QTableWidgetItem(symptoms_str))
            
            # Appointment info
            appointment_info = self._get_patient_appointment(patient.full_name())
            self.tableWidget.setItem(row_index, 5, QTableWidgetItem(appointment_info if appointment_info else 'No appointment'))

    def _show_my_patients(self):
        """Show my patients management interface."""
        current_geometry = self.geometry()
        
        # Create patient management widget
        mgmt_widget = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("My Patients")
        title.setStyleSheet("font-size: 18pt; font-weight: 600; color: #111827; margin: 10px;")
        layout.addWidget(title)
        
        # Buttons
        button_layout = QHBoxLayout()
        add_symptoms_btn = QPushButton("Add Symptoms to Patient")
        view_family_btn = QPushButton("View Patient Family")
        
        add_symptoms_btn.setStyleSheet("padding: 8px 16px; font-size: 11pt;")
        view_family_btn.setStyleSheet("padding: 8px 16px; font-size: 11pt;")
        
        add_symptoms_btn.clicked.connect(self._add_symptoms)
        view_family_btn.clicked.connect(self._view_patient_family)
        
        button_layout.addWidget(add_symptoms_btn)
        button_layout.addWidget(view_family_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Patient table
        self.patient_mgmt_table = QTableWidget()
        self.patient_mgmt_table.setColumnCount(6)
        self.patient_mgmt_table.setHorizontalHeaderLabels(["ID", "Full Name", "Mobile", "Address", "Symptoms", "Appointment"])
        self.patient_mgmt_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Populate with doctor's patients only
        doctor_patients = [p for p in self._patients if p.get_doctor() == self._doctor.full_name()]
        self.patient_mgmt_table.setRowCount(len(doctor_patients))
        
        for row_index, patient in enumerate(doctor_patients):
            self.patient_mgmt_table.setItem(row_index, 0, QTableWidgetItem(str(row_index + 1)))
            self.patient_mgmt_table.setItem(row_index, 1, QTableWidgetItem(patient.full_name()))
            self.patient_mgmt_table.setItem(row_index, 2, QTableWidgetItem(patient._Patient__mobile))
            self.patient_mgmt_table.setItem(row_index, 3, QTableWidgetItem(patient._Patient__address))
            
            symptoms = patient.get_symptoms()
            symptoms_str = ', '.join(symptoms) if symptoms else 'None'
            self.patient_mgmt_table.setItem(row_index, 4, QTableWidgetItem(symptoms_str))
            
            appointment_info = self._get_patient_appointment(patient.full_name())
            self.patient_mgmt_table.setItem(row_index, 5, QTableWidgetItem(appointment_info if appointment_info else 'No appointment'))
        
        layout.addWidget(self.patient_mgmt_table)
        mgmt_widget.setLayout(layout)
        
        self.setCentralWidget(mgmt_widget)
        self.setGeometry(current_geometry)

    def _add_symptoms(self):
        """Add symptoms to a patient."""
        # Get doctor's patients
        doctor_patients = [p for p in self._patients if p.get_doctor() == self._doctor.full_name()]
        
        if not doctor_patients:
            QMessageBox.information(self, "No Patients", "You don't have any patients assigned.")
            return
        
        # Get patient names
        patient_names = [p.full_name() for p in doctor_patients]
        
        # Ask which patient
        patient_name, ok = QInputDialog.getItem(
            self, "Select Patient", "Choose a patient:", patient_names, 0, False
        )
        
        if not ok:
            return
        
        # Get symptoms
        symptoms, ok = QInputDialog.getText(
            self, "Add Symptoms", f"Enter symptoms for {patient_name}:"
        )
        
        if ok and symptoms.strip():
            # Find the patient
            patient = next((p for p in doctor_patients if p.full_name() == patient_name), None)
            if patient:
                # Add symptoms directly to patient object
                patient.add_symptoms(symptoms.strip())
                # Save all patients to file
                self._save_all_patients()
                QMessageBox.information(self, "Success", f"Symptoms added to {patient_name}")
                # Refresh the view
                self._show_my_patients()

    def _save_all_patients(self):
        """Save all patients to patients_file.txt."""
        with open('patients_file.txt', 'w') as f:
            f.write("Full Name|Age|Mobile|Postcode|Address|Symptoms|Doctor\n")
        for patient in self._patients:
            Patient.append_patient_record('patients_file.txt', patient)

    def _view_patient_family(self):
        """View family members of a patient."""
        # Get doctor's patients
        doctor_patients = [p for p in self._patients if p.get_doctor() == self._doctor.full_name()]
        
        if not doctor_patients:
            QMessageBox.information(self, "No Patients", "You don't have any patients assigned.")
            return
        
        # Get patient names
        patient_names = [p.full_name() for p in doctor_patients]
        
        # Ask which patient
        patient_name, ok = QInputDialog.getItem(
            self, "Select Patient", "Choose a patient:", patient_names, 0, False
        )
        
        if not ok:
            return
        
        # Find the patient
        patient = next((p for p in doctor_patients if p.full_name() == patient_name), None)
        if patient:
            family_members = [p for p in self._patients if p.is_family_member(patient)]
            
            if family_members:
                family_info = f"Family members of {patient_name}:\n\n"
                for member in family_members:
                    family_info += f"Name: {member.full_name()}\n"
                    family_info += f"Mobile: {member._Patient__mobile}\n"
                    family_info += f"Address: {member._Patient__address}\n"
                    family_info += f"Doctor: {member.get_doctor()}\n\n"
                
                # Create dialog to show family info
                dialog = QDialog(self)
                dialog.setWindowTitle("Patient Family Members")
                dialog.setMinimumSize(500, 400)
                
                layout = QVBoxLayout()
                text_browser = QTextBrowser()
                text_browser.setPlainText(family_info)
                layout.addWidget(text_browser)
                
                close_btn = QPushButton("Close")
                close_btn.clicked.connect(dialog.accept)
                layout.addWidget(close_btn)
                
                dialog.setLayout(layout)
                dialog.exec_()
            else:
                QMessageBox.information(self, "No Family", f"{patient_name} has no family members registered.")

    def _show_settings(self):
        """Show settings interface for doctor."""
        current_geometry = self.geometry()
        
        # Create settings widget
        settings_widget = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Doctor Settings")
        title.setStyleSheet("font-size: 18pt; font-weight: 600; color: #111827; margin: 10px;")
        layout.addWidget(title)
        
        # Info section
        info_layout = QFormLayout()
        info_layout.addRow("Full Name:", QLabel(self._doctor.full_name()))
        info_layout.addRow("Speciality:", QLabel(self._doctor.get_speciality()))
        info_layout.addRow("Username:", QLabel(self._doctor.get_username()))
        info_layout.addRow("Total Patients:", QLabel(str(self._doctor.get_total_patients())))
        
        layout.addLayout(info_layout)
        
        # Action buttons
        button_layout = QVBoxLayout()
        
        change_username_btn = QPushButton("Change Username")
        change_password_btn = QPushButton("Change Password")
        logout_btn = QPushButton("Logout")
        
        change_username_btn.setStyleSheet("padding: 8px 16px; font-size: 11pt; margin: 5px;")
        change_password_btn.setStyleSheet("padding: 8px 16px; font-size: 11pt; margin: 5px;")
        logout_btn.setStyleSheet("padding: 8px 16px; font-size: 11pt; margin: 5px; background-color: #dc2626; color: white;")
        
        change_username_btn.clicked.connect(self._change_username)
        change_password_btn.clicked.connect(self._change_password)
        logout_btn.clicked.connect(self._logout)
        
        button_layout.addWidget(change_username_btn)
        button_layout.addWidget(change_password_btn)
        button_layout.addWidget(logout_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        settings_widget.setLayout(layout)
        self.setCentralWidget(settings_widget)
        self.setGeometry(current_geometry)

    def _change_username(self):
        """Change doctor's username."""
        new_username, ok = QInputDialog.getText(
            self, "Change Username", "Enter new username:",
            text=self._doctor.get_username()
        )
        
        if ok and new_username.strip():
            self._doctor.set_username(new_username.strip())
            self._doctor._persist_credentials()
            QMessageBox.information(self, "Success", "Username changed successfully!")
            self._show_settings()

    def _change_password(self):
        """Change doctor's password."""
        new_password, ok = QInputDialog.getText(
            self, "Change Password", "Enter new password:",
            echo=QLineEdit.Password
        )
        
        if ok and new_password.strip():
            self._doctor.set_password(new_password.strip())
            self._doctor._persist_credentials()
            QMessageBox.information(self, "Success", "Password changed successfully!")

    def _logout(self):
        """Logout and return to login window."""
        reply = QMessageBox.question(
            self, "Logout", "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.parent().show()
            self.close()


class AdminWindow(QMainWindow):
    def __init__(self, doctors, patients, parent=None):
        super().__init__(parent)
        uic.loadUi(ADMIN_UI, self)
        self._doctors = doctors
        self._patients = patients
        self._populate_dashboard()
        self._connect_menu_actions()

    def closeEvent(self, event):
        """Handle close event to properly quit the application."""
        QtWidgets.QApplication.quit()
        event.accept()

    def _connect_menu_actions(self):
        # Add actions to menus
        
        # Doctors menu - show directly when menu is about to show
        self.menuDoctors.aboutToShow.connect(self._show_doctor_management)
        
        # Patients menu
        self.menuPatients.aboutToShow.connect(self._show_patient_management)
        
        # Hospital Reports menu
        self.menuHospital_Reports.aboutToShow.connect(self._show_management_reports)
        
        # Settings menu
        self.menuSettings.aboutToShow.connect(self._show_settings)
        
        # Home menu action
        self.menuHome.aboutToShow.connect(self._show_dashboard)
    
    def _show_dashboard(self):
        """Return to dashboard view."""
        # Save current geometry
        current_geometry = self.geometry()
        
        # Reload the UI to get fresh dashboard
        uic.loadUi(ADMIN_UI, self)
        self._connect_menu_actions()
        self._populate_dashboard()
        
        # Restore geometry
        self.setGeometry(current_geometry)
    
    def _show_doctor_management(self):
        """Show doctor management in the main window."""
        
        # Save current geometry
        current_geometry = self.geometry()
        
        # Create doctor management widget
        mgmt_widget = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Doctor Management")
        title.setStyleSheet("font-size: 18pt; font-weight: 600; color: #111827; margin: 10px;")
        layout.addWidget(title)
        
        # Buttons
        button_layout = QHBoxLayout()
        register_btn = QPushButton("Register Doctor")
        update_btn = QPushButton("Update Doctor")
        delete_btn = QPushButton("Delete Doctor")
        
        register_btn.setStyleSheet("padding: 8px 16px; font-size: 11pt;")
        update_btn.setStyleSheet("padding: 8px 16px; font-size: 11pt;")
        delete_btn.setStyleSheet("padding: 8px 16px; font-size: 11pt;")
        
        register_btn.clicked.connect(self._register_doctor_inline)
        update_btn.clicked.connect(self._update_doctor_inline)
        delete_btn.clicked.connect(self._delete_doctor_inline)
        
        button_layout.addWidget(register_btn)
        button_layout.addWidget(update_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Doctor table
        self.doctor_mgmt_table = QTableWidget()
        self.doctor_mgmt_table.setColumnCount(4)
        self.doctor_mgmt_table.setHorizontalHeaderLabels(["ID", "Full Name", "Speciality", "Username"])
        self.doctor_mgmt_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._refresh_doctor_table()
        
        layout.addWidget(self.doctor_mgmt_table)
        mgmt_widget.setLayout(layout)
        
        self.setCentralWidget(mgmt_widget)
        
        # Restore geometry
        self.setGeometry(current_geometry)
    
    def _refresh_doctor_table(self):
        """Refresh the doctor management table."""
        self.doctor_mgmt_table.setRowCount(len(self._doctors))
        for row, doctor in enumerate(self._doctors):
            self.doctor_mgmt_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.doctor_mgmt_table.setItem(row, 1, QTableWidgetItem(doctor.full_name()))
            self.doctor_mgmt_table.setItem(row, 2, QTableWidgetItem(doctor.get_speciality()))
            self.doctor_mgmt_table.setItem(row, 3, QTableWidgetItem(doctor.get_username()))
    
    def _register_doctor_inline(self):
        """Register a new doctor."""
        dialog = DoctorDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            if not all([data['first_name'], data['surname'], data['speciality'], 
                       data['username'], data['password']]):
                QMessageBox.warning(self, "Invalid Input", "All fields are required.")
                return
            
            # Check if name exists
            name_exists = any(
                data['first_name'] == doctor.get_first_name() and 
                data['surname'] == doctor.get_surname() 
                for doctor in self._doctors
            )
            
            if name_exists:
                QMessageBox.warning(self, "Duplicate", "A doctor with this name already exists.")
                return
            
            # Create new doctor
            new_doctor = Doctor(
                data['first_name'], 
                data['surname'], 
                data['speciality'],
                data['username'],
                data['password']
            )
            self._doctors.append(new_doctor)
            new_doctor._persist_credentials()
            
            self._refresh_doctor_table()
            QMessageBox.information(self, "Success", "Doctor registered successfully.")
    
    def _update_doctor_inline(self):
        """Update doctor details."""
        selected_rows = self.doctor_mgmt_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a doctor to update.")
            return
        
        row = selected_rows[0].row()
        doctor = self._doctors[row]
        
        dialog = DoctorDialog(doctor=doctor, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            if not all([data['first_name'], data['surname'], data['speciality']]):
                QMessageBox.warning(self, "Invalid Input", 
                                   "First name, surname, and speciality are required.")
                return
            
            doctor.set_first_name(data['first_name'])
            doctor.set_surname(data['surname'])
            doctor.set_speciality(data['speciality'])
            
            if data['password']:
                doctor.set_password(data['password'])
            
            # Save all doctors to avoid duplicates when updating
            self._save_all_doctors()
            
            self._refresh_doctor_table()
            QMessageBox.information(self, "Success", "Doctor updated successfully.")
    
    def _delete_doctor_inline(self):
        """Delete a doctor."""
        selected_rows = self.doctor_mgmt_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a doctor to delete.")
            return
        
        row = selected_rows[0].row()
        doctor = self._doctors[row]
        
        reply = QMessageBox.question(
            self, 
            "Confirm Delete", 
            f"Are you sure you want to delete Dr. {doctor.full_name()}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            del self._doctors[row]
            self._save_all_doctors()
            self._refresh_doctor_table()
            QMessageBox.information(self, "Success", "Doctor deleted successfully.")
    
    def _save_all_doctors(self):
        """Save all doctors to doctor.txt file."""
        import base64
        header = "Full Name|Speciality|Username|Password"
        
        with open("doctor.txt", "w", encoding="utf-8") as f:
            f.write(header + "\n")
            for doctor in self._doctors:
                encoded_password = base64.b64encode(doctor.get_password().encode("utf-8")).decode("ascii")
                f.write(f"{doctor.full_name()}|{doctor.get_speciality()}|"
                       f"{doctor.get_username()}|{encoded_password}\n")
    
    def _show_patient_management(self):
        """Show patient management in the main window."""
        
        # Save current geometry
        current_geometry = self.geometry()
        
        # Create patient management widget
        mgmt_widget = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Patient Management")
        title.setStyleSheet("font-size: 18pt; font-weight: 600; color: #111827; margin: 10px;")
        layout.addWidget(title)
        
        # Row 1 Buttons
        button_layout1 = QHBoxLayout()
        add_btn = QPushButton("Add Patient")
        update_btn = QPushButton("Update Patient")
        symptoms_btn = QPushButton("View/Add Symptoms")
        assign_btn = QPushButton("Assign Doctor")
        
        add_btn.setStyleSheet("padding: 8px 16px; font-size: 11pt;")
        update_btn.setStyleSheet("padding: 8px 16px; font-size: 11pt;")
        symptoms_btn.setStyleSheet("padding: 8px 16px; font-size: 11pt;")
        assign_btn.setStyleSheet("padding: 8px 16px; font-size: 11pt;")
        
        add_btn.clicked.connect(self._add_patient_inline)
        update_btn.clicked.connect(self._update_patient_inline)
        symptoms_btn.clicked.connect(self._view_add_symptoms_inline)
        assign_btn.clicked.connect(self._assign_doctor_inline)
        
        button_layout1.addWidget(add_btn)
        button_layout1.addWidget(update_btn)
        button_layout1.addWidget(symptoms_btn)
        button_layout1.addWidget(assign_btn)
        
        # Row 2 Buttons
        button_layout2 = QHBoxLayout()
        discharge_btn = QPushButton("Discharge Patient")
        relocate_btn = QPushButton("Relocate Doctor")
        discharged_btn = QPushButton("View Discharged")
        family_btn = QPushButton("Group by Family")
        
        discharge_btn.setStyleSheet("padding: 8px 16px; font-size: 11pt;")
        relocate_btn.setStyleSheet("padding: 8px 16px; font-size: 11pt;")
        discharged_btn.setStyleSheet("padding: 8px 16px; font-size: 11pt;")
        family_btn.setStyleSheet("padding: 8px 16px; font-size: 11pt;")
        
        discharge_btn.clicked.connect(self._discharge_patient_inline)
        relocate_btn.clicked.connect(self._relocate_doctor_inline)
        discharged_btn.clicked.connect(self._view_discharged_inline)
        family_btn.clicked.connect(self._view_family_inline)
        
        button_layout2.addWidget(discharge_btn)
        button_layout2.addWidget(relocate_btn)
        button_layout2.addWidget(discharged_btn)
        button_layout2.addWidget(family_btn)
        button_layout2.addStretch()
        
        layout.addLayout(button_layout1)
        layout.addLayout(button_layout2)
        
        # Patient table
        self.patient_mgmt_table = QTableWidget()
        self.patient_mgmt_table.setColumnCount(7)
        self.patient_mgmt_table.setHorizontalHeaderLabels(["ID", "Full Name", "Age", "Mobile", "Postcode", "Symptoms", "Doctor"])
        self.patient_mgmt_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._refresh_patient_table()
        
        layout.addWidget(self.patient_mgmt_table)
        mgmt_widget.setLayout(layout)
        
        self.setCentralWidget(mgmt_widget)
        
        # Restore geometry
        self.setGeometry(current_geometry)
    
    def _refresh_patient_table(self):
        """Refresh the patient management table."""
        self.patient_mgmt_table.setRowCount(len(self._patients))
        for row, patient in enumerate(self._patients):
            self.patient_mgmt_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.patient_mgmt_table.setItem(row, 1, QTableWidgetItem(patient.full_name()))
            self.patient_mgmt_table.setItem(row, 2, QTableWidgetItem(str(patient._Patient__age)))
            self.patient_mgmt_table.setItem(row, 3, QTableWidgetItem(patient._Patient__mobile))
            self.patient_mgmt_table.setItem(row, 4, QTableWidgetItem(patient._Patient__postcode))
            self.patient_mgmt_table.setItem(row, 5, QTableWidgetItem(", ".join(patient.get_symptoms())))
            self.patient_mgmt_table.setItem(row, 6, QTableWidgetItem(patient.get_doctor()))
    
    def _add_patient_inline(self):
        """Add a new patient."""
        dialog = PatientDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            if not all([data['first_name'], data['surname'], data['age'], 
                       data['mobile'], data['postcode'], data['address'], data['symptoms']]):
                QMessageBox.warning(self, "Invalid Input", "All fields are required.")
                return
            
            try:
                age = int(data['age'])
            except ValueError:
                QMessageBox.warning(self, "Invalid Input", "Age must be a number.")
                return
            
            # Create new patient
            new_patient = Patient(
                data['first_name'], 
                data['surname'], 
                age,
                data['mobile'],
                data['postcode'],
                data['address'],
                data['symptoms']
            )
            self._patients.append(new_patient)
            Patient.append_patient_record('patients_file.txt', new_patient)
            
            self._refresh_patient_table()
            QMessageBox.information(self, "Success", "Patient added successfully.")
    
    def _update_patient_inline(self):
        """Update patient details."""
        selected_rows = self.patient_mgmt_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a patient to update.")
            return
        
        row = selected_rows[0].row()
        patient = self._patients[row]
        
        dialog = PatientDialog(patient=patient, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            if not all([data['first_name'], data['surname'], data['age'], 
                       data['mobile'], data['postcode'], data['address']]):
                QMessageBox.warning(self, "Invalid Input", "All fields except symptoms are required.")
                return
            
            try:
                age = int(data['age'])
            except ValueError:
                QMessageBox.warning(self, "Invalid Input", "Age must be a number.")
                return
            
            patient.set_first_name(data['first_name'])
            patient.set_surname(data['surname'])
            patient._Patient__age = age
            patient._Patient__mobile = data['mobile']
            patient._Patient__postcode = data['postcode']
            patient._Patient__address = data['address']
            if data['symptoms']:
                patient.set_symptoms([s.strip() for s in data['symptoms'].split(',')])
            
            self._save_all_patients()
            self._refresh_patient_table()
            QMessageBox.information(self, "Success", "Patient updated successfully.")
    
    def _discharge_patient_inline(self):
        """Discharge a patient."""
        selected_rows = self.patient_mgmt_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a patient to discharge.")
            return
        
        row = selected_rows[0].row()
        patient = self._patients[row]
        
        reply = QMessageBox.question(
            self, 
            "Confirm Discharge", 
            f"Are you sure you want to discharge {patient.full_name()}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            Patient.append_discharged_patient(patient)
            del self._patients[row]
            self._save_all_patients()
            self._refresh_patient_table()
            QMessageBox.information(self, "Success", "Patient discharged successfully.")
    
    def _save_all_patients(self):
        """Save all patients to patients_file.txt."""
        with open('patients_file.txt', 'w') as f:
            f.write("Full Name|Age|Mobile|Postcode|Address|Symptoms|Doctor\n")
        for patient in self._patients:
            Patient.append_patient_record('patients_file.txt', patient)

    def _view_add_symptoms_inline(self):
        """View or add symptoms for a patient."""
        selected_rows = self.patient_mgmt_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a patient.")
            return
        
        row = selected_rows[0].row()
        patient = self._patients[row]
        
        # Ask what to do
        msg = QMessageBox(self)
        msg.setWindowTitle("Symptoms Options")
        msg.setText(f"What would you like to do for {patient.full_name()}?")
        view_btn = msg.addButton("View Symptoms", QMessageBox.ActionRole)
        add_btn = msg.addButton("Add Symptoms", QMessageBox.ActionRole)
        cancel_btn = msg.addButton("Cancel", QMessageBox.RejectRole)
        msg.exec_()
        
        if msg.clickedButton() == view_btn:
            symptoms = patient.get_symptoms()
            if symptoms:
                QMessageBox.information(
                    self, 
                    "Patient Symptoms", 
                    f"Symptoms for {patient.full_name()}:\n\n" + "\n".join(f"• {s}" for s in symptoms)
                )
            else:
                QMessageBox.information(self, "No Symptoms", "This patient has no symptoms recorded.")
        
        elif msg.clickedButton() == add_btn:
            current_symptoms = ", ".join(patient.get_symptoms())
            text, ok = QInputDialog.getText(
                self,
                "Add Symptoms",
                f"Current symptoms: {current_symptoms}\n\nEnter new symptoms to add:",
                QLineEdit.Normal
            )
            
            if ok and text:
                patient.add_symptoms(text)
                self._save_all_patients()
                self._refresh_patient_table()
                QMessageBox.information(self, "Success", "Symptoms added successfully.")

    def _assign_doctor_inline(self):
        """Assign a doctor to a patient."""
        selected_rows = self.patient_mgmt_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a patient.")
            return
        
        row = selected_rows[0].row()
        patient = self._patients[row]
        
        # Check if already assigned
        if patient.get_doctor() != "None":
            QMessageBox.warning(
                self, 
                "Already Assigned", 
                f"This patient is already assigned to Dr. {patient.get_doctor()}.\nUse 'Relocate Doctor' option to change."
            )
            return
        
        # Show doctor selection dialog
        doctor_names = [f"{i+1}. {d.full_name()} - {d.get_speciality()}" for i, d in enumerate(self._doctors)]
        doctor_name, ok = QInputDialog.getItem(
            self,
            "Select Doctor",
            f"Patient symptoms: {', '.join(patient.get_symptoms())}\n\nSelect doctor:",
            doctor_names,
            0,
            False
        )
        
        if ok:
            doctor_index = doctor_names.index(doctor_name)
            doctor = self._doctors[doctor_index]
            
            # Get appointment details
            from datetime import datetime
            
            # Simple dialog for appointment date/time
            date_str, ok = QInputDialog.getText(
                self,
                "Appointment Date",
                "Enter appointment date (YYYY-MM-DD):",
                QLineEdit.Normal,
                "2026-02-20"
            )
            
            if not ok:
                return
            
            time_str, ok = QInputDialog.getText(
                self,
                "Appointment Time",
                "Enter appointment time (HH:MM):",
                QLineEdit.Normal,
                "10:00"
            )
            
            if not ok:
                return
            
            try:
                appointment_date = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                
                # Assign doctor
                patient.link(doctor.full_name(), appointment_date)
                doctor.add_patient(patient.full_name())
                doctor.add_appointment(appointment_date)
                
                # Save appointment to file
                appointment_file = f"{appointment_date.year}_appointments.txt"
                import os
                if not os.path.exists(appointment_file):
                    with open(appointment_file, 'w') as f:
                        f.write("Patient Name|Doctor Name|Appointment DateTime\n")
                
                with open(appointment_file, 'a') as f:
                    f.write(f"{patient.full_name()}|{doctor.full_name()}|{appointment_date.strftime('%Y/%m/%d %H:%M')}\n")
                
                self._save_all_patients()
                self._refresh_patient_table()
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"Patient assigned to Dr. {doctor.full_name()} on {appointment_date.strftime('%Y/%m/%d %H:%M')}"
                )
            except ValueError as e:
                QMessageBox.warning(self, "Invalid Date/Time", f"Please enter valid date and time.\nError: {e}")

    def _view_discharged_inline(self):
        """View discharged patients."""
        try:
            with open('discharged_patient.txt', 'r') as f:
                lines = f.readlines()[1:]  # Skip header
            
            if not lines:
                QMessageBox.information(self, "No Discharged Patients", "There are no discharged patients.")
                return
            
            # Create dialog to show discharged patients
            dialog = QDialog(self)
            dialog.setWindowTitle("Discharged Patients")
            dialog.resize(800, 400)
            
            layout = QVBoxLayout()
            
            table = QTableWidget()
            table.setColumnCount(7)
            table.setHorizontalHeaderLabels(["ID", "Full Name", "Age", "Mobile", "Postcode", "Symptoms", "Doctor"])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.setRowCount(len(lines))
            
            for row, line in enumerate(lines):
                parts = line.strip().split('|')
                if len(parts) >= 7:
                    table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
                    table.setItem(row, 1, QTableWidgetItem(parts[0]))
                    table.setItem(row, 2, QTableWidgetItem(parts[1]))
                    table.setItem(row, 3, QTableWidgetItem(parts[2]))
                    table.setItem(row, 4, QTableWidgetItem(parts[3]))
                    table.setItem(row, 5, QTableWidgetItem(parts[5]))
                    table.setItem(row, 6, QTableWidgetItem(parts[6]))
            
            layout.addWidget(table)
            
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.close)
            layout.addWidget(close_btn)
            
            dialog.setLayout(layout)
            dialog.exec_()
            
        except FileNotFoundError:
            QMessageBox.information(self, "No Discharged Patients", "There are no discharged patients.")

    def _view_family_inline(self):
        """View patients grouped by family."""
        same_family = {}
        for patient in self._patients:
            patient_surname = patient.get_surname()
            same_family.setdefault(patient_surname, []).append(patient)
        
        if not same_family:
            QMessageBox.information(self, "No Patients", "There are no patients to group.")
            return
        
        # Create dialog to show family groups
        dialog = QDialog(self)
        dialog.setWindowTitle("Patients Grouped by Family")
        dialog.resize(700, 500)
        
        layout = QVBoxLayout()
        
        # Create text browser to display families
        from PyQt5.QtWidgets import QTextBrowser
        text_browser = QTextBrowser()
        
        content = "<h2>Patients Grouped by Family</h2>"
        for family_name, family_members in sorted(same_family.items()):
            content += f"<h3>Family: {family_name}</h3><ul>"
            for patient in family_members:
                content += f"<li>{patient.full_name()} - Age: {patient._Patient__age}, Doctor: {patient.get_doctor()}</li>"
            content += "</ul>"
        
        text_browser.setHtml(content)
        layout.addWidget(text_browser)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def _show_management_reports(self):
        """Show management reports options in the main window."""
        
        # Save current geometry
        current_geometry = self.geometry()
        
        # Create reports widget
        reports_widget = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Management Reports")
        title.setStyleSheet("font-size: 18pt; font-weight: 600; color: #111827; margin: 10px;")
        layout.addWidget(title)
        
        # Row 1 Buttons
        button_layout1 = QHBoxLayout()
        total_doctors_btn = QPushButton("Total Doctors")
        patients_per_doctor_btn = QPushButton("Patients per Doctor")
        appointments_per_month_btn = QPushButton("Appointments per Month")
        
        total_doctors_btn.setStyleSheet("padding: 12px 16px; font-size: 11pt;")
        patients_per_doctor_btn.setStyleSheet("padding: 12px 16px; font-size: 11pt;")
        appointments_per_month_btn.setStyleSheet("padding: 12px 16px; font-size: 11pt;")
        
        total_doctors_btn.clicked.connect(self._report_total_doctors)
        patients_per_doctor_btn.clicked.connect(self._report_patients_per_doctor)
        appointments_per_month_btn.clicked.connect(self._report_appointments_per_month)
        
        button_layout1.addWidget(total_doctors_btn)
        button_layout1.addWidget(patients_per_doctor_btn)
        button_layout1.addWidget(appointments_per_month_btn)
        
        # Row 2 Buttons
        button_layout2 = QHBoxLayout()
        patients_by_symptom_btn = QPushButton("Patients by Symptom")
        all_appointments_btn = QPushButton("All Appointments")
        
        patients_by_symptom_btn.setStyleSheet("padding: 12px 16px; font-size: 11pt;")
        all_appointments_btn.setStyleSheet("padding: 12px 16px; font-size: 11pt;")
        
        patients_by_symptom_btn.clicked.connect(self._report_patients_by_symptom)
        all_appointments_btn.clicked.connect(self._report_all_appointments)
        
        button_layout2.addWidget(patients_by_symptom_btn)
        button_layout2.addWidget(all_appointments_btn)
        button_layout2.addStretch()
        
        layout.addLayout(button_layout1)
        layout.addLayout(button_layout2)
        
        # Info label
        info = QLabel("Click a button above to generate a report")
        info.setStyleSheet("font-size: 12pt; color: #6b7280; margin: 20px; text-align: center;")
        layout.addWidget(info)
        
        layout.addStretch()
        
        reports_widget.setLayout(layout)
        self.setCentralWidget(reports_widget)
        
        # Restore geometry
        self.setGeometry(current_geometry)
    
    def _report_total_doctors(self):
        """Generate report for total number of doctors."""
        # Close all existing figures first
        plt.close('all')
        
        total_doctors = len(self._doctors)
        
        # Count doctors by speciality
        speciality_counts = {}
        for doctor in self._doctors:
            speciality = doctor.get_speciality()
            speciality_counts[speciality] = speciality_counts.get(speciality, 0) + 1
        
        # Create visualization with unique figure
        fig = plt.figure(num="Total Doctors Report", figsize=(14, 6))
        ax1, ax2 = fig.subplots(1, 2)
        
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
        
        # Get figure manager and prevent it from closing the app
        fig_manager = plt.get_current_fig_manager()
        if fig_manager is not None and hasattr(fig_manager, 'window'):
            # Prevent the figure window from closing the entire application
            def closeEvent(event):
                event.accept()  # Just close the figure window, don't quit the app
            fig_manager.window.closeEvent = closeEvent
        
        plt.show(block=False)
        
        QMessageBox.information(
            self, 
            "Total Doctors Report", 
            f"Total number of doctors: {total_doctors}\n\nChart displayed separately."
        )
    
    def _report_patients_per_doctor(self):
        """Generate report for patients per doctor."""
        # Close all existing figures first
        plt.close('all')
        
        doctor_names = []
        total_patients_list = []
        
        for doctor in self._doctors:
            total_patients = doctor.get_total_patients()
            doctor_names.append(doctor.full_name())
            total_patients_list.append(total_patients)
        
        if doctor_names:
            # Create bar chart with colors
            fig = plt.figure(num="Patients per Doctor Report", figsize=(12, 6))
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
            
            # Get figure manager and prevent it from closing the app
            fig_manager = plt.get_current_fig_manager()
            if fig_manager is not None and hasattr(fig_manager, 'window'):
                # Prevent the figure window from closing the entire application
                def closeEvent(event):
                    event.accept()  # Just close the figure window, don't quit the app
                fig_manager.window.closeEvent = closeEvent
            
            plt.show(block=False)
            
            # Show summary
            summary = "Patients per Doctor:\n\n"
            for name, count in zip(doctor_names, total_patients_list):
                summary += f"{name}: {count} patients\n"
            
            QMessageBox.information(self, "Patients per Doctor Report", summary + "\nChart displayed separately.")
        else:
            QMessageBox.information(self, "No Data", "No doctors found.")
    
    def _report_appointments_per_month(self):
        """Generate report for appointments per month per doctor."""
        # Close all existing figures first
        plt.close('all')
        
        import glob
        
        appointments_data = {}
        APPOINTMENT_HEADER = "Patient Name|Doctor Name|Appointment DateTime"
        
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
            # Create visualization with unique figure
            fig = plt.figure(num="Appointments per Month Report", figsize=(14, 8))
            ax = fig.add_subplot(111)
            
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
            
            # Get figure manager and prevent it from closing the app
            fig_manager = plt.get_current_fig_manager()
            if fig_manager is not None and hasattr(fig_manager, 'window'):
                # Prevent the figure window from closing the entire application
                def closeEvent(event):
                    event.accept()  # Just close the figure window, don't quit the app
                fig_manager.window.closeEvent = closeEvent
            
            plt.show(block=False)
            
            QMessageBox.information(self, "Appointments Report", "Appointments per month chart displayed.")
        else:
            QMessageBox.information(self, "No Data", "No appointments found.")
    
    def _report_patients_by_symptom(self):
        """Generate report for patients by symptom type."""
        # Close all existing figures first
        plt.close('all')
        
        symptom_counts = {}
        for patient in self._patients:
            for symptom in patient.get_symptoms():
                symptom = symptom.strip()
                if symptom:
                    symptom_counts[symptom] = symptom_counts.get(symptom, 0) + 1

        if symptom_counts:
            # Prepare data for visualization
            symptom_names = list(symptom_counts.keys())
            pt_wt_symp = list(symptom_counts.values())

            # Create a more appealing visualization with unique figure
            fig = plt.figure(num="Patients by Symptom Report", figsize=(16, 6))
            ax1, ax2 = fig.subplots(1, 2)
            
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
            
            # Get figure manager and prevent it from closing the app
            fig_manager = plt.get_current_fig_manager()
            if fig_manager is not None and hasattr(fig_manager, 'window'):
                # Prevent the figure window from closing the entire application
                def closeEvent(event):
                    event.accept()  # Just close the figure window, don't quit the app
                fig_manager.window.closeEvent = closeEvent
            
            plt.show(block=False)
            
            # Show summary
            summary = "Patients per Symptom:\n\n"
            for symptom, count in sorted(symptom_counts.items(), key=lambda x: x[1], reverse=True):
                summary += f"{symptom}: {count} patients\n"
            
            QMessageBox.information(self, "Patients by Symptom Report", summary + "\nChart displayed separately.")
        else:
            QMessageBox.information(self, "No Data", "No symptoms data available.")
    
    def _report_all_appointments(self):
        """Generate report showing all appointments."""
        import glob
        
        appointments = {}
        
        # Read appointments from all year-specific files
        appointment_files = glob.glob('*_appointments.txt')
        
        if not appointment_files:
            QMessageBox.information(self, "No Data", "No appointment files found.")
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
                            
                            # Skip header
                            if patient_name == "Patient Name":
                                continue
                            
                            # Parse date to get year and month
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
            QMessageBox.information(self, "No Data", "No appointments found.")
            return
        
        # Create dialog to show appointments
        dialog = QDialog(self)
        dialog.setWindowTitle("All Appointments")
        dialog.resize(900, 600)
        
        layout = QVBoxLayout()
        
        # Create text browser to display appointments
        text_browser = QTextBrowser()
        
        content = "<h2>All Appointments</h2>"
        for year_month in sorted(appointments.keys()):
            year, month = year_month.split('/')
            month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                        'July', 'August', 'September', 'October', 'November', 'December']
            month_name = month_names[int(month)]
            
            content += f"<h3>{month_name} {year}</h3>"
            content += "<table border='1' cellpadding='5' cellspacing='0' width='100%'>"
            content += "<tr><th>Patient Name</th><th>Doctor Name</th><th>Appointment Date/Time</th></tr>"
            
            for appointment in appointments[year_month]:
                content += f"<tr><td>{appointment['patient']}</td><td>{appointment['doctor']}</td><td>{appointment['datetime']}</td></tr>"
            
            content += "</table><br>"
        
        text_browser.setHtml(content)
        layout.addWidget(text_browser)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def _relocate_doctor_inline(self):
        """Relocate doctor or update appointment for a patient."""
        selected_rows = self.patient_mgmt_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a patient.")
            return
        
        row = selected_rows[0].row()
        patient = self._patients[row]
        
        # Check if patient has a doctor assigned
        if patient.get_doctor() == "None":
            QMessageBox.warning(
                self, 
                "No Doctor Assigned", 
                "This patient has no doctor assigned yet. Please use 'Assign Doctor' first."
            )
            return
        
        # Ask what to do
        msg = QMessageBox(self)
        msg.setWindowTitle("Relocate/Update Options")
        msg.setText(f"Current doctor: Dr. {patient.get_doctor()}\n\nWhat would you like to do?")
        relocate_btn = msg.addButton("Relocate to Different Doctor", QMessageBox.ActionRole)
        update_btn = msg.addButton("Update Appointment Only", QMessageBox.ActionRole)
        cancel_btn = msg.addButton("Cancel", QMessageBox.RejectRole)
        msg.exec_()
        
        if msg.clickedButton() == relocate_btn:
            # Relocate to different doctor
            doctor_names = [f"{i+1}. {d.full_name()} - {d.get_speciality()}" for i, d in enumerate(self._doctors)]
            doctor_name, ok = QInputDialog.getItem(
                self,
                "Select New Doctor",
                f"Patient symptoms: {', '.join(patient.get_symptoms())}\n\nSelect new doctor:",
                doctor_names,
                0,
                False
            )
            
            if not ok:
                return
            
            doctor_index = doctor_names.index(doctor_name)
            new_doctor = self._doctors[doctor_index]
            
            # Get appointment details
            from datetime import datetime
            
            date_str, ok = QInputDialog.getText(
                self,
                "Appointment Date",
                "Enter appointment date (YYYY-MM-DD):",
                QLineEdit.Normal,
                "2026-02-20"
            )
            
            if not ok:
                return
            
            time_str, ok = QInputDialog.getText(
                self,
                "Appointment Time",
                "Enter appointment time (HH:MM):",
                QLineEdit.Normal,
                "10:00"
            )
            
            if not ok:
                return
            
            try:
                appointment_date = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                
                old_doctor_name = patient.get_doctor()
                
                # Update patient's doctor and appointment
                patient.link(new_doctor.full_name(), appointment_date)
                new_doctor.add_patient(patient.full_name())
                
                # Save appointment to file
                appointment_file = f"{appointment_date.year}_appointments.txt"
                import os
                if not os.path.exists(appointment_file):
                    with open(appointment_file, 'w') as f:
                        f.write("Patient Name|Doctor Name|Appointment DateTime\n")
                
                with open(appointment_file, 'a') as f:
                    f.write(f"{patient.full_name()}|{new_doctor.full_name()}|{appointment_date.strftime('%Y/%m/%d %H:%M')}\n")
                
                self._save_all_patients()
                self._refresh_patient_table()
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"Successfully relocated from Dr. {old_doctor_name} to Dr. {new_doctor.full_name()} on {appointment_date.strftime('%Y/%m/%d %H:%M')}"
                )
            except ValueError as e:
                QMessageBox.warning(self, "Invalid Date/Time", f"Please enter valid date and time.\nError: {e}")
        
        elif msg.clickedButton() == update_btn:
            # Update appointment only
            from datetime import datetime
            
            date_str, ok = QInputDialog.getText(
                self,
                "Appointment Date",
                "Enter new appointment date (YYYY-MM-DD):",
                QLineEdit.Normal,
                "2026-02-20"
            )
            
            if not ok:
                return
            
            time_str, ok = QInputDialog.getText(
                self,
                "Appointment Time",
                "Enter new appointment time (HH:MM):",
                QLineEdit.Normal,
                "10:00"
            )
            
            if not ok:
                return
            
            try:
                appointment_date = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                doctor_name = patient.get_doctor()
                
                patient.appointment_date = appointment_date
                
                # Save updated appointment to file
                appointment_file = f"{appointment_date.year}_appointments.txt"
                import os
                if not os.path.exists(appointment_file):
                    with open(appointment_file, 'w') as f:
                        f.write("Patient Name|Doctor Name|Appointment DateTime\n")
                
                with open(appointment_file, 'a') as f:
                    f.write(f"{patient.full_name()}|{doctor_name}|{appointment_date.strftime('%Y/%m/%d %H:%M')} (Updated)\n")
                
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"Appointment updated to {appointment_date.strftime('%Y/%m/%d %H:%M')} with Dr. {doctor_name}"
                )
            except ValueError as e:
                QMessageBox.warning(self, "Invalid Date/Time", f"Please enter valid date and time.\nError: {e}")

    def _show_settings(self):
        """Show admin settings options in the main window."""
        
        # Save current geometry
        current_geometry = self.geometry()
        
        # Create settings widget
        settings_widget = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Admin Settings")
        title.setStyleSheet("font-size: 18pt; font-weight: 600; color: #111827; margin: 10px;")
        layout.addWidget(title)
        
        # Buttons
        button_layout = QHBoxLayout()
        change_username_btn = QPushButton("Change Username")
        change_password_btn = QPushButton("Change Password")
        logout_btn = QPushButton("Logout")
        
        change_username_btn.setStyleSheet("padding: 12px 16px; font-size: 11pt;")
        change_password_btn.setStyleSheet("padding: 12px 16px; font-size: 11pt;")
        logout_btn.setStyleSheet("padding: 12px 16px; font-size: 11pt; background-color: #dc2626;")
        
        change_username_btn.clicked.connect(self._change_username)
        change_password_btn.clicked.connect(self._change_password)
        logout_btn.clicked.connect(self._logout)
        
        button_layout.addWidget(change_username_btn)
        button_layout.addWidget(change_password_btn)
        button_layout.addWidget(logout_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Info label
        info = QLabel("Manage your admin account settings")
        info.setStyleSheet("font-size: 12pt; color: #6b7280; margin: 20px; text-align: center;")
        layout.addWidget(info)
        
        layout.addStretch()
        
        settings_widget.setLayout(layout)
        self.setCentralWidget(settings_widget)
        
        # Restore geometry
        self.setGeometry(current_geometry)
    
    def _change_username(self):
        """Change admin username."""
        new_username, ok = QInputDialog.getText(
            self,
            "Change Username",
            "Enter new username:",
            QLineEdit.Normal
        )
        
        if ok and new_username:
            new_username = new_username.strip()
            if not new_username:
                QMessageBox.warning(self, "Invalid Input", "Username cannot be empty.")
                return
            
            # Update admin username
            from Main import load_admin
            admin = load_admin()
            admin._Admin__username = new_username
            admin._persist_credentials()
            
            QMessageBox.information(self, "Success", "Username updated successfully.")
        elif ok:
            QMessageBox.warning(self, "Invalid Input", "Username cannot be empty.")
    
    def _change_password(self):
        """Change admin password."""
        # Get current password
        current_password, ok = QInputDialog.getText(
            self,
            "Change Password",
            "Enter current password:",
            QLineEdit.Password
        )
        
        if not ok:
            return
        
        # Verify current password
        from Main import load_admin
        admin = load_admin()
        if current_password != admin.get_password():
            QMessageBox.warning(self, "Error", "Current password is incorrect.")
            return
        
        # Get new password
        new_password, ok = QInputDialog.getText(
            self,
            "Change Password",
            "Enter new password:",
            QLineEdit.Password
        )
        
        if not ok:
            return
        
        if not new_password:
            QMessageBox.warning(self, "Invalid Input", "Password cannot be empty.")
            return
        
        # Confirm new password
        confirm_password, ok = QInputDialog.getText(
            self,
            "Change Password",
            "Re-enter new password:",
            QLineEdit.Password
        )
        
        if not ok:
            return
        
        if new_password != confirm_password:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return
        
        # Update password
        admin._Admin__password = new_password
        admin._persist_credentials()
        
        QMessageBox.information(self, "Success", "Password updated successfully.")
    
    def _logout(self):
        """Logout and return to login screen."""
        reply = QMessageBox.question(
            self,
            "Confirm Logout",
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Close this window and show login window
            self.close()
            
            # The parent should be the login window
            if self.parent():
                self.parent().show()

    def _populate_dashboard(self):
        self.lcdNumber.display(len(self._doctors))
        self.lcdNumber_2.display(len(self._patients))

        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.tableWidget.setRowCount(len(self._doctors))
        for row_index, doctor in enumerate(self._doctors):
            self.tableWidget.setItem(row_index, 0, QTableWidgetItem(str(row_index + 1)))
            self.tableWidget.setItem(row_index, 1, QTableWidgetItem(doctor.full_name()))
            self.tableWidget.setItem(row_index, 2, QTableWidgetItem(doctor.get_speciality()))


class LoginWindow(QMainWindow):
    def __init__(self, loading_screen=None):
        super().__init__()
        uic.loadUi(LOGIN_UI, self)
        self.lineEdit_3.setEchoMode(QtWidgets.QLineEdit.Password)
        self.pushButton.clicked.connect(self._handle_login)

        # Load data with progress updates
        if loading_screen:
            loading_screen.update_progress(20, "Loading administrator data...")
            time.sleep(0.5)  # Delay to show progress
        self._admin = load_admin()
        
        if loading_screen:
            loading_screen.update_progress(50, "Loading doctors data...")
            time.sleep(0.5)  # Delay to show progress
        self._doctors = load_doctors()
        
        if loading_screen:
            loading_screen.update_progress(80, "Loading patients data...")
            time.sleep(0.5)  # Delay to show progress
        self._patients = self._load_patients()
        
        if loading_screen:
            loading_screen.update_progress(100, "Loading complete!")
            time.sleep(0.3)  # Brief pause before closing

        self._admin_window = None

    def closeEvent(self, event):
        """Handle close event to properly quit the application."""
        QtWidgets.QApplication.quit()
        event.accept()

    def _load_patients(self):
        patients_file = os.path.join(BASE_DIR, "patients_file.txt")
        if not os.path.exists(patients_file) or os.path.getsize(patients_file) == 0:
            return []
        return Patient.read_patient_records(patients_file)

    def _handle_login(self):
        username = self.lineEdit.text().strip()
        password = self.lineEdit_3.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Please enter username and password.")
            return

        if self._admin.get_username() == username and self._admin.get_password() == password:
            self._admin_window = AdminWindow(self._doctors, self._patients, parent=self)
            self._admin_window.show()
            self.hide()
            return

        for doctor in self._doctors:
            if doctor.get_username() == username and doctor.get_password() == password:
                self._doctor_window = DoctorWindow(doctor, self._patients, parent=self)
                self._doctor_window.show()
                self.hide()
                return

        QMessageBox.warning(self, "Login Failed", "Incorrect username or password.")


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Prevent app from quitting when matplotlib figures close
    
    # Show loading screen
    loading_screen = LoadingScreen()
    loading_screen.show()
    loading_screen.update_progress(10, "Initializing application...")
    QtWidgets.QApplication.processEvents()
    time.sleep(0.5)  # Initial delay
    
    # Load main window with progress updates
    window = LoginWindow(loading_screen)
    
    # Close loading screen and show login window
    loading_screen.close()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
