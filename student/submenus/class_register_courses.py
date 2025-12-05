import sys, os
from PyQt6.QtWidgets import QApplication, QWidget, QTableWidgetItem
from PyQt6.QtCore import Qt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app_ui.student_ui.submenus_ui.ui_register_courses import Ui_RegisterCourses
from student.submenus.class_view_sections import ViewSectionsWidget
from helper_files.shared_utilities import show_msg
from student.class_student_utilities import StudentUtilities, db


class RegisterCoursesWidget(QWidget):
    """
    Register courses widget:
    - Table selectable
    - Only courses meeting prerequisites are selectable
    - View Sections button disabled until valid selection
    """

    def __init__(self, student_id: int, semester: str, parent=None):
        super().__init__(parent)

        # Setup UI
        self.ui = Ui_RegisterCourses()
        self.ui.setupUi(self)

        self.student_utils = StudentUtilities(db, student_id)
        self.semester = semester

        self.all_courses = []

        # Table settings
        table = self.ui.tableAllCourses
        table.setSelectionBehavior(table.SelectionBehavior.SelectRows)
        table.setSelectionMode(table.SelectionMode.SingleSelection)
        table.setEditTriggers(table.EditTrigger.NoEditTriggers)
        table.itemSelectionChanged.connect(self.on_table_selection_changed)

        # Button signals
        self.ui.buttonRefresh.clicked.connect(self.load_courses)
        self.ui.lineEditSearch.textChanged.connect(self.apply_search_filter)
        self.ui.buttonViewSections.clicked.connect(self.handle_view_sections)
        self.ui.buttonViewSections.setEnabled(False)  # disabled until selection

        self.load_courses()

    # ---------------- Load courses ----------------
    def load_courses(self):
        courses = self.student_utils.get_available_courses(self.semester)
        self.all_courses = courses
        self.fill_table(courses)

    def fill_table(self, rows):
        table = self.ui.tableAllCourses
        table.setRowCount(len(rows))

        for i, course in enumerate(rows):
            code = course["course_code"]
            name = course["course_name"]
            credits = course["credits"]
            can_register = course["can_register"]

            # Row number
            table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            # Course code
            code_item = QTableWidgetItem(code)
            code_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 1, code_item)
            # Course name
            name_item = QTableWidgetItem(name)
            name_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 2, name_item)
            # Credits
            credits_item = QTableWidgetItem(str(credits))
            credits_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 3, credits_item)
            # Can’t register courses appear gray
            if not can_register:
                for col in range(4):  # adjust as needed
                    item = table.item(i, col)
                    if item:
                        item.setBackground(Qt.GlobalColor.lightGray)

    # ---------------- Filter ----------------
    def apply_search_filter(self):
        text = self.ui.lineEditSearch.text().strip().lower()
        if not text:
            self.fill_table(self.all_courses)
            return
        filtered = [c for c in self.all_courses
                    if text in c["course_code"].lower() or text in c["course_name"].lower()]
        self.fill_table(filtered)

    # ---------------- Enable/disable button ----------------
    def on_table_selection_changed(self):
        row = self.ui.tableAllCourses.currentRow()
        if row < 0:
            self.ui.buttonViewSections.setEnabled(False)
            return

        course_code = self.ui.tableAllCourses.item(row, 1).text()
        course = next((c for c in self.all_courses if c["course_code"] == course_code), None)
        # Only enable button if prerequisites met
        self.ui.buttonViewSections.setEnabled(course["can_register"] if course else False)

    # ---------------- View Sections ----------------
    def handle_view_sections(self):
        row = self.ui.tableAllCourses.currentRow()
        if row < 0:
            return  # button should be disabled anyway

        course_code = self.ui.tableAllCourses.item(row, 1).text()
        self.sections_window = ViewSectionsWidget(self.student_utils, course_code)
        self.sections_window.show()
        show_msg(self, "DEBUG", f"Selected course: {course_code}")


# ---------------- Run standalone ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    student_id = 2500001
    semester = "2025-1"
    window = RegisterCoursesWidget(student_id, semester)
    window.show()
    sys.exit(app.exec())
