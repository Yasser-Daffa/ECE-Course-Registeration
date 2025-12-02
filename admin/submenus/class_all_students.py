import os, sys, functools
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))




from PyQt6 import QtWidgets
from PyQt6.QtWidgets import (
    QWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt

from app_ui.admin_ui.submenus_ui.ui_all_students import Ui_AllStudents
from helper_files.shared_utilities import BaseLoginForm
from database_files.initialize_database import initialize_database
from database_files.class_database_uitlities import DatabaseUtilities


class AllStudentsController:

    def __init__(self, ui: Ui_AllStudents, db: DatabaseUtilities):
        self.ui = ui
        self.db = db
        self.students_data = []
        self.blf = BaseLoginForm()

        # --- Connect UI signals ---
        self.connect_ui_signals()

        # --- Load initial table ---
        self.load_students()
        self.format_table()

        # Track checkbox changes
        self.ui.tableAllStudents.itemChanged.connect(self.update_remove_button_state)

    # ----------------- UI SIGNAL CONNECTIONS -----------------
    def connect_ui_signals(self):
        self.ui.lineEditSearch.textChanged.connect(self.search_students)
        self.ui.buttonRemoveSelected.clicked.connect(self.remove_selected_students)

        self.handle_refresh()
        self.ui.buttonRefresh.clicked.connect(self.handle_refresh)

    # ================== LOAD / POPULATE TABLE ==================
    def load_students(self):
        self.students_data.clear()
        self.ui.tableAllStudents.setRowCount(0)

        # Get all users
        rows = self.db.list_users()

        # Filter only active students
        active_rows = [row for row in rows if row[5] == "active"]

        for i, row in enumerate(active_rows, start=1):
            student = {
                "row_number": i,
                "user_id": row[0],
                "name": row[1],
                "email": row[2],
                "program": row[3],
                "state": row[4],
                "account_status": row[5]
            }
            self.students_data.append(student)

        self.fill_table(self.students_data)
        self.update_total_counter()

    def handle_refresh(self):
        # use the original animate_label_with_dots method
        BaseLoginForm.animate_label_with_dots(
            self.ui.labelTotalStudentsCount,
            base_text="Refreshing",
            interval=400,
            duration=2000,
            on_finished=self.load_students
        )

    # ================== POPULATE TABLE ==================
    def fill_table(self, students):
        table = self.ui.tableAllStudents
        table.setRowCount(len(students))

        for row_idx, student in enumerate(students):

            # Row number
            item_number = QTableWidgetItem(str(row_idx + 1))
            item_number.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(row_idx, 1, item_number)

            # Student ID
            item_id = QTableWidgetItem(str(student["user_id"]))
            table.setItem(row_idx, 2, item_id)

            # Name, Email, Program, State
            table.setItem(row_idx, 3, QTableWidgetItem(student["name"]))
            table.setItem(row_idx, 4, QTableWidgetItem(student["email"]))
            table.setItem(row_idx, 5, QTableWidgetItem(student["program"]))
            table.setItem(row_idx, 6, QTableWidgetItem(student["state"]))

            # Remove Student button
            btnRemove = QPushButton("Remove")
            btnRemove.setMinimumWidth(70)
            btnRemove.setMinimumHeight(30)
            btnRemove.setStyleSheet(
                "QPushButton {background-color:#f8d7da; color:#721c24; border-radius:5px; padding:4px;} "
                "QPushButton:hover {background-color:#c82333; color:white;}"
            )
            btnRemove.clicked.connect(functools.partial(self.remove_student, student["user_id"]))

            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(4)
            layout.addWidget(btnRemove)
            table.setCellWidget(row_idx, 7, container)

            # Checkbox
            chk_item = QTableWidgetItem()
            chk_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
            chk_item.setCheckState(Qt.CheckState.Unchecked)
            table.setItem(row_idx, 0, chk_item)

    # ================== TABLE FORMATTING ==================
    def format_table(self):
        table = self.ui.tableAllStudents
        headers = ["S", "#", "Student ID", "Name", "Email", "Program", "State", "Actions"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)

        header = table.horizontalHeader()

        # First column fixed for checkbox
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(0, 40)

        # All other columns allow user resizing
        for col in range(1, len(headers)):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)

        table.verticalHeader().setDefaultSectionSize(100)
        table.setColumnWidth(1, 60)  # #
        table.setColumnWidth(2, 120) # Student ID

    # ================== SEARCH ==================
    def search_students(self):
        text = self.ui.lineEditSearch.text().lower()
        filtered = [
            s for s in self.students_data
            if text in s["name"].lower() or text in str(s["user_id"])
        ]
        self.fill_table(filtered)

    # ================== REMOVE INDIVIDUAL STUDENT ==================
    def remove_student(self, user_id):
        reply = self.blf.show_confirmation(
            "Remove Student",
            f"Are you sure you want to remove student ID {user_id}?"
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.cur.execute("DELETE FROM users WHERE user_id=?", (user_id,))
            self.db.commit()
            self.load_students()

    # ================== REMOVE SELECTED STUDENTS ==================
    def get_selected_user_ids(self):
        table = self.ui.tableAllStudents
        user_ids = []
        for row in range(table.rowCount()):
            item = table.item(row, 0)
            if item and item.checkState() == Qt.CheckState.Checked:
                user_id = int(table.item(row, 2).text())
                user_ids.append(user_id)
        return user_ids

    def remove_selected_students(self):
        selected_ids = self.get_selected_user_ids()
        if not selected_ids:
            reply = self.blf.show_confirmation(
                "Remove All Students",
                "Are you sure you want to remove all students?"
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
            self.db.cur.execute("DELETE FROM users")
            self.db.commit()
            self.load_students()
            return

        reply = self.blf.show_confirmation(
            "Remove Selected Students",
            f"Are you sure you want to remove {len(selected_ids)} selected student(s)?"
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        for uid in selected_ids:
            self.db.cur.execute("DELETE FROM users WHERE user_id=?", (uid,))
        self.db.commit()
        self.load_students()

    # ================== UPDATE BUTTON TEXT BASED ON CHECKBOXES ==================
    def update_remove_button_state(self):
        table = self.ui.tableAllStudents
        selected_count = 0

        for row in range(table.rowCount()):
            item = table.item(row, 0)
            if item and item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                if item.checkState() == Qt.CheckState.Checked:
                    selected_count += 1

        if selected_count > 0:
            self.ui.buttonRemoveSelected.setText(f"Remove Selected ({selected_count})")
            self.ui.buttonRemoveSelected.setEnabled(True)
        else:
            self.ui.buttonRemoveSelected.setText("Remove All")
            self.ui.buttonRemoveSelected.setEnabled(bool(self.students_data))

    # ================== UPDATE TOTAL COUNTER ==================
    def update_total_counter(self):
        self.ui.labelTotalStudentsCount.setText(str(f"Total Students: {len(self.students_data)}"))


# ---------------- MAIN APP ----------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "../../university_database.db")
    con, cur = initialize_database(DB_PATH)
    db = DatabaseUtilities(con, cur)

    window = QWidget()
    ui = Ui_AllStudents()
    ui.setupUi(window)

    controller = AllStudentsController(ui, db)

    window.show()
    sys.exit(app.exec())
