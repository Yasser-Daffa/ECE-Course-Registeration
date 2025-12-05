import sys, os
from PyQt6.QtWidgets import QApplication, QWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QStackedWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6 import QtWidgets

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
        self.sections_windows = []  # <-- store all opened section windows
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
        self.format_table()

    # ---------------- Load courses ----------------
    def load_courses(self):
        try:
            courses = self.student_utils.get_available_courses(self.semester)
        except Exception as e:
            show_msg(self, "Error", f"Failed to load courses:\n{e}")
            courses = []
        self.all_courses = courses
        self.fill_table(courses)

    # ---------------- Fill table with courses ----------------
    def fill_table(self, rows):
        table = self.ui.tableAllCourses
        table.setRowCount(len(rows))

        for i, course in enumerate(rows):
            code = course["course_code"]
            name = course["course_name"]
            credits = course["credits"]
            can_register = course["can_register"]
            prereqs = ", ".join(course.get("prereqs", [])) or "None"
            level = course.get("level", "-")

            # Row number
            table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            table.item(i, 0).setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)

            # Course code
            code_item = QTableWidgetItem(code)
            code_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 1, code_item)

            # Course name
            name_item = QTableWidgetItem(name)
            name_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 2, name_item)

            # Credits
            credits_item = QTableWidgetItem(str(credits))
            credits_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 3, credits_item)

            # Level
            level_item = QTableWidgetItem(level)
            level_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 4, level_item)

            # Prerequisites
            prereq_item = QTableWidgetItem(prereqs)
            prereq_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 5, prereq_item)

            # Tooltip for prerequisites
            for col in range(6):
                item = table.item(i, col)
                if item:
                    item.setToolTip(f"Prerequisites: {prereqs}")

    # ---------------- Filter ----------------
    def apply_search_filter(self):
        text = self.ui.lineEditSearch.text().strip().lower()
        if not text:
            self.fill_table(self.all_courses)
            return
        filtered = [c for c in self.all_courses
                    if text in c["course_code"].lower() or text in c["course_name"].lower()]
        self.fill_table(filtered)

    # ---------------- Format table ----------------
    def format_table(self):
        table = self.ui.tableAllCourses

        headers = ["#", "Course Code", "Name", "Credits", "Level", "Prerequisites"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)

        header = table.horizontalHeader()
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.verticalHeader().setDefaultSectionSize(60)

        table.setColumnWidth(0, 60)
        table.setColumnWidth(1, 150)
        table.setColumnWidth(2, 300)
        table.setColumnWidth(3, 80)
        table.setColumnWidth(4, 80)
        table.setColumnWidth(5, 200)

        # Make columns sortable
        table.setSortingEnabled(True)

        # Header resize mode
        for col in range(len(headers)):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)

    # ---------------- Enable/disable button ----------------
    def on_table_selection_changed(self):
        row = self.ui.tableAllCourses.currentRow()
        if row < 0:
            self.ui.buttonViewSections.setEnabled(False)
            return

        course_code = self.ui.tableAllCourses.item(row, 1).text()
        course = next((c for c in self.all_courses if c["course_code"] == course_code), None)
        self.ui.buttonViewSections.setEnabled(course["can_register"] if course else False)

    def handle_view_sections(self):
        row = self.ui.tableAllCourses.currentRow()
        if row < 0:
            return

        course_code = self.ui.tableAllCourses.item(row, 1).text()

        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("View Sections")
        dialog.setModal(True)   # modal dialog

        # Layout for the dialog
        layout = QtWidgets.QVBoxLayout(dialog)

        # Create the widget inside the dialog
        sections_widget = ViewSectionsWidget(
            student_id=self.student_utils.student_id,
            semester=self.semester,
            course_codes=[course_code],
            parent=dialog
        )

        layout.addWidget(sections_widget)

        dialog.resize(900, 600)   # optional size
        dialog.exec()             # BLOCKING modal dialog




# ---------------- Run standalone ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    student_id = 7500003
    semester = "First"
    window = RegisterCoursesWidget(student_id, semester)
    window.show()
    sys.exit(app.exec())
