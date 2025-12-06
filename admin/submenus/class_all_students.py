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
from admin.class_admin_utilities import AdminUtilities   # ← جديد


class AllStudentsController:

    def __init__(self, ui: Ui_AllStudents, admin_utils: AdminUtilities):
        self.ui = ui
        self.admin = admin_utils                 # ← نمسك الأدمن
        self.db = admin_utils.db                # ← لو احتجنا دوال DB الجاهزة مثل list_users
        self.students_data = []
        self.blf = BaseLoginForm()

        # --- Connect UI signals ---
        self.connect_ui_signals()

        # --- Load initial table ---
        self.load_students()
        self.format_table()

    # ----------------- UI SIGNAL CONNECTIONS -----------------
    def connect_ui_signals(self):
        self.ui.lineEditSearch.textChanged.connect(self.search_students)
        self.ui.buttonRemoveSelected.clicked.connect(self.remove_selected_students)
        self.ui.buttonRefresh.clicked.connect(self.handle_refresh)

        # Enable/disable Remove Selected based on row selection
        self.ui.tableAllStudents.selectionModel().selectionChanged.connect(
            lambda: self.update_remove_button_text()
        )

        self.handle_refresh()

    # ----------------- LOAD / POPULATE TABLE -----------------
    def load_students(self):
        self.students_data.clear()
        self.ui.tableAllStudents.setRowCount(0)

        rows = self.db.list_users()
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
        self.update_remove_button_text()

    def handle_refresh(self):
        BaseLoginForm.animate_label_with_dots(
            self.ui.labelTotalStudentsCount,
            base_text="Refreshing",
            interval=400,
            duration=2000,
            on_finished=self.load_students
        )

    # ----------------- POPULATE TABLE -----------------
    def fill_table(self, students):
        table = self.ui.tableAllStudents
        table.setRowCount(len(students))

        for row_idx, student in enumerate(students):
            # Row number
            item_number = QTableWidgetItem(str(row_idx + 1))
            item_number.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            table.setItem(row_idx, 0, item_number)

            # Student ID
            item_id = QTableWidgetItem(str(student["user_id"]))
            item_id.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            table.setItem(row_idx, 1, item_id)

            # Name, Email, Program, State
            table.setItem(row_idx, 2, QTableWidgetItem(student["name"]))
            table.setItem(row_idx, 3, QTableWidgetItem(student["email"]))
            table.setItem(row_idx, 4, QTableWidgetItem(student["program"]))
            table.setItem(row_idx, 5, QTableWidgetItem(student["state"]))

            # Remove Student button
            btnRemove = QPushButton("Remove")
            btnRemove.setMinimumWidth(70)
            btnRemove.setMinimumHeight(30)
            btnRemove.setStyleSheet(
                "QPushButton {background-color:#f8d7da; color:#721c24; border-radius:5px; padding:4px;} "
                "QPushButton:hover {background-color:#c82333; color:white;}"
            )
            btnRemove.clicked.connect(
                functools.partial(self.remove_student, student["user_id"])
            )

            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(4)
            layout.addWidget(btnRemove)
            table.setCellWidget(row_idx, 6, container)

    # ----------------- TABLE FORMATTING -----------------
    def format_table(self):
        table = self.ui.tableAllStudents
        headers = ["#", "Student ID", "Name", "Email", "Program", "State", "Actions"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)

        header = table.horizontalHeader()
        for col in range(len(headers)):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)

        table.verticalHeader().setDefaultSectionSize(100)
        table.setColumnWidth(0, 60)   # #
        table.setColumnWidth(1, 120)  # Student ID

        # Row selection
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)
        table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

    # ----------------- SEARCH -----------------
    def search_students(self):
        text = self.ui.lineEditSearch.text().lower()
        filtered = [
            s for s in self.students_data
            if text in s["name"].lower()
            or text in str(s["user_id"])
            or text in s["program"].lower()   # ← هنا أضفنا البحث بالـ Program
        ]
        self.fill_table(filtered)

    # ----------------- REMOVE INDIVIDUAL STUDENT -----------------
    def remove_student(self, user_id):
        reply = self.blf.show_confirmation(
            "Remove Student",
            f"Are you sure you want to remove student ID {user_id}?"
        )
        if reply == QMessageBox.StandardButton.Yes:
            msg = self.admin.admin_delete_student(user_id)   # ← استعمال AdminUtilities
            print(msg)
            self.load_students()

    # ----------------- REMOVE SELECTED STUDENTS -----------------
    def get_selected_user_ids(self):
        table = self.ui.tableAllStudents
        selected_rows = table.selectionModel().selectedRows()
        return [int(table.item(idx.row(), 1).text()) for idx in selected_rows]  # column 1 = Student ID

    def remove_selected_students(self):
        selected_ids = self.get_selected_user_ids()

        # لو مافي صفوف محددة → اعتبرها "Remove All"
        if not selected_ids:
            reply = self.blf.show_confirmation(
                "Remove All Students",
                "Are you sure you want to remove all students?"
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

            msg = self.admin.admin_delete_all_students()   # ← حذف الكل عن طريق الأدمن
            print(msg)
            self.load_students()
            return

        # لو فيه صفوف محددة
        reply = self.blf.show_confirmation(
            "Remove Selected Students",
            f"Are you sure you want to remove {len(selected_ids)} selected student(s)?"
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        for uid in selected_ids:
            self.admin.admin_delete_student(uid)   # ← حذف فردي عن طريق الأدمن

        self.load_students()

    # ----------------- UPDATE REMOVE BUTTON TEXT -----------------
    def update_remove_button_text(self):
        selected_count = len(self.ui.tableAllStudents.selectionModel().selectedRows())
        if selected_count == 0:
            self.ui.buttonRemoveSelected.setText("Remove Selected")
            self.ui.buttonRemoveSelected.setEnabled(False)
        else:
            self.ui.buttonRemoveSelected.setText(f"Remove Selected ({selected_count})")
            self.ui.buttonRemoveSelected.setEnabled(True)

    # ----------------- UPDATE TOTAL COUNTER -----------------
    def update_total_counter(self):
        self.ui.labelTotalStudentsCount.setText(f"Total Students: {len(self.students_data)}")


# ---------------- MAIN APP (للاختبار فقط) ----------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "../../university_database.db")
    con, cur = initialize_database(DB_PATH)
    db = DatabaseUtilities(con, cur)
    admin_utils = AdminUtilities(db)   # ← نجهز كائن الأدمن

    window = QWidget()
    ui = Ui_AllStudents()
    ui.setupUi(window)

    controller = AllStudentsController(ui, admin_utils)

    window.show()
    sys.exit(app.exec())
