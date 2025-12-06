import os, sys, functools

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import (
    QWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt

from app_ui.admin_ui.submenus_ui.ui_pending_requests import Ui_PendingRequestsWidget
from helper_files.shared_utilities import BaseLoginForm, EmailSender
from admin.class_admin_utilities import admin  # Using the global admin utilities instance


class PendingRequestsController:
    """
    Controller for pending student approval requests.

    This version uses only AdminUtilities, not raw SQL.
    Student rows are provided by admin_list_pending_students(), which
    returns only inactive, pending student accounts.

    Features:
    - Display pending student accounts
    - Search by name or ID
    - Approve or reject individual students
    - Approve or reject all or selected students
    - Send email notification on approval or rejection
    """

    def __init__(self, ui: Ui_PendingRequestsWidget, admin_utils=admin):
        self.ui = ui
        self.admin = admin_utils               # AdminUtilities instance
        self.students_data = []                # Cached list of pending students
        self.animate = BaseLoginForm.animate_label_with_dots
        self.blf = BaseLoginForm()
        self.es = EmailSender()                # Email sending helper

        # Connect UI events
        self.connect_ui_signals()

        # Load initial pending students
        self.load_pending_students()
        self.format_table()

        # Listen for checkbox updates
        self.ui.tableRequests.itemChanged.connect(self.update_approve_reject_button_state)

    # ----------------------------------------------------------------------
    # UI SIGNAL CONNECTIONS
    # ----------------------------------------------------------------------
    def connect_ui_signals(self):
        # Text search box
        if hasattr(self.ui, "lineEditSearch"):
            self.ui.lineEditSearch.textChanged.connect(self.search_students)

        # Buttons for mass approve/reject
        if hasattr(self.ui, "btnApproveAll"):
            self.ui.btnApproveAll.clicked.connect(self.approve_selected_students)

        if hasattr(self.ui, "btnRejectAll"):
            self.ui.btnRejectAll.clicked.connect(self.reject_selected_students)

        # Refresh button
        self.handle_refresh()
        self.ui.btnRefresh.clicked.connect(self.handle_refresh)

    # ----------------------------------------------------------------------
    # LOAD PENDING STUDENTS
    # ----------------------------------------------------------------------
    def load_pending_students(self):
        """
        Loads all pending students using the admin_list_pending_students() method.

        This method already filters:
        - state = student
        - account_status = inactive
        """
        self.students_data = self.admin.admin_list_pending_students()
        self.ui.tableRequests.setRowCount(0)
        self.fill_table(self.students_data)
        self.update_pending_counter()

    def handle_refresh(self):
        """
        Plays the animated refresh effect and reloads data afterward.
        """
        self.animate(
            self.ui.labelPendingCount,
            base_text="Refreshing",
            interval=400,
            duration=2000,
            on_finished=self.load_pending_students
        )

    # ----------------------------------------------------------------------
    # TABLE POPULATION
    # ----------------------------------------------------------------------
    def fill_table(self, students):
        """
        Populates the table with the given list of pending students.
        """
        table = self.ui.tableRequests
        table.setRowCount(len(students))

        for row_idx, student in enumerate(students):
            # Row number (for display only)
            item_number = QTableWidgetItem(str(row_idx + 1))
            item_number.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(row_idx, 1, item_number)

            # Student ID
            table.setItem(row_idx, 2, QTableWidgetItem(str(student["user_id"])))

            # Name, Email, Program, State
            table.setItem(row_idx, 3, QTableWidgetItem(student["name"]))
            table.setItem(row_idx, 4, QTableWidgetItem(student["email"]))
            table.setItem(row_idx, 5, QTableWidgetItem(student["program"] or ""))
            table.setItem(row_idx, 6, QTableWidgetItem(student["state"] or ""))

            # Approve button
            btnApprove = QPushButton("Approve")
            btnApprove.setMinimumWidth(70)
            btnApprove.setMinimumHeight(30)
            btnApprove.setStyleSheet(
                "QPushButton {background-color:#d4edda; color:#155724; border-radius:5px; padding:4px;} "
                "QPushButton:hover {background-color:#28a745; color:white;}"
            )
            btnApprove.clicked.connect(
                functools.partial(self.approve_student, student["user_id"])
            )

            # Reject button
            btnReject = QPushButton("Reject")
            btnReject.setMinimumWidth(70)
            btnReject.setMinimumHeight(30)
            btnReject.setStyleSheet(
                "QPushButton {background-color:#f8d7da; color:#721c24; border-radius:5px; padding:4px;} "
                "QPushButton:hover {background-color:#c82333; color:white;}"
            )
            btnReject.clicked.connect(
                functools.partial(self.reject_student, student["user_id"])
            )

            # Place Approve + Reject in same cell
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(4)
            layout.addWidget(btnApprove)
            layout.addWidget(btnReject)
            table.setCellWidget(row_idx, 7, container)

            # Checkbox for multi-select
            chk_item = QTableWidgetItem()
            chk_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
            chk_item.setCheckState(Qt.CheckState.Unchecked)
            table.setItem(row_idx, 0, chk_item)

    # ----------------------------------------------------------------------
    # TABLE FORMATTING
    # ----------------------------------------------------------------------
    def format_table(self):
        table = self.ui.tableRequests
        headers = ["S", "#", "Student ID", "Name", "Email", "Program", "State", "Actions"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)

        header = table.horizontalHeader()

        # Fixed width for checkbox
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(0, 40)

        # Remaining columns adjustable
        for col in range(1, len(headers)):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)

        table.verticalHeader().setDefaultSectionSize(100)

    # ----------------------------------------------------------------------
    # SEARCH BAR FILTER
    # ----------------------------------------------------------------------
    def search_students(self):
        text = self.ui.lineEditSearch.text().lower()
        filtered = [
            s for s in self.students_data
            if text in s["name"].lower() or text in str(s["user_id"])
        ]
        self.fill_table(filtered)

    # ----------------------------------------------------------------------
    # APPROVE / REJECT INDIVIDUAL STUDENTS
    # ----------------------------------------------------------------------
    def approve_student(self, user_id):
        """
        Approves a single pending student and sends email.
        """
        reply = self.blf.show_confirmation(
            "Approve Student",
            f"Are you sure you want to approve student ID {user_id}?"
        )
        if reply == QMessageBox.StandardButton.Yes:
            username, email = self.get_user_name_email(user_id)
            msg = self.admin.admin_approve_student(user_id)

            # Send approval email
            self.send_approval_email(username, email)

            print("[ADMIN]", msg)
            self.load_pending_students()

    def reject_student(self, user_id):
        """
        Rejects a single pending student and sends email.
        """
        reply = self.blf.show_confirmation(
            "Reject Student",
            f"Are you sure you want to reject student ID {user_id}?"
        )
        if reply == QMessageBox.StandardButton.Yes:
            username, email = self.get_user_name_email(user_id)
            msg = self.admin.admin_reject_student(user_id)

            # Send rejection email
            self.send_rejection_email(username, email)

            print("[ADMIN]", msg)
            self.load_pending_students()

    # ----------------------------------------------------------------------
    # BULK APPROVE / REJECT
    # ----------------------------------------------------------------------
    def get_selected_user_ids(self):
        """
        Returns the list of selected user IDs from checked rows.
        """
        table = self.ui.tableRequests
        user_ids = []
        for row in range(table.rowCount()):
            item = table.item(row, 0)
            if item and item.checkState() == Qt.CheckState.Checked:
                user_id = int(table.item(row, 2).text())
                user_ids.append(user_id)
        return user_ids

    def approve_selected_students(self):
        selected_ids = self.get_selected_user_ids()

        if not selected_ids:
            # Apply to all pending students
            reply = self.blf.show_confirmation(
                "Approve All Students",
                "Approve all pending students?"
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

            for s in self.students_data:
                self.send_approval_email(s["name"], s["email"])

            msg = self.admin.admin_approve_all_pending_students()
            print("[ADMIN]", msg)
            self.load_pending_students()
            return

        # Approve selected only
        reply = self.blf.show_confirmation(
            "Approve Selected Students",
            f"Approve {len(selected_ids)} selected student(s)?"
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        for uid in selected_ids:
            username, email = self.get_user_name_email(uid)
            self.admin.admin_approve_student(uid)
            self.send_approval_email(username, email)

        self.load_pending_students()

    def reject_selected_students(self):
        selected_ids = self.get_selected_user_ids()

        if not selected_ids:
            reply = self.blf.show_confirmation(
                "Reject All Students",
                "Reject all pending students?"
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

            for s in self.students_data:
                self.send_rejection_email(s["name"], s["email"])

            msg = self.admin.admin_reject_all_pending_students()
            print("[ADMIN]", msg)
            self.load_pending_students()
            return

        reply = self.blf.show_confirmation(
            "Reject Selected Students",
            f"Reject {len(selected_ids)} selected student(s)?"
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        for uid in selected_ids:
            username, email = self.get_user_name_email(uid)
            self.admin.admin_reject_student(uid)
            self.send_rejection_email(username, email)

        self.load_pending_students()

    # ----------------------------------------------------------------------
    # EMAIL SENDING HELPERS
    # ----------------------------------------------------------------------
    def get_user_name_email(self, user_id):
        """
        Helper: returns (name, email) for given user_id from students_data.
        This avoids additional database queries.
        """
        for s in self.students_data:
            if s["user_id"] == user_id:
                return s["name"], s["email"]
        return None, None

    def send_approval_email(self, name, email):
        """
        Sends approval notification email to the student.
        """
        if email is None:
            return

        subject = "Account Approved"
        body = (
            f"Hello {name},\n\n"
            f"Your university account has been approved.\n"
            f"You can now log in and access all available student services.\n\n"
            f"Regards,\nUniversity Administration"
        )
        self.es.send_email(email, subject, body)

    def send_rejection_email(self, name, email):
        """
        Sends rejection notification email to the student.
        """
        if email is None:
            return

        subject = "Account Rejected"
        body = (
            f"Hello {name},\n\n"
            f"Your university account request has been rejected.\n"
            f"If you believe this is an error, please contact support.\n\n"
            f"Regards,\nUniversity Administration"
        )
        self.es.send_email(email, subject, body)

    # ----------------------------------------------------------------------
    # UPDATE BUTTON LABELS BASED ON SELECTION COUNT
    # ----------------------------------------------------------------------
    def update_approve_reject_button_state(self):
        table = self.ui.tableRequests
        selected_count = 0

        for row in range(table.rowCount()):
            item = table.item(row, 0)
            if item and item.checkState() == Qt.CheckState.Checked:
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

    # ----------------------------------------------------------------------
    # UPDATE STUDENT COUNTER LABEL
    # ----------------------------------------------------------------------
    def update_pending_counter(self):
        self.ui.labelPendingCount.setText(f"Total Pending: {len(self.students_data)}")


# ----------------------------------------------------------------------
# STANDALONE TEST
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = QWidget()
    ui = Ui_PendingRequestsWidget()
    ui.setupUi(window)

    controller = PendingRequestsController(ui, admin)

    window.show()
    sys.exit(app.exec())
