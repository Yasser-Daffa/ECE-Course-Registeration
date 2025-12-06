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

    def __init__(self, user_data, parent=None):
        """
        admin_user_data → (user_id, name, email, program, state, account_status)
        """
        super().__init__(parent)

        # Setup UI
        self.ui = Ui_Profile()
        self.ui.setupUi(self)

        # Store DB and user info
        self.db = db
        self.user_id = user_data[0]
        self.name = user_data[1]
        self.email = user_data[2]
        self.program = user_data[3]  # unused for admin but kept for consistency

        # Load data into UI
        self.load_initial_data()

        # # Connect buttons
        # self.ui.buttonEdit.clicked.connect(self.request_email_verification)
        # self.ui.buttonSave.clicked.connect(self.save_changes)
        # self.ui.buttonCancel.clicked.connect(self.cancel_edit)
        # self.ui.buttonChangePassword.clicked.connect(self.change_password)

        # # Lock UI initially
        # self.disable_edit_mode()

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


