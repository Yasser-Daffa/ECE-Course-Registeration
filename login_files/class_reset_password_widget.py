from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import QApplication, QWidget, QGraphicsDropShadowEffect, QFrame, QHBoxLayout, QPushButton
import sys

from ui_login_widget import Ui_LoginWidget
from ui_reset_password_widget import Ui_ResetPasswordWidget
from login_helper_functions import BaseLoginForm
import login_resources_rc

class ResetPasswordWidget(BaseLoginForm):
    def __init__(self):
        super().__init__()
        self.ui = Ui_ResetPasswordWidget()
        self.ui.setupUi(self)  # setup the UI on this QWidget
        
        # for signaling and slotting
        self.buttonSendCode = self.ui.buttonSendCode
        self.buttonVerifyCode = self.ui.buttonVerifyCode
        self.buttonBackToSignIn = self.ui.buttonBackToSignIn
        self.lineEditRegisteredEmail = self.ui.lineEditRegisteredEmail
        self.lineEditCode = self.ui.lineEditCode
        

        # visual shadows
        self.add_shadow(self.buttonBackToSignIn)
        self.add_shadow(self.buttonSendCode)
        self.add_shadow(self.buttonVerifyCode)
        self.add_shadow(self.ui.resetPasswordPanel)

        # add a hide/show toggle button for verification code lineEdit
        self.create_pwrd_toggle_button(self.lineEditCode)

if __name__ == "__main__":
    app = QApplication([])
    window = ResetPasswordWidget()
    window.show()
    app.exec()