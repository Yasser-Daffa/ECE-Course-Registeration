import sys
from PyQt6.QtWidgets import QApplication, QWidget, QStackedWidget, QMessageBox

# --- 1. Import all necessary files ---
from ui_auth_stackedwidget import Ui_AuthStackedWidget 
from class_login_widget import LoginWidget
from class_create_account_widget import CreateAccountWidget 
from class_reset_password_widget import ResetPasswordWidget
# from class_reset_password_dialog import ResetPasswordDialog
from class_confirm_email_widget import ConfirmEmailWidget

# Placeholder imports for your future main windows
# from class_student_dashboard import StudentDashboard
# from class_admin_dashboard import AdminDashboard 

class AuthenticationWindow(QWidget): 
    def __init__(self):
        super().__init__()
        self.ui = Ui_AuthStackedWidget()
        self.ui.setupUi(self)
        self.ui.stackedWidgetAuth.setCurrentIndex(0)

        # --- 2. Get the promoted widget instances ---
        # NOTE: If you added pages in a different order, adjust the indexes.
        self.login_page: LoginWidget = self.ui.stackedWidgetAuth.widget(0)      
        self.create_acc_page: CreateAccountWidget = self.ui.stackedWidgetAuth.widget(1)
        self.reset_password_confirm_email_page: ResetPasswordWidget = self.ui.stackedWidgetAuth.widget(2)
        # self.reset_password_page: ResetPasswordDialog = self.ui.stackedWidgetAuth.widget(3)
        self.confirm_email_page: ConfirmEmailWidget = self.ui.stackedWidgetAuth.widget(4)

        # --- 3. Connect Navigation Signals ---
        
        # From Login (Index 0) to Registration (Index 1)
        self.login_page.buttonCreateAccount.clicked.connect(self.go_to_registration)

        # From Registration (Index 1) back to Login (Index 0)
        self.create_acc_page.buttonLoginHere.clicked.connect(self.go_to_login)

        # From login to reset password(index 2) and from reset password to login(index 0)
        self.login_page.buttonResetPassword.clicked.connect(self.go_to_reset)
        self.reset_password_confirm_email_page.buttonBackToSignIn.clicked.connect(self.go_to_login)

        # --- 4. Connect Final Action Signals ---
        self.login_page.ui.buttonLogin.clicked.connect(self.handle_login)
        self.create_acc_page.ui.buttonCreateAccount.clicked.connect(self.handle_registration)
    
    def go_to_login(self):
        print("Switching back to login page...")
        self.ui.stackedWidgetAuth.setCurrentIndex(0) # Switch back to the LoginWidget

    def go_to_registration(self):
        print("Switching to registration page...")
        self.ui.stackedWidgetAuth.setCurrentIndex(1) # Switch to the CreateAccountWidget

    def go_to_reset(self):
        """ If the user clickes on the reset password button it will open this page"""
        print("Switching to reset pasword page")
        self.ui.stackedWidgetAuth.setCurrentIndex(2)
    
    def open_password_reset_outside(self):
        """If password and confirm password match it will
            redirect the user to the reset password window. """
        print("Openning password reset dialog")
        self.ui.stackedWidgetAuth.setCurrentIndex(3)
    


    def handle_login(self):
        # *** This is where you transition to the main application ***
        username = self.login_page.ui.lineEditUsername.text() 
        password = self.login_page.ui.lineEditPassword.text()

        print(f"Attempting login for: {username}")
        
        # --- Dummy Login Check ---
        if username == "student" and password == "123":
            print("Login successful. Opening Student Dashboard.")
            # self.student_dash = StudentDashboard() 
            # self.student_dash.show()
            self.close() # Close the AuthWindow

        elif username == "admin" and password == "admin":
            print("Login successful. Opening Admin Dashboard.")
            # self.admin_dash = AdminDashboard()
            # self.admin_dash.show()
            self.close() # Close the AuthWindow
            
        else:
            print("Login Failed.")
            return "failed"
            # (Show error message on login page)


    def handle_registration(self):
        # Access the exposed status label on the registration page
        status_label = self.create_acc_page.statusLabel # ---------------------HERE CREATE STATUS LABEL AS QDIALOG FOR CHECKING!!!-----
        
        # --- 1. Basic Input Validation (Example) ---
        password = self.create_acc_page.lineEditPassword.text()
        confirm_password = self.create_acc_page.lineEditPasswordConfirm.text()
        
            
        # --- 2. Registration Logic ---
        
        # Simulating a successful database submission
        status_label.setText("Success! Account created. Redirecting to login...")
        status_label.setStyleSheet("color: green;") 
        
        # 3. Use a QTimer to wait a moment before switching pages
        from PyQt6.QtCore import QTimer
        
        # This line schedules the 'go_to_login' function to run after 1500 milliseconds (1.5 seconds)
        QTimer.singleShot(1500, self.go_to_login)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AuthenticationWindow() 
    window.show()
    sys.exit(app.exec())