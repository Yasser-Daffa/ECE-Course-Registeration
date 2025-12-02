import os, sys, functools
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import (
    QWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt

from app_ui.admin_ui.submenus_ui.ui_manage_courses import Ui_ManageCourses
from app_ui.admin_ui.submenus_ui.ui_add_courses_dialog import Ui_AddCourseDialog 

from helper_files.shared_utilities import BaseLoginForm

from database_files.initialize_database import initialize_database
from database_files.class_database_uitlities import DatabaseUtilities


class ManageCoursesController:

    def __init__(self, ui, db: DatabaseUtilities):
        self.ui = ui
        self.db = db
        self.courses_data = []
        self.blf = BaseLoginForm()

        self.connect_ui_signals()
        self.load_courses()
        self.format_table()

        # track checkbox changes
        # self.ui.tableAllCourses.itemChanged.connect(self.update_remove_button_state)

    # ------------------ SIGNALS ------------------
    def connect_ui_signals(self):
        self.ui.lineEditSearch.textChanged.connect(self.search_courses)
        self.ui.buttonRemoveCourse.clicked.connect(self.remove_selected_courses)
        self.ui.buttonRefresh.clicked.connect(self.handle_refresh)
        self.ui.buttonAddCourse.clicked.connect(self.handle_add_course_clicked)

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

        rows = self.db.ListCourses()  # expected: (code, name, credits)

        for i, row in enumerate(rows, start=1):
            course = {
                "row_number": i,
                "code": row[0],
                "name": row[1],
                "credits": row[2]
            }
            self.courses_data.append(course)

        self.populate_table(self.courses_data)
        self.update_total_counter()

    # ------------------ POPULATE TABLE ------------------
    def populate_table(self, courses):
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

            # Code, Name, Credits
            table.setItem(row_idx, 2, QTableWidgetItem(course["code"]))
            table.setItem(row_idx, 3, QTableWidgetItem(course["name"]))
            table.setItem(row_idx, 4, QTableWidgetItem(str(course["credits"])))

            # Remove button
            btnRemove = QPushButton("Remove")
            btnRemove.setMinimumWidth(70)
            btnRemove.setMinimumHeight(30)
            btnRemove.setStyleSheet(
                "QPushButton {background-color:#f8d7da; color:#721c24; border-radius:5px; padding:4px;} "
                "QPushButton:hover {background-color:#c82333; color:white;}"
            )
            btnRemove.clicked.connect(functools.partial(self.remove_single_course, course["code"]))

            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(4)
            layout.addWidget(btnRemove)
            table.setCellWidget(row_idx, 5, container)

    # ------------------ FORMAT TABLE ------------------
    def format_table(self):
        table = self.ui.tableAllCourses
        headers = ["S", "#", "Course Code", "Name", "Credits", "Actions"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)

        header = table.horizontalHeader()

        # checkbox column fixed
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(0, 40)

        # others resizable
        for col in range(1, len(headers)):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)

        table.verticalHeader().setDefaultSectionSize(80)
        table.setColumnWidth(1, 50)
        table.setColumnWidth(2, 140)
        table.setColumnWidth(3, 240)

    # ------------------ SEARCH ------------------
    def search_courses(self):
        text = self.ui.lineEditSearch.text().lower()
        filtered = [
            c for c in self.courses_data
            if text in c["code"].lower() or text in c["name"].lower()
        ]
        self.populate_table(filtered)

    # ------------------ REMOVE SINGLE ------------------
    def remove_single_course(self, code):
        reply = self.blf.show_confirmation(
            "Delete Course",
            f"Are you sure you want to delete course '{code}'?"
        )

        if reply == QMessageBox.StandardButton.Yes:
            msg = self.db.DeleteCourse(code)
            print(msg)
            self.load_courses()

    # ------------------ REMOVE SELECTED ------------------
    def get_selected_course_codes(self):
        table = self.ui.tableAllCourses
        codes = []
        for row in range(table.rowCount()):
            item = table.item(row, 0)
            if item and item.checkState() == Qt.CheckState.Checked:
                codes.append(table.item(row, 2).text())
        return codes

    def remove_selected_courses(self):
        selected = self.get_selected_course_codes()

        # if no checkboxes selected → delete ALL
        if not selected:
            reply = self.blf.show_confirmation(
                "Delete All Courses",
                "Are you sure you want to delete ALL courses?"
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

            self.db.cur.execute("DELETE FROM courses")
            self.db.commit()
            self.load_courses()
            return

        # delete selected only
        reply = self.blf.show_confirmation(
            "Delete Selected Courses",
            f"Delete {len(selected)} selected course(s)?"
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        for code in selected:
            self.db.DeleteCourse(code)

        self.load_courses()

    # ------------------ ADD COURSE ------------------
    def handle_add_course_clicked(self):
        # You can replace this with a QDialog later.
        print("\nAdd Course button clicked (connect to dialog here)\n")
        

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

    controller = ManageCoursesController(ui, db)

    window.show()
    sys.exit(app.exec())
