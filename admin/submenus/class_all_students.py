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
from admin.class_admin_utilities import AdminUtilities


class AllStudentsController:

    def __init__(self, ui: Ui_AllStudents, admin_utils: AdminUtilities):
        self.ui = ui
        self.admin = admin_utils          # كائن الأدمن
        self.db = admin_utils.db          # نفس الـ DatabaseUtilities
        self.students_data = []           # كل الطلاب (active فقط)
        self.blf = BaseLoginForm()

        # --- ربط إشارات الواجهة ---
        self.connect_ui_signals()

        # --- تحميل أولي ---
        self.load_students()
        self.format_table()

    # ----------------- UI SIGNAL CONNECTIONS -----------------
    def connect_ui_signals(self):
        # البحث (name / id / email / program)
        self.ui.lineEditSearch.textChanged.connect(self.search_and_filter)

        # فلتر البرنامج من الكومبو بوكس
        self.ui.comboBoxSelectProgram.currentIndexChanged.connect(self.search_and_filter)

        # زر حذف المحددين
        self.ui.buttonRemoveSelected.clicked.connect(self.remove_selected_students)

        # زر التحديث
        self.ui.buttonRefresh.clicked.connect(self.handle_refresh)

        # تفعيل/تعطيل زر Remove Selected حسب الاختيار
        self.ui.tableAllStudents.selectionModel().selectionChanged.connect(
            lambda: self.update_remove_button_text()
        )

        # أول مرة نعمل Refresh أنيميشن + تحميل
        self.handle_refresh()

    # ----------------- LOAD / POPULATE TABLE -----------------
    def load_students(self):
        self.students_data.clear()
        self.ui.tableAllStudents.setRowCount(0)

        rows = self.db.list_users()
        # row = (user_id, name, email, program, state, account_status, password_h)

        # نجيب فقط الطلاب اللي حالتهم active
        active_rows = [
            row for row in rows
            if row[5] == "active" and row[4] == "student"
        ]

        for i, row in enumerate(active_rows, start=1):
            student = {
                "row_number": i,
                "user_id": row[0],
                "name": row[1],
                "email": row[2],
                "program": row[3],  # ممكن تكون None
                "state": row[4],
                "account_status": row[5],
            }
            self.students_data.append(student)

        # عرض كامل
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

    def format_table(self):
        table = self.ui.tableAllStudents
        header = table.horizontalHeader()
        header.setStretchLastSection(True)
        table.verticalHeader().setDefaultSectionSize(80)
        table.setColumnWidth(0, 60)
        table.setColumnWidth(1, 120)
        table.setColumnWidth(2, 220)
        table.setColumnWidth(3, 260)
        table.setColumnWidth(4, 100)
        table.setColumnWidth(5, 120)
        table.setColumnWidth(6, 120)
        table.setColumnWidth(7, 80)


    # ----------------- POPULATE TABLE -----------------
    def fill_table(self, students):
        table = self.ui.tableAllStudents
        table.setRowCount(len(students))

        for row_idx, student in enumerate(students):
            # 0: Row number
            item_number = QTableWidgetItem(str(row_idx + 1))
            item_number.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            table.setItem(row_idx, 0, item_number)

            # 1: Student ID
            item_id = QTableWidgetItem(str(student["user_id"]))
            item_id.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            table.setItem(row_idx, 1, item_id)

            # 2: Name
            table.setItem(row_idx, 2, QTableWidgetItem(student["name"] or ""))

            # 3: Email
            table.setItem(row_idx, 3, QTableWidgetItem(student["email"] or ""))

            # 4: Program
            prog_text = student["program"] or ""   # <-- مهم عشان ما يكرش لو None
            table.setItem(row_idx, 4, QTableWidgetItem(prog_text))

            # 5: State
            table.setItem(row_idx, 5, QTableWidgetItem(student["state"] or ""))

            # 6: Remove Student button
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
    #
    # ----------------- SEARCH + PROGRAM FILTER -----------------
    def search_and_filter(self):
        """
        يطبق فلتر النص + فلتر البرنامج معاً.
        - النص: name / id / email / program
        - البرنامج: من الكومبوبوكس (All / Computer / Communication / Power / Biomedical)
        """
        text = self.ui.lineEditSearch.text().strip().lower()

        # قيمة الكومبو بوكس
        program_filter = self.ui.comboBoxSelectProgram.currentText()

        # نحدد كود البرنامج اللي نفلتر عليه
        program_map = {
            "Computer": "COMP",
            "Communication": "COMM",
            "Power": "PWM",
            "Biomedical": "BIO",
        }

        # فلتر البرنامج (لو مو "All Programs")
        def match_program(s):
            if program_filter == "All Programs":
                return True  # لا نفلتر بالبروجرام
            code = program_map.get(program_filter)
            # في الداتابيس نخزن الكود مثل COMP / COMM / ...
            return (s["program"] or "") == code

        # فلتر النص
        def match_text(s):
            if not text:
                return True

            name = (s["name"] or "").lower()
            email = (s["email"] or "").lower()
            program_str = (s["program"] or "").lower()
            user_id_str = str(s["user_id"])

            return (
                text in name
                or text in user_id_str
                or text in email
                or text in program_str
            )

        filtered = [
            s for s in self.students_data
            if match_program(s) and match_text(s)
        ]

        self.fill_table(filtered)

    # ----------------- REMOVE INDIVIDUAL STUDENT -----------------
    def remove_student(self, user_id):
        reply = self.blf.show_confirmation(
            "Remove Student",
            f"Are you sure you want to remove student ID {user_id}?"
        )
        if reply == QMessageBox.StandardButton.Yes:
            msg = self.admin.admin_delete_student(user_id)
            print(msg)
            self.load_students()

    # ----------------- REMOVE SELECTED STUDENTS -----------------
    def get_selected_user_ids(self):
        table = self.ui.tableAllStudents
        selected_rows = table.selectionModel().selectedRows()
        ids = []
        for idx in selected_rows:
            item = table.item(idx.row(), 1)  # عمود الـ ID
            if item:
                try:
                    ids.append(int(item.text()))
                except ValueError:
                    # لو فيه كلام مو رقم، نتجاهله بس ما نكرش
                    continue
        return ids

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

            msg = self.admin.admin_delete_all_students()
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
            self.admin.admin_delete_student(uid)

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
    admin_utils = AdminUtilities(db)

    window = QWidget()
    ui = Ui_AllStudents()
    ui.setupUi(window)

    controller = AllStudentsController(ui, admin_utils)

    window.show()
    sys.exit(app.exec())
