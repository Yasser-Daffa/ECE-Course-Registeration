import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from PyQt6 import QtWidgets
from database_files.class_database_uitlities import DatabaseUtilities
from database_files.initialize_database import initialize_database

# Subpage controllers and UI imports
from app_ui.admin_ui.ui_admin_dashboard import Ui_AdminDashboard

from app_ui.admin_ui.submenus_ui.ui_all_students import Ui_AllStudents
from admin.submenus.class_all_students import AllStudentsController


class AdminDashboard(QtWidgets.QMainWindow):
    def __init__(self, db: DatabaseUtilities):
        super().__init__()

        # Main UI
        self.ui = Ui_AdminDashboard()
        self.ui.setupUi(self)
        self.db = db

        # ------------------------
        # 1 Initialize all pages
        # ------------------------
        self.init_sub_pages()

        # ------------------------
        # 2 Add pages to stacked widget
        # ------------------------
        self.ui.stackedWidget.addWidget(self.all_students_page)
        self.ui.stackedWidget.addWidget(self.pending_requests_page)
        # Add more pages here as needed:
        # self.ui.stackedWidget.addWidget(self.courses_page)

        # ------------------------
        # 3 Connect submenu buttons
        # ------------------------
        for i, button in enumerate(self.ui.buttonGroupSubmenus.buttons()):
            self.ui.buttonGroupSubmenus.setId(button, i)
        self.ui.buttonGroupSubmenus.idClicked.connect(self.change_page)

        # Show first page by default
        self.ui.stackedWidget.setCurrentIndex(0)

    # -------------------------------
    # Initialize all sub-pages
    # -------------------------------
    def init_sub_pages(self):
        # All Students page
        self.all_students_page = QtWidgets.QWidget()
        self.all_students_ui = Ui_AllStudents()
        self.all_students_ui.setupUi(self.all_students_page)
        self.all_students_controller = AllStudentsController(self.all_students_ui, self.db)

        # Pending Requests page
        self.pending_requests_page = QtWidgets.QWidget()
        self.pending_requests_ui = Ui_PendingRequestsWidget()
        self.pending_requests_ui.setupUi(self.pending_requests_page)
        self.pending_requests_controller = PendingRequestsController(self.pending_requests_ui, self.db)

        # Example: Courses page could be added here similarly
        # self.courses_page = QtWidgets.QWidget()
        # self.courses_ui = Ui_Courses()
        # self.courses_ui.setupUi(self.courses_page)
        # self.courses_controller = CoursesController(self.courses_ui, self.db)

    # -------------------------------
    # Change page
    # -------------------------------
    def change_page(self, button_id):
        print(f"Switching to page index: {button_id}")
        self.ui.stackedWidget.setCurrentIndex(button_id)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "../../university_database.db")
    con, cur = initialize_database(DB_PATH)
    db = DatabaseUtilities(con, cur)

    window = AdminDashboard(db)
    window.show()
    sys.exit(app.exec())
