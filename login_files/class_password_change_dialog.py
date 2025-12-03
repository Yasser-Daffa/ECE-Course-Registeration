from PyQt6.QtWidgets import QDialog, QApplication

from ui_password_change_dialog import Ui_PasswordChangeDialog
from login_helper_functions import BaseLoginForm # helper class that adds multitude of things



class PasswordChangeDialog(QDialog, BaseLoginForm):
    def __init__(self):
        super().__init__()
        self.ui = Ui_PasswordChangeDialog()
        self.ui.setupUi(self)  # setup the UI on this QWidget

        # Signal Slotting
        self.buttonChangePassword = self.ui.buttonChangePassword
        self.buttonCancel = self.ui.buttonCancel
        # line edits
        self.lineEditPassword = self.ui.lineEditPassword
        self.lineEditPasswordConfirm = self.ui.lineEditPasswordConfirm
        # pwrd authenticatuiins
        self.progressBarPwrdStrength = self.ui.progressBarPwrdStrength
        self.labelPwrdStrengthStatus = self.ui.labelPwrdStrengthStatus
        self.labelPasswordRules = self.ui.labelPasswordRules

        # Apply shadow to buttons
        self.add_shadow(self.buttonChangePassword)
        self.add_shadow(self.buttonCancel)
        # Shadow for the Login Panel/Qframe
        self.add_shadow(self.ui.passwordChangePanel, blur=25, xOffset=0, yOffset=5, color=(0, 0, 0, 120))


        # --- Show/hide password toggle button ---
        self.create_pwrd_toggle_button(self.lineEditPassword)
        self.create_pwrd_toggle_button(self.lineEditPasswordConfirm)
        
                # --- Connect password field to strength checker ---
        self.attach_password_strength_checker(
            self.lineEditPassword,
            self.progressBarPwrdStrength,
            self.labelPwrdStrengthStatus,
            self.labelPasswordRules
            )

        # initialize strength feedback




if __name__ == "__main__":
    app = QApplication([])
    dialog = PasswordChangeDialog()
    dialog.exec()  # modal dialog
