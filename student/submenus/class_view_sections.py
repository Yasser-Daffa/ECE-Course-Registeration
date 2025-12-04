import os
import sys
from PyQt6.QtWidgets import QWidget, QTableWidgetItem, QMessageBox, QApplication
from PyQt6.QtCore import Qt

# Add main folder to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# UI
from app_ui.student_ui.submenus_ui.ui_view_sections import Ui_ViewSections
from student.class_student_utilities import StudentUtilities
from database_files.initialize_database import initialize_database
from database_files.class_database_uitlities import DatabaseUtilities

# ------------------------ StudentUtilities init ------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "../../university_database.db"))
con, cur = initialize_database(DB_PATH)
db_util = DatabaseUtilities(con, cur)
student_id = 1  # example student
student_utils = StudentUtilities(db_util, student_id)


# ------------------------ Widget ------------------------
class ViewSectionsWidget(QWidget):
    def __init__(self, student_utils: StudentUtilities, parent=None):
        super().__init__(parent)

        # UI setup
        self.ui = Ui_ViewSections()
        self.ui.setupUi(self)

        self.student_utils = student_utils
        self.all_sections = []

        # Connect signals
        self.ui.buttonRefresh.clicked.connect(self.load_sections)
        self.ui.lineEditSearch.textChanged.connect(self.filter_sections)
        self.ui.comboBoxFilterCourses.currentIndexChanged.connect(self.filter_sections)
        self.ui.comboBoxStatusFilter.currentIndexChanged.connect(self.filter_sections)
        self.ui.buttonRegisterCourse.clicked.connect(self.register_course)

        # Table settings
        self.ui.tableSections.setSelectionBehavior(self.ui.tableSections.SelectionBehavior.SelectRows)
        self.ui.tableSections.setSelectionMode(self.ui.tableSections.SelectionMode.SingleSelection)

        # Populate course filter and load sections
        self.setup_courses_combo()
        self.load_sections()

    # ---------------- Setup course filter ----------------
    def setup_courses_combo(self):
        cb = self.ui.comboBoxFilterCourses
        cb.clear()
        cb.addItem("All Courses", None)

        courses = self.student_utils.get_available_courses(semester=None)
        for course in courses:
            cb.addItem(f"{course['course_code']} - {course['course_name']}", course['course_code'])

    # ---------------- Load sections ----------------
    def load_sections(self):
        self.all_sections = self.student_utils.get_all_sections()
        self.populate_table(self.all_sections)
        self.update_stats()

    # ---------------- Populate table ----------------
    def populate_table(self, sections):
        table = self.ui.tableSections
        table.setRowCount(0)
        for idx, sec in enumerate(sections, start=1):
            row = table.rowCount()
            table.insertRow(row)

            table.setItem(row, 0, QTableWidgetItem(str(idx)))
            table.setItem(row, 1, QTableWidgetItem(str(sec['id'])))
            table.setItem(row, 2, QTableWidgetItem(sec['course_code']))
            table.setItem(row, 3, QTableWidgetItem(sec['name']))
            table.setItem(row, 4, QTableWidgetItem(sec['instructor']))
            table.setItem(row, 5, QTableWidgetItem(sec['schedule']))
            table.setItem(row, 6, QTableWidgetItem(str(sec['enrolled'])))
            table.setItem(row, 7, QTableWidgetItem(str(sec['capacity'])))
            table.setItem(row, 8, QTableWidgetItem(sec['status']))

    # ---------------- Update stats ----------------
    def update_stats(self):
        total = len(self.all_sections)
        open_count = sum(1 for s in self.all_sections if s['status'] == 'Open')
        closed_count = sum(1 for s in self.all_sections if s['status'] == 'Closed')
        full_count = sum(1 for s in self.all_sections if s['status'] == 'Full')

        self.ui.labelTotalSectionsCount.setText(str(total))
        self.ui.labelOpenSectionsCount.setText(str(open_count))
        self.ui.labelClosedSectionsCount.setText(str(closed_count))
        self.ui.labelFullSectionsCount.setText(str(full_count))

    # ---------------- Filter sections ----------------
    def filter_sections(self):
        search_text = self.ui.lineEditSearch.text().lower()
        course_filter = self.ui.comboBoxFilterCourses.currentData()
        status_filter = self.ui.comboBoxStatusFilter.currentText()

        filtered = []
        for s in self.all_sections:
            if search_text and search_text not in str(s['id']).lower():
                continue
            if course_filter and s['course_code'] != course_filter:
                continue
            if status_filter != "All Status" and s['status'] != status_filter:
                continue
            filtered.append(s)

        self.populate_table(filtered)

    # ---------------- Register ----------------
    def register_course(self):
        row = self.ui.tableSections.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a section to register.")
            return

        section_id = int(self.ui.tableSections.item(row, 1).text())
        success = self.student_utils.register_section(section_id)
        if success:
            QMessageBox.information(self, "Success", f"Successfully registered for section {section_id}.")
            self.load_sections()
        else:
            QMessageBox.warning(self, "Failed", "Cannot register for this section (full, conflict, or already registered).")


# ------------------------ Run standalone ------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = ViewSectionsWidget(student_utils)
    w.show()
    sys.exit(app.exec())
