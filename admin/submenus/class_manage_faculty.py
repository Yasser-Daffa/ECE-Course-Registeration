# admin/submenus/class_manage_faculty.py

import os, sys, functools
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from PyQt6.QtWidgets import (
    QWidget, QTableWidgetItem, QPushButton, QHBoxLayout,
    QMessageBox, QHeaderView, QDialog, QLineEdit, QVBoxLayout, QLabel
)
from PyQt6.QtCore import Qt

from app_ui.admin_ui.submenus_ui.ui_manage_faculty import Ui_ManageFaculty
from helper_files.shared_utilities import BaseLoginForm, info, warning, error
from helper_files.validators import validate_email, validate_full_name, hash_password
from login_files.class_authentication_window import AuthenticationWindow

from login_files.create_account_for_admin import SignupAndConfirmWindow



class ManageFacultyWidget(QWidget):
    """
    Clean QWidget-based faculty manager:
    - UI loaded in __init__
    - Ready to add directly to stackedWidget
    """

    def __init__(self, db, parent=None):
        super().__init__(parent)

        self.ui = Ui_ManageFaculty()
        self.ui.setupUi(self)

        self.db = db
        self.blf = BaseLoginForm()
        self.faculty_data = []

        # Connect signals
        self.ui.lineEditSearch.textChanged.connect(self.search_faculty)
        self.ui.buttonRefresh.clicked.connect(self.load_faculty)
        self.ui.buttonRemoveSelected.clicked.connect(self.remove_selected_faculty)

        self.ui.buttonAddFaculty.setEnabled(True)
        self.ui.buttonAddFaculty.clicked.connect(self.add_new_faculty)

        self.load_faculty()
        self.format_table()


    # -------------------------------------------------------------
    def format_table(self):
        table = self.ui.tableFaculty
        headers = ["#", "ID", "Name", "Email", "State", "Action"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)

        header = table.horizontalHeader()
        for col in range(len(headers)):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)

        table.verticalHeader().setVisible(False)
        table.setEditTriggers(table.EditTrigger.NoEditTriggers)


    # -------------------------------------------------------------
    def load_faculty(self):
        self.faculty_data.clear()
        self.ui.tableFaculty.setRowCount(0)

        rows = self.db.fetchall("""
            SELECT user_id, name, email, program, state, account_status
            FROM users
            WHERE state = 'instructor'
            ORDER BY user_id ASC
        """)

        for i, row in enumerate(rows, start=1):
            self.faculty_data.append({
                "row_number": i,
                "user_id": row[0],
                "name": row[1],
                "email": row[2],
                "program": row[3],
                "state": row[4],
                "account_status": row[5]
            })

        self.fill_table(self.faculty_data)
        self.update_total_count()
        self.update_remove_button_state()


    # -------------------------------------------------------------
    def fill_table(self, faculty):
        table = self.ui.tableFaculty
        table.setRowCount(len(faculty))

        for row_idx, f in enumerate(faculty):
            table.setItem(row_idx, 0, QTableWidgetItem(str(row_idx + 1)))
            table.setItem(row_idx, 1, QTableWidgetItem(str(f["user_id"])))
            table.setItem(row_idx, 2, QTableWidgetItem(f["name"]))
            table.setItem(row_idx, 3, QTableWidgetItem(f["email"]))
            table.setItem(row_idx, 4, QTableWidgetItem(f["state"]))

            btn = QPushButton("Remove")
            btn.clicked.connect(functools.partial(self.remove_faculty, f["user_id"]))

            container = QWidget()
            lay = QHBoxLayout(container)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.addWidget(btn)

            table.setCellWidget(row_idx, 5, container)

        self.update_remove_button_state()


    # -------------------------------------------------------------
    def search_faculty(self):
        text = self.ui.lineEditSearch.text().lower().strip()

        if not text:
            self.fill_table(self.faculty_data)
            return

        filtered = [f for f in self.faculty_data
                    if text in f["name"].lower() or text in str(f["user_id"])]

        self.fill_table(filtered)


    # -------------------------------------------------------------
    def remove_faculty(self, user_id):
        reply = self.blf.show_confirmation(
            "Remove Faculty",
            f"Are you sure you want to remove instructor ID {user_id}?"
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.execute("DELETE FROM users WHERE user_id=?", (user_id,))
            self.load_faculty()


    # -------------------------------------------------------------
    def remove_selected_faculty(self):
        table = self.ui.tableFaculty
        selected_rows = table.selectionModel().selectedRows()
        ids = [int(table.item(r.row(), 1).text()) for r in selected_rows]

        if not ids:
            warning("Nothing Selected", "No faculty selected.")
            return

        reply = self.blf.show_confirmation(
            "Remove Faculty",
            f"Are you sure you want to remove {len(ids)} instructor(s)?"
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        for uid in ids:
            self.db.execute("DELETE FROM users WHERE user_id=?", (uid,))

        info("Success", f"Removed {len(ids)} instructor(s).")
        self.load_faculty()


    # -------------------------------------------------------------
    def add_new_faculty(self):
        dialog = SignupAndConfirmWindow()

        if dialog.exec() != QDialog.Accepted:
            return

        info("Success", "Faculty member added.")
        self.load_faculty()


    # -------------------------------------------------------------
    def update_remove_button_state(self):
        selected_rows = self.ui.tableFaculty.selectionModel().selectedRows()
        self.ui.buttonRemoveSelected.setEnabled(len(selected_rows) > 0)


    def update_total_count(self):
        self.ui.labelTotalCount.setText(f"{len(self.faculty_data)} Total Faculty")


if __name__ == "__main__":
    import sys, os

    # Add project root so imports work
    ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    sys.path.append(ROOT_DIR)

    from PyQt6.QtWidgets import QApplication
    from admin.class_admin_utilities import AdminUtilities, db

    app = QApplication(sys.argv)

    admin_utils = AdminUtilities(db)

    from admin.submenus.class_manage_faculty import ManageFacultyWidget
    window = ManageFacultyWidget(admin_utils)
    window.show()

    sys.exit(app.exec())


