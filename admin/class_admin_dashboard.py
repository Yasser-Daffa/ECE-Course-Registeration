import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))


from PyQt6 import QtWidgets
from database_files.class_database_uitlities import DatabaseUtilities
from database_files.initialize_database import initialize_database

# Subpage UI & Controller imports
from app_ui.admin_ui.ui_admin_dashboard import Ui_AdminDashboard
from app_ui.admin_ui.submenus_ui.ui_all_students import Ui_AllStudents
from admin.submenus.class_all_students import AllStudentsController

from app_ui.admin_ui.submenus_ui.ui_pending_requests import Ui_PendingRequestsWidget
from admin.submenus.class_pending_requests import PendingRequestsController

from app_ui.admin_ui.submenus_ui.ui_manage_courses import Ui_ManageCourses
from admin.submenus.class_manage_courses import ManageCoursesController

class AdminDashboard(QtWidgets.QMainWindow):
    """
    Main admin dashboard window.
    Handles page switching via a QStackedWidget and initializes all sub-pages.
    """
    
    def __init__(self, db: DatabaseUtilities):
        super().__init__()

        # -------------------------------
        # Main UI setup
        # -------------------------------
        self.ui = Ui_AdminDashboard()
        self.ui.setupUi(self)
        self.db = db

        # ------------------------
        # 1. Initialize all pages
        # ------------------------
        self.init_sub_pages()

        # ------------------------
        # 2. Add pages to stacked widget
        # ------------------------
        self.ui.stackedWidget.addWidget(self.all_students_page)
        self.ui.stackedWidget.addWidget(self.pending_requests_page)
        self.ui.stackedWidget.addWidget(self.manage_courses_page)
        # Add other pages similarly...


        # -------------------------------
        # 3- Map buttons to their corresponding pages
        # -------------------------------

        # Key: QPushButton object
        # Value: Tuple of (page name string, QWidget page)
        # Using a string here avoids printing emojis/unicode directly from button.text()
        self.page_mapping = {
            self.ui.buttonAllStudents: ("All Students", self.all_students_page),
            self.ui.buttonPendingRequests: ("Pending Requests", self.pending_requests_page),
            self.ui.buttonManageCourses: ("Manage Courses", self.manage_courses_page)
        }

        # Connect buttons to page-switching logic
        for button in self.page_mapping.keys():
            button.clicked.connect(lambda checked, b=button: self.switch_to_page(b))

        # Show default page (should be profile first)
        # self.switch_to_page(self.ui.buttonProfile)

    # -------------------------------
    # Initialize all sub-pages
    # -------------------------------
    def init_sub_pages(self):
        """
        Create QWidget pages, set up their UI, and attach controllers.
        Controllers must be initialized AFTER widget + UI exist.
        """
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
        # Pending Requests page
        # -------------------------------
        self.manage_courses_page = QtWidgets.QWidget()
        self.manage_courses_ui = Ui_ManageCourses()
        self.manage_courses_ui.setupUi(self.manage_courses_page)
        self.manage_courses_controller = ManageCoursesController(self.manage_courses_ui, self.db)

    # -------------------------------
    # Switch the stacked widget to the page associated with the clicked button
    # -------------------------------
    def switch_to_page(self, button):
        # Retrieve the mapping info for the clicked button
        info = self.page_mapping.get(button)
        if info:
            # Unpack the tuple into a readable name and the actual QWidget page
            name, page = info
            
            # Set the stacked widget to display the selected page
            self.ui.stackedWidget.setCurrentWidget(page)
            
            # Optional debug: safely print the human-readable name of the page
            print(f"Switched to page: {name}")

# ------------------------------- MAIN APP -------------------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "../university_database.db")
    con, cur = initialize_database(DB_PATH)
    db = DatabaseUtilities(con, cur)

    window = AdminDashboard(db)
    window.show()
    sys.exit(app.exec())
