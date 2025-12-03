from PyQt6.QtCore import Qt, QEvent, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QColor, QIcon, QPalette

from PyQt6.QtWidgets import QApplication, QWidget, QGraphicsDropShadowEffect, QFrame, QHBoxLayout, QPushButton

from ui_create_account_widget import Ui_CreateAccountWidget
from login_helper_functions import BaseLoginForm
import login_resources_rc


# from helper_functions_v2 import all_fields_filled, passwords_match


class CreateAccountWidget(BaseLoginForm):
    def __init__(self, ):
        super().__init__()
        self.ui = Ui_CreateAccountWidget()
        self.ui.setupUi(self)  # setup the UI on this QWidget


        # Store frequently used widgets in shortcuts
        self.buttonCreateAccont = self.ui.buttonCreateAccount
        self.fullName = self.ui.lineEditFullName
        self.email = self.ui.lineEditEmail
        self.password = self.ui.lineEditPassword
        self.confirm = self.ui.lineEditPasswordConfirm
        self.comboBoxProgram = self.ui.comboBoxSelectProgram
        self.buttonLoginHere = self.ui.buttonLoginHere

        # pwrd authenticatuiins
        self.progressBarPwrdStrength = self.ui.progressBarPwrdStrength
        self.labelPwrdStrengthStatus = self.ui.labelPwrdStrengthStatus
        self.labelPasswordRules = self.ui.labelPasswordRules
        


        # Disable mouse wheel scrolling for this combobox to avoid annoyance
        self.ui.comboBoxSelectProgram.wheelEvent = lambda event: event.ignore()


        # Add shadows
        self.add_shadow(self.buttonCreateAccont)
        self.add_shadow(self.ui.loginPanel, blur=25, yOffset=5, color=(0, 0, 0, 120))

        # Disable button initially (till values are filled)
        self.buttonCreateAccont.setEnabled(False)
        self.buttonCreateAccont.setToolTip("Please make sure all required fields are filled.")

        
        # Here every time the user types, deletes, or edits text in any of those fields;
        # The method create_acc_button_state is automatically called
        # Placed in a list for easier readablilty
        # Connecting field changes to button state update
        for lineEdits in [
            self.fullName,
            self.email,
            self.password,
            self.confirm
            ]:

            lineEdits.textChanged.connect(self.update_create_btn_state)

        self.comboBoxProgram.currentIndexChanged.connect(self.update_create_btn_state)

    
        # Highlight combobox only on user interaction
        self.comboBoxProgram.activated.connect(lambda: self.attach_combobox_validator(self.comboBoxProgram))

        
        # --- Creating Show/hide password toggle button ---
        # False to keep password hidden by default
        self.show_password = False
        self.show_password_confirm = False


        # Create toggle buttons for password fields
        self.create_pwrd_toggle_button(self.ui.lineEditPassword)
        self.create_pwrd_toggle_button(self.ui.lineEditPasswordConfirm)

        
        # Save original style for confirm password line edit
        self.original_confirm_style = self.ui.lineEditPasswordConfirm.styleSheet()

        # Connect password matching validation
        self.attach_confirm_password_validator(self.password, self.confirm)

        # For the password strength and validation
        self.attach_password_strength_checker(
            self.password,
            self.progressBarPwrdStrength,
            self.labelPwrdStrengthStatus,
            self.labelPasswordRules
            )

    
    def update_create_btn_state(self):
        """Enable create button only if all fields are filled, passwords match, and combobox valid."""
        from login_helper_functions import all_fields_filled, passwords_match

        fields_ok = all_fields_filled([
            self.fullName.text().strip(),
            self.email.text().strip(),
            self.password.text(),
            self.confirm.text()
        ])
        passwords_ok = passwords_match(self.password.text(), self.confirm.text())
        program_ok = self.validate_combobox_selection(self.comboBoxProgram)

        if fields_ok and passwords_ok and program_ok:
            self.buttonCreateAccont.setEnabled(True)
            self.buttonCreateAccont.setToolTip("Ayman IS THE BEST!")
        else:
            self.buttonCreateAccont.setEnabled(False)
            self.buttonCreateAccont.setToolTip("Please make sure all required fields are filled.")


if __name__ == "__main__":
    app = QApplication([])
    window = CreateAccountWidget()
    window.show()
    app.exec()

