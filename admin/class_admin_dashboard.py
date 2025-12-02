import os, sys, io
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

# Enable UTF-8 in Windows console
if os.name == 'nt':
    import ctypes
    ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from PyQt6 import QtWidgets
from database_files.class_database_uitlities import DatabaseUtilities
from database_files.initialize_database import initialize_database

# Subpage UI & Controller imports
from app_ui.admin_ui.ui_admin_dashboard import Ui_AdminDashboard
from app_ui.admin_ui.submenus_ui.ui_all_students import Ui_AllStudents
from admin.submenus.class_all_students import AllStudentsController

from app_ui.admin_ui.submenus_ui.ui_pending_requests import Ui_PendingRequestsWidget
from admin.submenus.class_pending_requests import PendingRequestsController

from app_ui.admin_ui.submenus_ui.ui_course_management import Ui_CourseManagement
from admin.submenus.class_course_management import CoursesManagementController

class AdminDashboard(QtWidgets.QMainWindow):
    def __init__(self, db: DatabaseUtilities):
        super().__init__()

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
        # Add other pages similarly...

        # ------------------------
        # 3. Map buttons to pages
        # ------------------------
        self.page_mapping = {
            self.ui.buttonAllStudents: self.all_students_page,
            self.ui.buttonPendingRequests: self.pending_requests_page
            # other buttons → pages
        }

        for button in self.page_mapping.keys():
            button.clicked.connect(lambda checked, b=button: self.switch_to_page(b))

        # Show default page (should be profile first)
        # self.switch_to_page(self.ui.buttonAllStudents)

    # -------------------------------
    # Initialize all sub-pages
    # -------------------------------
    def init_sub_pages(self):
        # Create the widget
        self.all_students_page = QtWidgets.QWidget()
        # Setup UI
        self.all_students_ui = Ui_AllStudents()
        self.all_students_ui.setupUi(self.all_students_page)

        # Initialize controller **after widget exists and UI is set up**
        self.all_students_controller = AllStudentsController(self.all_students_ui, self.db)


        # pending requests page
        self.pending_requests_page = QtWidgets.QWidget()
        # Setup UI
        self.pending_requests_ui = Ui_PendingRequestsWidget()
        self.pending_requests_ui.setupUi(self.pending_requests_page)
        # Initialize controller **after widget exists and UI is set up**
        self.pending_requests_controller = PendingRequestsController(self.pending_requests_ui, self.db)

    # -------------------------------
    # Switch page by button
    # -------------------------------
    def switch_to_page(self, button):
        page = self.page_mapping.get(button)
        if page:
            self.ui.stackedWidget.setCurrentWidget(page)
            # safely print even if button text has emojis
            try:
                print(f"Switched to page: {button.text()}")
            except UnicodeEncodeError:
                # fallback: remove unprintable characters
                safe_text = button.text().encode('ascii', errors='ignore').decode()
                print(f"Switched to page: {safe_text}")

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
