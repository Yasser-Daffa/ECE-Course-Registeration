import os
import sys
from PyQt6.QtWidgets import QWidget, QTableWidgetItem, QMessageBox, QApplication, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect

# Add main folder to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# UI
from app_ui.student_ui.submenus_ui.ui_view_sections import Ui_ViewSections
from student.class_student_utilities import StudentUtilities
from database_files.initialize_database import initialize_database
from database_files.class_database_uitlities import DatabaseUtilities
from helper_files.shared_utilities import show_msg, info, warning, error

# ------------------------ StudentUtilities init ------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "../../university_database.db"))
con, cur = initialize_database(DB_PATH)
db_util = DatabaseUtilities(con, cur)


# ------------------------ Widget ------------------------
class ViewSectionsWidget(QWidget):
    def __init__(self, student_utils: StudentUtilities, course_code: str, parent=None):
        super().__init__(parent)

        self.ui = Ui_ViewSections()
        self.ui.setupUi(self)

        self.student_utils = student_utils
        self.course_code = course_code
        self.all_sections = []

        # -------------- ANIMATION ---------------

        # # Fade effect
        # self.effect = QGraphicsOpacityEffect(self)
        # self.setGraphicsEffect(self.effect)

        # self.fade_anim = QPropertyAnimation(self.effect, b"opacity")
        # self.fade_anim.setDuration(350)
        # self.fade_anim.setStartValue(0.0)
        # self.fade_anim.setEndValue(1.0)

        # # Slide effect
        # start_rect = QRect(self.x() + 60, self.y(), self.width(), self.height())
        # end_rect = QRect(self.x(), self.y(), self.width(), self.height())

        # self.slide_anim = QPropertyAnimation(self, b"geometry")
        # self.slide_anim.setDuration(350)
        # self.slide_anim.setStartValue(start_rect)
        # self.slide_anim.setEndValue(end_rect)

        # # # Start both
        # self.fade_anim.start()
        # self.slide_anim.start()


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
        """Loads all sections with user selected course code"""
        self.all_sections = [
            s for s in self.student_utils.get_all_sections()
            if s["course_code"] == self.course_code
        ]

        self.fill_table(self.all_sections)
        self.update_stats()


    # ---------------- Populate table ----------------
    def fill_table(self, sections):
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

        self.fill_table(filtered)

    # ---------------- Register ----------------
    def register_course(self):
        row = self.ui.tableSections.currentRow()
        if row < 0:
            show_msg(self, "No Selection", "Please select a section to register.", QMessageBox.Icon.Warning)
            return

        section_id = int(self.ui.tableSections.item(row, 1).text())
        success = self.student_utils.register_section(section_id)
        if success:
            show_msg(self, "Success", f"Successfully registered for section {section_id}.", QMessageBox.Icon.Information)
            self.load_sections()
        else:
            warning(self, "Cannot register for this section (full, conflict, or already registered).")


# ------------------------ Run standalone test ------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)

    student_id = 5000002  # example student
    course_code = "SALEM" # example 'student' selected course

    student_utils = StudentUtilities(db_util, student_id)

    w = ViewSectionsWidget(student_utils, course_code)

    w.show()
    sys.exit(app.exec())
