import sys, os
from PyQt6.QtWidgets import QWidget, QApplication, QTableWidgetItem, QPushButton, QMessageBox
from PyQt6.QtCore import Qt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app_ui.student_ui.submenus_ui.ui_current_schedule import Ui_CurrentSchedule
from student.class_student_utilities import StudentUtilities, db


class CurrentScheduleWidget(QWidget):
    def __init__(self, student_id: int, parent=None):
        super().__init__(parent)
        self.ui = Ui_CurrentSchedule()
        self.ui.setupUi(self)

        self.student_id = student_id
        self.student_utils = StudentUtilities(db, student_id)
        self.registered_courses = []

        # Add Refresh button
        self.ui.buttonRefresh.clicked.connect(self.load_registered_courses)

        # Disable remove button initially
        self.ui.buttonRemoveSelected.setEnabled(False)
        self.ui.buttonRemoveSelected.clicked.connect(self.remove_selected_courses)

        # Configure table for row selection
        table = self.ui.tableCourses
        table.setSelectionBehavior(table.SelectionBehavior.SelectRows)
        table.setSelectionMode(table.SelectionMode.MultiSelection)

        # Connect selection change to button enable/disable
        table.selectionModel().selectionChanged.connect(self.on_selection_changed)

        # Load registered courses
        self.load_registered_courses()

    def load_registered_courses(self):
        """Load courses registered by the student into the table."""
        self.registered_courses = self.student_utils.get_registered_courses_full()

        # Debug: see what is returned
        print("[DEBUG] Registered courses:", self.registered_courses)

        table = self.ui.tableCourses
        table.setRowCount(len(self.registered_courses))

        for row, course in enumerate(self.registered_courses):
            table.setItem(row, 1, QTableWidgetItem(str(row + 1)))
            table.setItem(row, 2, QTableWidgetItem(course.get("course_id", "")))
            table.setItem(row, 3, QTableWidgetItem(str(course.get("credit", ""))))
            table.setItem(row, 4, QTableWidgetItem(str(course.get("section", ""))))
            table.setItem(row, 5, QTableWidgetItem(course.get("days", "")))
            table.setItem(row, 6, QTableWidgetItem(course.get("time", "")))
            table.setItem(row, 7, QTableWidgetItem(course.get("room", "")))
            table.setItem(row, 8, QTableWidgetItem(course.get("instructor", "")))

        self.ui.buttonRemoveSelected.setEnabled(False)

    def on_selection_changed(self):
        """Enable/disable Remove button based on row selection."""
        table = self.ui.tableCourses
        selected = table.selectionModel().selectedRows()
        self.ui.buttonRemoveSelected.setEnabled(bool(selected))

    def remove_selected_courses(self):
        """Remove selected courses from database and table."""
        table = self.ui.tableCourses
        selected_rows = sorted([idx.row() for idx in table.selectionModel().selectedRows()], reverse=True)

        for row in selected_rows:
            course_id = table.item(row, 2).text()
            self.student_utils.remove_registered_course(course_id)
            table.removeRow(row)

        # Re-number "#" column
        for i in range(table.rowCount()):
            table.setItem(i, 1, QTableWidgetItem(str(i + 1)))

        self.ui.buttonRemoveSelected.setEnabled(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = CurrentScheduleWidget(student_id=7500003)
    w.show()
    sys.exit(app.exec())
