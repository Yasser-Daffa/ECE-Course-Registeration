from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QColor, QIcon

from PyQt6.QtWidgets import QApplication, QWidget, QGraphicsDropShadowEffect, QFrame, QHBoxLayout, QPushButton

from ui_confirm_email_widget import Ui_ConfirmEmailWidget
from login_helper_functions import BaseLoginForm # helper class that adds multitude of things

import login_resources_rc


class ConfirmEmailWidget(BaseLoginForm):
    def __init__(self):
        super().__init__()
        self.ui = Ui_ConfirmEmailWidget()
        self.ui.setupUi(self)  # setup the UI on this QWidget

        # for signaling and slotting
        self.buttonReSendCode = self.ui.buttonReSendCode
        self.buttonVerifyCode = self.ui.buttonVerifyCode
        self.buttonBackToSignIn = self.ui.buttonBackToSignIn
        self.lineEditCode = self.ui.lineEditCode

        # visual shadows
        self.add_shadow(self.buttonBackToSignIn)
        self.add_shadow(self.buttonReSendCode)
        self.add_shadow(self.buttonVerifyCode)
        self.add_shadow(self.ui.confirmEmailPanel)

        # add a hide/show toggle button for verification code lineEdit

        self.create_pwrd_toggle_button(self.lineEditCode)
        self.update_toggle_button_position(self.lineEditCode)
        self.toggle_password(self.lineEditCode)
        

if __name__ == "__main__":
    app = QApplication([])
    window = ConfirmEmailWidget()
    window.show()
    app.exec()
