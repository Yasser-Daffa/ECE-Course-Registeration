import os, sys, functools
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import (
    QWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt

from app_ui.admin_ui.submenus_ui.ui_pending_requests import Ui_PendingRequestsWidget
from helper_files.shared_utilities import BaseLoginForm
from database_files.initialize_database import initialize_database
from database_files.class_database_uitlities import DatabaseUtilities


class PendingRequestsController:

    def __init__(self, ui: Ui_PendingRequestsWidget, db: DatabaseUtilities):
        self.ui = ui
        self.db = db
        self.students_data = []
        self.animate = BaseLoginForm.animate_label_with_dots
        self.blf = BaseLoginForm()

        # --- Connect UI signals ---
        self.connect_ui_signals()

        # --- Load initial table ---
        self.load_pending_students()
        self.format_table()

        # Track checkbox changes
        self.ui.tableRequests.itemChanged.connect(self.update_approve_reject_button_state)

    # ----------------- UI SIGNAL CONNECTIONS -----------------
    def connect_ui_signals(self):
        if hasattr(self.ui, "lineEditSearch"):
            self.ui.lineEditSearch.textChanged.connect(self.search_students)

        if hasattr(self.ui, "btnApproveAll"):
            self.ui.btnApproveAll.clicked.connect(self.approve_selected_students)
        if hasattr(self.ui, "btnRejectAll"):
            self.ui.btnRejectAll.clicked.connect(self.reject_selected_students)

        self.handle_refresh()
        self.ui.btnRefresh.clicked.connect(self.handle_refresh)

    # ================== LOAD / POPULATE TABLE ==================
    def load_pending_students(self):
        self.students_data.clear()
        self.ui.tableRequests.setRowCount(0)

        self.db.cur.execute("""
            SELECT user_id, name, email, program, state
            FROM users
            WHERE account_status='inactive'
        """)
        rows = self.db.cur.fetchall()

        for i, row in enumerate(rows, start=1):
            student = {
                "row_number": i,
                "user_id": row[0],
                "name": row[1],
                "email": row[2],
                "program": row[3],
                "state": row[4],
            }
            self.students_data.append(student)

        self.populate_table(self.students_data)
        self.update_pending_counter()

    def handle_refresh(self):
        self.animate(
            self.ui.labelPendingCount,
            base_text="Refreshing",
            interval=400,
            duration=2000,
            on_finished=self.load_pending_students
        )

    # ================== POPULATE TABLE ==================
    def populate_table(self, students):
        table = self.ui.tableRequests
        table.setRowCount(len(students))
    
        for row_idx, student in enumerate(students):

            # Row number (first visible column after checkbox)
            item_number = QTableWidgetItem(str(row_idx + 1))
            item_number.setFlags(Qt.ItemFlag.ItemIsEnabled)  # Read-only
            table.setItem(row_idx, 1, item_number)

            # Student ID
            item_id = QTableWidgetItem(str(student["user_id"]))
            table.setItem(row_idx, 2, item_id)

            # Name, Email, Program, State
            table.setItem(row_idx, 3, QTableWidgetItem(student["name"]))
            table.setItem(row_idx, 4, QTableWidgetItem(student["email"]))
            table.setItem(row_idx, 5, QTableWidgetItem(student["program"]))
            table.setItem(row_idx, 6, QTableWidgetItem(student["state"]))

            # Approve / Reject Buttons
            btnApprove = QPushButton("Approve")
            btnApprove.setMinimumWidth(70)
            btnApprove.setMinimumHeight(30)
            btnApprove.setStyleSheet(
                "QPushButton {background-color:#d4edda; color:#155724; border-radius:5px; padding:4px;} "
                "QPushButton:hover {background-color:#28a745; color:white;}"
            )
            btnApprove.clicked.connect(functools.partial(self.approve_student, student["user_id"]))

            btnReject = QPushButton("Reject")
            btnReject.setMinimumWidth(70)
            btnReject.setMinimumHeight(30)
            btnReject.setStyleSheet(
                "QPushButton {background-color:#f8d7da; color:#721c24; border-radius:5px; padding:4px;} "
                "QPushButton:hover {background-color:#c82333; color:white;}"
            )
            btnReject.clicked.connect(functools.partial(self.reject_student, student["user_id"]))

            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(4)
            layout.addWidget(btnApprove)
            layout.addWidget(btnReject)
            table.setCellWidget(row_idx, 7, container)

            # Checkbox
            chk_item = QTableWidgetItem()
            chk_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
            chk_item.setCheckState(Qt.CheckState.Unchecked)
            table.setItem(row_idx, 0, chk_item)

    # ================== TABLE FORMATTING ==================
    def format_table(self):
        table = self.ui.tableRequests
        headers = ["S", "#", "Student ID", "Name", "Email", "Program", "State", "Actions"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)

        header = table.horizontalHeader()

        # First column fixed for checkbox
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(0, 40)

        # All other columns allow user resizing
        for col in range(1, len(headers)):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)

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
        self.populate_table(filtered)

    # ================== APPROVE / REJECT INDIVIDUAL ==================
    def approve_student(self, user_id):
        reply = self.blf.show_confirmation(
            "Approve Student",
            f"Are you sure you want to approve student ID {user_id}?"
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.update_user(user_id, account_status="active")
            self.load_pending_students()

    def reject_student(self, user_id):
        reply = self.blf.show_confirmation(
            "Reject Student",
            f"Are you sure you want to reject student ID {user_id}?"
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.cur.execute("DELETE FROM users WHERE user_id=?", (user_id,))
            self.db.commit()
            self.load_pending_students()

    # ================== APPROVE / REJECT SELECTED ==================
    def get_selected_user_ids(self):
        table = self.ui.tableRequests
        user_ids = []
        for row in range(table.rowCount()):
            item = table.item(row, 0)  # checkbox column
            if item and item.checkState() == Qt.CheckState.Checked:
                user_id = int(table.item(row, 2).text())  # student_id column
                user_ids.append(user_id)
        return user_ids

    def approve_selected_students(self):
        selected_ids = self.get_selected_user_ids()
        if not selected_ids:
            reply = self.blf.show_confirmation(
                "Approve All Students",
                "Are you sure you want to approve all pending students?"
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
            self.db.cur.execute("UPDATE users SET account_status='active' WHERE account_status='inactive'")
            self.db.commit()
            self.load_pending_students()
            return

        reply = self.blf.show_confirmation(
            "Approve Selected Students",
            f"Are you sure you want to approve {len(selected_ids)} selected student(s)?"
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        for uid in selected_ids:
            self.db.update_user(uid, account_status="active")
        self.load_pending_students()

    def reject_selected_students(self):
        selected_ids = self.get_selected_user_ids()
        if not selected_ids:
            reply = self.blf.show_confirmation(
                "Reject All Students",
                "Are you sure you want to reject all pending students?"
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
            self.db.cur.execute("DELETE FROM users WHERE account_status='inactive'")
            self.db.commit()
            self.load_pending_students()
            return

        reply = self.blf.show_confirmation(
            "Reject Selected Students",
            f"Are you sure you want to reject {len(selected_ids)} selected student(s)?"
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        for uid in selected_ids:
            self.db.cur.execute("DELETE FROM users WHERE user_id=?", (uid,))
        self.db.commit()
        self.load_pending_students()

    # ================== UPDATE BUTTON TEXT BASED ON CHECKBOXES ==================
    def update_approve_reject_button_state(self):
        table = self.ui.tableRequests
        selected_count = 0

        for row in range(table.rowCount()):
            item = table.item(row, 0)
            if item and item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                if item.checkState() == Qt.CheckState.Checked:
                    selected_count += 1

        if selected_count > 0:
            self.ui.btnApproveAll.setText(f"Approve Selected ({selected_count})")
            self.ui.btnApproveAll.setEnabled(True)
            self.ui.btnRejectAll.setText(f"Reject Selected ({selected_count})")
            self.ui.btnRejectAll.setEnabled(True)
        else:
            self.ui.btnApproveAll.setText("Approve All")
            self.ui.btnApproveAll.setEnabled(bool(self.students_data))
            self.ui.btnRejectAll.setText("Reject All")
            self.ui.btnRejectAll.setEnabled(bool(self.students_data))

    # ================== UPDATE PENDING COUNTER ==================
    def update_pending_counter(self):
        self.ui.labelPendingCount.setText(str(len(self.students_data)))


# ---------------- MAIN APP ----------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "../../university_database.db")
    con, cur = initialize_database(DB_PATH)
    db = DatabaseUtilities(con, cur)

    window = QWidget()
    ui = Ui_PendingRequestsWidget()
    ui.setupUi(window)

    controller = PendingRequestsController(ui, db)

    window.show()
    sys.exit(app.exec())
