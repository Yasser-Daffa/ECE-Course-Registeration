import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtWidgets import QApplication
from PyQt6 import QtWidgets

from database_files.class_database_uitlities import DatabaseUtilities
from admin.class_admin_utilities import AdminUtilities, db

# Subpage UI & Controller imports
from app_ui.admin_ui.ui_admin_dashboard import Ui_AdminDashboard


from admin.submenus.class_profile import ProfileWidget

from app_ui.admin_ui.submenus_ui.ui_all_students import Ui_AllStudents
from admin.submenus.class_all_students import AllStudentsController

from app_ui.admin_ui.submenus_ui.ui_pending_requests import Ui_PendingRequestsWidget
from admin.submenus.class_pending_requests import PendingRequestsController

from app_ui.admin_ui.submenus_ui.ui_manage_courses import Ui_ManageCourses
from admin.submenus.class_manage_courses import ManageCoursesController

from app_ui.admin_ui.submenus_ui.ui_manage_prereq import Ui_ManagePrereqs
from admin.submenus.class_manage_prereqs import ManagePrerequisitesController

from app_ui.admin_ui.submenus_ui.ui_manage_sections import Ui_ManageSections
from admin.submenus.class_manage_sections import ManageSectionsWidget

from app_ui.admin_ui.submenus_ui.ui_program_plans import Ui_ProgramPlans
from admin.submenus.class_program_plans import ProgramPlansWidget 

from admin.submenus.class_manage_faculty import ManageFacultyWidget

class AdminDashboard(QtWidgets.QMainWindow):
    """
    Main admin dashboard window.
    Handles page switching via a QStackedWidget and initializes all sub-pages.
    """
    
    def __init__(self, db, user: tuple):
        super().__init__()

        # -------------------------------
        # Main UI setup
        # -------------------------------
        self.ui = Ui_AdminDashboard()
        self.ui.setupUi(self)

        self.db = db
        self.user_id, self.name, self.email, self.program, self.state, self.account_status, self.hashed_pw = user
        self.admin = AdminUtilities(self.db)

        # ------------------------
        # 1. Initialize all pages
        # ------------------------
        self.init_sub_pages()

        # ------------------------
        # 2. Add pages to stacked widget
        # ------------------------
        self.ui.stackedWidget.addWidget(self.profile_page)
        self.ui.stackedWidget.addWidget(self.all_students_page)
        self.ui.stackedWidget.addWidget(self.pending_requests_page)

        self.ui.stackedWidget.addWidget(self.manage_faculty_controller)

        self.ui.stackedWidget.addWidget(self.manage_courses_page)
        self.ui.stackedWidget.addWidget(self.manage_prereqs_page)
        self.ui.stackedWidget.addWidget(self.manage_sections_controller)
        self.ui.stackedWidget.addWidget(self.program_plans_controller)

        # -------------------------------
        # 3. Map buttons to their corresponding pages
        # -------------------------------
        self.page_mapping = {
            self.ui.buttonProfile: ("Profile", self.profile_page),
            self.ui.buttonAllStudents: ("All Students", self.all_students_page),
            self.ui.buttonPendingRequests: ("Pending Requests", self.pending_requests_page),

            self.ui.buttonManageFaculty: ("Manage Faculty", self.manage_faculty_controller),

            self.ui.buttonManageCourses: ("Manage Courses", self.manage_courses_page),
            self.ui.buttonManagePrereqs: ("Manage Prereqs", self.manage_prereqs_page),
            self.ui.buttonManageSections: ("Manage Sections", self.manage_sections_controller),
            self.ui.buttonProgramPlans: ("Program Plans", self.program_plans_controller),
        }

        # Connect buttons to page-switching logic
        for button in self.page_mapping.keys():
            button.clicked.connect(lambda checked, b=button: self.switch_to_page(b))

        # Connect logout button
        self.ui.buttonLogout.clicked.connect(self.fade_and_logout)

        # Show profile by default
        self.switch_to_page(self.ui.buttonProfile)
        

    # -------------------------------
    # Initialize all sub-pages
    # -------------------------------
    def init_sub_pages(self):
        """
        Create QWidget pages, set up their UI, and attach controllers.
        """
        # -------------------------------
        # Profile page
        # -------------------------------
        # user tuple passed to ProfileWidget
        self.profile_page = ProfileWidget(
            (self.user_id, self.name, self.email, self.program, self.state, self.account_status)
        )

        # -------------------------------
        # All Students page
        # -------------------------------
        self.all_students_page = QtWidgets.QWidget()
        self.all_students_ui = Ui_AllStudents()
        self.all_students_ui.setupUi(self.all_students_page)
        self.all_students_controller = AllStudentsController(self.all_students_ui, self.db)

        # -------------------------------
        # Pending Requests page
        # -------------------------------
        self.pending_requests_page = QtWidgets.QWidget()
        self.pending_requests_ui = Ui_PendingRequestsWidget()
        self.pending_requests_ui.setupUi(self.pending_requests_page)
        self.pending_requests_controller = PendingRequestsController(self.pending_requests_ui, self.db)


        # -------------------------------
        # Manage Faculty [new]
        # -------------------------------
        # uses database utilities
        
        self.manage_faculty_controller = ManageFacultyWidget(self.db)


        # -------------------------------
        # Manage courses
        # -------------------------------
        # uses database utilities
        self.manage_courses_page = QtWidgets.QWidget()
        self.manage_courses_ui = Ui_ManageCourses()
        self.manage_courses_ui.setupUi(self.manage_courses_page)
        self.manage_courses_controller = ManageCoursesController(self.manage_courses_ui, self.db)


        # -------------------------------
        # Manage prereqs
        # -------------------------------
        # uses admin utilities and database utilities
        self.manage_prereqs_page = QtWidgets.QWidget()
        self.manage_prereqs_ui = Ui_ManagePrereqs()
        self.manage_prereqs_ui.setupUi(self.manage_prereqs_page)
        self.manage_prereqs_controller = ManagePrerequisitesController(
            self.manage_prereqs_ui, self.admin, self.db
        )

        # -------------------------------
        # Manage sections
        # -------------------------------
        # uses admin utilities
        self.manage_sections_controller = ManageSectionsWidget(self.admin)

        # -------------------------------
        # Program plans
        # -------------------------------
        # uses admin utilities
        self.program_plans_controller = ProgramPlansWidget(self.admin)

    # -------------------------------
    # Page switching with stacked widget
    # -------------------------------
    def switch_to_page(self, button):
        info = self.page_mapping.get(button)
        if info:
            name, page = info
            self.ui.stackedWidget.setCurrentWidget(page)
            print(f"Switched to page: {name}")

    # -------------------------------
    # Logout fade-out animation
    # -------------------------------
    def fade_and_logout(self):
        from login_files.class_authentication_window import AuthenticationWindow

        QApplication.instance().setQuitOnLastWindowClosed(False)

        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(350)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.anim.finished.connect(lambda: (
            self.close(),
            QTimer.singleShot(50, self.show_authentication_window)
        ))

        self.anim.start()

    def show_authentication_window(self):
        from login_files.class_authentication_window import AuthenticationWindow
        self.authentication_window = AuthenticationWindow()
        self.authentication_window.show()


# ------------------------------- MAIN APP -------------------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Example usage:
    # Replace "user" with a real tuple from login
    # window = AdminDashboard(db, user)

    sys.exit(app.exec())
