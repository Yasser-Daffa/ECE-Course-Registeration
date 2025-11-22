from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QColor, QIcon

from PyQt6.QtWidgets import QApplication, QWidget, QGraphicsDropShadowEffect, QFrame, QHBoxLayout, QPushButton

from ui_login_widget import Ui_LoginWidget
from login_helper_functions import BaseLoginForm # helper class that adds multitude of things

import login_resources_rc


class LoginWidget(BaseLoginForm):
    def __init__(self):
        super().__init__()
        self.ui = Ui_LoginWidget()
        self.ui.setupUi(self)  # setup the UI on this QWidget

        # new line added trying to signalslot in auth window
        self.buttonCreateAccount = self.ui.buttonCreateAccount
        self.buttonLogin = self.ui.buttonLogin
        self.lineEditUsername = self.ui.lineEditUsername
        self.buttonResetPassword = self.ui.buttonResetPassword

        

        # Apply shadow to buttons
        self.add_shadow(self.buttonLogin)
        self.add_shadow(self.buttonCreateAccount)

        # Shadow for checkbox
        self.add_shadow(self.ui.checkBoxRemember, blur=8, xOffset=0, yOffset=2, color=(0, 0, 0, 80))

        # Shadow for the Login Panel/Qframe
        self.add_shadow(self.ui.loginPanel, blur=25, xOffset=0, yOffset=5, color=(0, 0, 0, 120))



        # --- Show/hide password toggle button ---

        # False to keep password hidden by default
        self.show_password = False

        self.toggle_password_button = QPushButton(self.ui.lineEditPassword)
        self.toggle_password_button.clicked.connect(self.toggle_password)

        self.toggle_password_button.setIcon(QIcon(":/qrc_images/assets/images/open_eye_icon24.png"))
        self.toggle_password_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_password_button.setCheckable(True)
        self.toggle_password_button.setFixedSize(24, 24)
        self.toggle_password_button.setStyleSheet("border: none; background: transparent;")

        

        # Save the original resizeEvent of the lineEdit
        original_resize_event = self.ui.lineEditPassword.resizeEvent

        
        # Define new resize event to reposition toggle button dynamically

        # Override the lineEdit’s resizeEvent so the eye-button follows its size changes.
        # We wrap the original resizeEvent inside a lambda that calls our custom function
        # (on_password_lineedit_resize) while still preserving Qt’s original resize behavior.
        self.ui.lineEditPassword.resizeEvent = \
    lambda event: self.on_password_lineedit_resize(original_resize_event, event)


        # Initial position
        self.update_button_position()


    def on_password_lineedit_resize(self, original_event, event):
        self.update_button_position()
        if original_event:
            original_event(event)




    def toggle_password(self):
        if self.show_password:
            self.ui.lineEditPassword.setEchoMode(self.ui.lineEditPassword.EchoMode.Password)
            self.toggle_password_button.setIcon(QIcon(":/qrc_images/assets/images/open_eye_icon24.png")) # makes the icon appear open when password is shown
        else:
            self.ui.lineEditPassword.setEchoMode(self.ui.lineEditPassword.EchoMode.Normal)
            self.toggle_password_button.setIcon(QIcon(":/qrc_images/assets/images/close_eye_icon24.png")) # makes the icon appear open when password is shown
        self.show_password = not self.show_password

    def update_button_position(self):
        pw = self.ui.lineEditPassword

        # Since this was too complicated to eyeball, these calculations made by chatGPT
        # To track the position of the lineEdit and make the toggle password button move with it
        self.toggle_password_button.move(
            pw.width() - self.toggle_password_button.width() - 4,
            (pw.height() - self.toggle_password_button.height()) // 2
        )



if __name__ == "__main__":
    app = QApplication([])
    window = LoginWidget()
    window.show()
    app.exec()
