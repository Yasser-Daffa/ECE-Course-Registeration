# class_profile_widget.py

import os
import sys

from PyQt6.QtWidgets import QWidget, QDialog
from PyQt6.QtCore import Qt

from app_ui.admin_ui.submenus_ui.ui_profile import Ui_Profile
from helper_files.shared_utilities import info, warning, error
from helper_files.validators import validate_email, hash_password

from admin.class_admin_utilities import db
from login_files.class_authentication_window import AuthenticationWindow


class ProfileWidget(QWidget):
    """
    Full Profile Widget:
    - Loads Ui_Profile
    - Handles email verification before edit
    - Allows editing admin name/email
    - Allows password change via dialog
    - Writes updates to DB using update_user()
    """

    def __init__(self, admin_user_data, parent=None):
        """
        admin_user_data → (user_id, name, email, program, state, account_status)
        """
        super().__init__(parent)

        # Setup UI
        self.ui = Ui_Profile()
        self.ui.setupUi(self)

        # Store DB and user info
        self.db = db
        self.admin_id = admin_user_data[0]
        self.name = admin_user_data[1]
        self.email = admin_user_data[2]
        self.program = admin_user_data[3]  # unused for admin but kept for consistency

        # Load data into UI
        self.load_initial_data()

        # Connect buttons
        self.ui.buttonEdit.clicked.connect(self.request_email_verification)
        self.ui.buttonSave.clicked.connect(self.save_changes)
        self.ui.buttonCancel.clicked.connect(self.cancel_edit)
        self.ui.buttonChangePassword.clicked.connect(self.change_password)

        # Lock UI initially
        self.disable_edit_mode()

    # ---------------------------------------------------------
    # INITIAL DATA
    # ---------------------------------------------------------
    def load_initial_data(self):
        self.ui.lineEditName.setText(self.name)
        self.ui.lineEditEmail.setText(self.email)

        # Department static for all users
        self.ui.lineEditDepartment.setText("Electrical and Computer Engineering")

        # Password is masked placeholder
        self.ui.lineEditPassword.setText("••••••••")

    # ---------------------------------------------------------
    # ENABLE/DISABLE EDIT MODE
    # ---------------------------------------------------------
    def enable_edit_mode(self):
        editable = [
            self.ui.lineEditName,
            self.ui.lineEditEmail,
        ]

        for f in editable:
            f.setReadOnly(False)

        self.ui.buttonChangePassword.setEnabled(True)
        self.ui.buttonSave.setEnabled(True)
        self.ui.buttonCancel.setEnabled(True)
        self.ui.buttonEdit.setEnabled(False)

    def disable_edit_mode(self):
        all_fields = [
            self.ui.lineEditName,
            self.ui.lineEditEmail,
            self.ui.lineEditDepartment,
            self.ui.lineEditPassword
        ]

        for f in all_fields:
            f.setReadOnly(True)

        self.ui.buttonChangePassword.setEnabled(False)
        self.ui.buttonSave.setEnabled(False)
        self.ui.buttonCancel.setEnabled(False)
        self.ui.buttonEdit.setEnabled(True)

    # ---------------------------------------------------------
    # STEP 1 — EMAIL VERIFICATION
    # ---------------------------------------------------------
    def request_email_verification(self):
        """
        Opens AuthenticationWindow in profile-edit mode.
        Only allows editing after email is validated.
        """
        auth = AuthenticationWindow()
        auth.start_profile_edit_verification(self.email)

        result = auth.exec()

        if result == QDialog.Accepted:
            self.enable_edit_mode()
        else:
            warning("Verification Failed", "Email verification was not completed.")

    # ---------------------------------------------------------
    # STEP 2 — PASSWORD CHANGE
    # ---------------------------------------------------------
    def change_password(self):
        """
        Uses AuthenticationWindow's password change dialog.
        """
        auth = AuthenticationWindow()
        dialog = auth.change_password_page

        # Connect change button to apply password
        dialog.ui.buttonChangePassword.clicked.connect(
            lambda: self._apply_password_change(auth, dialog)
        )

        dialog.exec()

    def _apply_password_change(self, auth, dialog):
        new_pw = dialog.ui.lineEditPassword.text().strip()

        if not new_pw:
            warning("Invalid Password", "Password cannot be empty.")
            return

        hashed = hash_password(new_pw)
        result = self.db.update_user(self.admin_id, password=hashed)

        if "successfully" in result.lower():
            info("Success", "Password updated successfully.")
            dialog.accept()
        else:
            error("Error", result)

    # ---------------------------------------------------------
    # STEP 3 — SAVE CHANGES
    # ---------------------------------------------------------
    def save_changes(self):
        new_name = self.ui.lineEditName.text().strip()
        new_email = self.ui.lineEditEmail.text().strip()

        if not new_name or not new_email:
            warning("Missing Info", "Name and email cannot be empty.")
            return

        # Validate email format
        email_error = validate_email(new_email)
        if email_error:
            warning("Invalid Email", email_error)
            return

        # Update database
        result = self.db.update_user(
            self.admin_id,
            name=new_name,
            email=new_email
        )

        if "successfully" in result.lower():
            info("Success", "Profile updated successfully.")

            # Sync internal values
            self.name = new_name
            self.email = new_email

            self.disable_edit_mode()
        else:
            error("Error", result)

    # ---------------------------------------------------------
    # CANCEL EDIT
    # ---------------------------------------------------------
    def cancel_edit(self):
        """Restore original values and re-lock UI."""
        self.ui.lineEditName.setText(self.name)
        self.ui.lineEditEmail.setText(self.email)
        self.disable_edit_mode()
