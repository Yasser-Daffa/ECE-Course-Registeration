# manage_course_prerequisites.py

import os, sys, functools
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import (
    QWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt

from app_ui.admin_ui.submenus_ui.not_made.ui_manage_prereq import Ui_ManageCourses
from helper_files.shared_utilities import BaseLoginForm
from database_files.initialize_database import initialize_database
from database_files.class_database_uitlities import DatabaseUtilities


class ManagePrerequisitesController:

    def __init__(self, ui, db: DatabaseUtilities):
        self.ui = ui
        self.db = db
        self.courses_data = []
        self.blf = BaseLoginForm()

        self.connect_ui_signals()
        self.load_courses()
        self.format_table()

    # ------------------ SIGNALS ------------------
    def connect_ui_signals(self):
        self.ui.lineEditSearch.textChanged.connect(self.search_courses)
        self.ui.buttonRefresh.clicked.connect(self.handle_refresh)
        # self.ui.buttonManagePrereq.clicked.connect(self.handle_manage_prereq)

    # ------------------ REFRESH ------------------
    def handle_refresh(self):
        BaseLoginForm.animate_label_with_dots(
            self.ui.labelTotalCoursesCount,
            base_text="Refreshing",
            interval=400,
            duration=2000,
            on_finished=self.load_courses
        )

    # ------------------ LOAD COURSES ------------------
    def load_courses(self):
        self.courses_data.clear()
        self.ui.tableAllCourses.setRowCount(0)

        rows = self.db.ListCourses()  # expected: (code, name, prereq_str)

        for i, row in enumerate(rows, start=1):
            course = {
                "row_number": i,
                "code": row[0],
                "name": row[1],
                "prereq": row[2] if len(row) > 2 else ""  # string of prereq codes
            }
            self.courses_data.append(course)

        self.fill_table(self.courses_data)
        self.update_total_counter()

    # ------------------ POPULATE TABLE ------------------
    def fill_table(self, courses):
        table = self.ui.tableAllCourses
        table.setRowCount(len(courses))

        for row_idx, course in enumerate(courses):

            # Checkbox column
            chk_item = QTableWidgetItem()
            chk_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
            chk_item.setCheckState(Qt.CheckState.Unchecked)
            table.setItem(row_idx, 0, chk_item)

            # Row number
            item_number = QTableWidgetItem(str(row_idx + 1))
            item_number.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(row_idx, 1, item_number)

            # Course Code & Name
            table.setItem(row_idx, 2, QTableWidgetItem(course["code"]))
            table.setItem(row_idx, 3, QTableWidgetItem(course["name"]))

            # Prerequisites column
            table.setItem(row_idx, 4, QTableWidgetItem(course["prereq"]))

    # ------------------ FORMAT TABLE ------------------
    def format_table(self):
        table = self.ui.tableAllCourses
        headers = ["SELECT", "#", "COURSE CODE", "COURSE NAME", "PREREQ"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(0, 40)
        for col in range(1, len(headers)):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)

        table.verticalHeader().setDefaultSectionSize(60)
        table.setColumnWidth(1, 50)
        table.setColumnWidth(2, 140)
        table.setColumnWidth(3, 240)
        table.setColumnWidth(4, 200)

    # ------------------ SEARCH ------------------
    def search_courses(self):
        text = self.ui.lineEditSearch.text().lower()
        filtered = [
            c for c in self.courses_data
            if text in c["code"].lower() or text in c["name"].lower()
        ]
        self.fill_table(filtered)

    # ------------------ MANAGE PREREQUISITES ------------------
    def get_selected_courses(self):
        table = self.ui.tableAllCourses
        selected = []
        for row in range(table.rowCount()):
            item = table.item(row, 0)
            if item and item.checkState() == Qt.CheckState.Checked:
                selected.append(table.item(row, 2).text())
        return selected


    # ------------------ TOTAL COUNTER ------------------
    def update_total_counter(self):
        self.ui.labelTotalCoursesCount.setText(
            f"Total Courses: {len(self.courses_data)}"
        )


# ---------------- MAIN APP ----------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "../../university_database.db")
    con, cur = initialize_database(DB_PATH)
    db = DatabaseUtilities(con, cur)

    window = QWidget()
    ui = Ui_ManageCourses()
    ui.setupUi(window)

    controller = ManagePrerequisitesController(ui, db)

    window.show()
    sys.exit(app.exec())
