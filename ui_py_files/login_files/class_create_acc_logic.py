from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QColor, QIcon

from PyQt6.QtWidgets import QApplication, QWidget, QGraphicsDropShadowEffect, QFrame, QHBoxLayout, QPushButton

from class_create_acc_widget import CreateAccountWidget
import login_resources_rc

class CreateAccountLogic(QWidget):
    def __init__(self):
        super().__init__()
        self.logic = CreateAccountWidget()
        
        # new line added trying to signalslot in auth window
        self.createAccountButton = self.logic.createAccountButton
        self.loginHereButton = self.logic.loginHereButton
        self.lineEditFullName = self.logic.lineEditFullName
        self.lineEditPassword = self.logic.lineEditPassword
        self.lineEditPasswordConfirm = self.logic.lineEditPasswordConfirm

    def create_acc_button_state(self):
        password = self.logic.lineEditPassword.text()
        confirm = self.logic.lineEditPasswordConfirm.text()

        # # Get rule results
        # rules = check_password_rules(password)

        # # All password rules must be True
        # all_rules_ok = all(rules.values())

        # Passwords must match
        passwords_match = password == confirm and password != ""

        # All required fields must be filled
        fields_filled = all([
            self.logic.labelFullName.text().strip(),
            self.logic.lineEditEmail.text().strip(),
            password.strip(),
            confirm.strip()
        ])

        # Final condition
        can_create = all_rules_ok and passwords_match and fields_filled

        self.ui.createAccountButton.setEnabled(can_create)





if __name__ == "__main__":
    app = QApplication([])
    window = CreateAccountWidget()
    window.show()
    app.exec()
