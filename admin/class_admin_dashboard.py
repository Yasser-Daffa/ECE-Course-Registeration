import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from PyQt6 import QtWidgets
from database_files.class_database_uitlities import DatabaseUtilities
from database_files.initialize_database import initialize_database

# Subpage controllers
from app_ui.admin_ui.submenus_ui.ui_all_students import Ui_AllStudents
from admin.submenus.class_all_students import AllStudentsController
# from app_ui.admin_ui.submenus_ui.ui_pending_requests import Ui_PendingRequestsWidget
# from admin.submenus.class_pending_requests import PendingRequestsController

from app_ui.admin_ui.ui_admin_dashboard import Ui_AdminDashboard


class AdminDashboard(QtWidgets.QMainWindow):
    def __init__(self, db: DatabaseUtilities):
        super().__init__()

        # Main UI
        self.ui = Ui_AdminDashboard()
        self.ui.setupUi(self)
        self.db = db

        # ------------------------
        # Initialize all subpages
        # ------------------------
        self.init_sub_pages()

        # ------------------------
        # Map buttons to pages
        # ------------------------
        self.page_mapping = {
            self.ui.buttonAllStudents: self.all_students_page,
            # self.ui.buttonPendingRequests: self.pending_requests_page,
            # Add more buttons → pages here
        }

        # ------------------------
        # Connect buttons properly
        # ------------------------
        for button, page in self.page_mapping.items():
            button.clicked.connect(lambda checked, p=page: self.ui.stackedWidget.setCurrentWidget(p))

        # Show default page
        self.ui.stackedWidget.setCurrentIndex(0)

    # -------------------------------
    # Initialize sub-pages
    # -------------------------------
    def init_sub_pages(self):
        # --- All Students Page ---
        self.all_students_page = QtWidgets.QWidget()
        self.all_students_ui = Ui_AllStudents()
        self.all_students_ui.setupUi(self.all_students_page)
        self.all_students_controller = AllStudentsController(self.all_students_ui, self.db)

        # Add to stackedWidget
        self.ui.stackedWidget.addWidget(self.all_students_page)

        # --- Pending Requests Page (example) ---
        # self.pending_requests_page = QtWidgets.QWidget()
        # self.pending_requests_ui = Ui_PendingRequestsWidget()
        # self.pending_requests_ui.setupUi(self.pending_requests_page)
        # self.pending_requests_controller = PendingRequestsController(self.pending_requests_ui, self.db)
        # self.ui.stackedWidget.addWidget(self.pending_requests_page)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "../../university_database.db")
    con, cur = initialize_database(DB_PATH)
    db = DatabaseUtilities(con, cur)

    window = AdminDashboard(db)
    window.show()
    sys.exit(app.exec())
