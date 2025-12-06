import os, sys, functools
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import (
    QWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt

# واجهة Manage Students الجديدة
from app_ui.admin_ui.submenus_ui.ui_manage_students import Ui_ManageStudents

from helper_files.shared_utilities import BaseLoginForm
from database_files.initialize_database import initialize_database
from database_files.class_database_uitlities import DatabaseUtilities
from admin.class_admin_utilities import AdminUtilities


class ManageStudentsController:
    """
    يعرض كل الطلاب (STATE = 'student' و ACCOUNT_STATUS = 'active')
    مع:
    - بحث بالنص (الاسم / الإيميل / ID / البرنامج)
    - فلترة بالبرنامج من الكومبو بوكس
    - عدّاد Total Students
    * أزرار:
        - Add Grades
        - Register Course for student
        - Remove Course for student
      >>> متروكة بدون ربط كما طلبت.
    """

    def __init__(self, ui: Ui_ManageStudents, admin_utils: AdminUtilities):
        self.ui = ui
        self.admin = admin_utils          # كائن الأدمن
        self.db = admin_utils.db          # نفس الـ DatabaseUtilities
        self.students_data = []           # كل الطلاب (active فقط)
        self.blf = BaseLoginForm()

        # --- ربط إشارات الواجهة (بدون ربط الأزرار الثلاثة) ---
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

        # زر التحديث فقط
        self.ui.buttonRefresh.clicked.connect(self.handle_refresh)

        # ما نربط:
        # self.ui.buttonAddGrades
        # self.ui.buttonAddStudent
        # self.ui.buttonRemoveSelected
        # تترك فاضية عشان تستخدمها لاحقاً للكورسات / الجريد

        # أول مرة نعمل Refresh أنيميشن + تحميل
        self.handle_refresh()

    # ----------------- LOAD / POPULATE TABLE -----------------
    def load_students(self):
        """يجلب كل الطلاب active من جدول users ويعبّي self.students_data"""
        self.students_data.clear()
        self.ui.tableAllStudents.setRowCount(0)

        rows = self.db.list_users()
        # row = (user_id, name, email, program, state, account_status, password_h)

        # نجيب فقط الطلاب اللي حالتهم active و state = student
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

    def handle_refresh(self):
        BaseLoginForm.animate_label_with_dots(
            self.ui.labelTotalStudentsCount,
            base_text="Refreshing",
            interval=400,
            duration=2000,
            on_finished=self.load_students
        )

    def format_table(self):
        """تظبيط أحجام الأعمدة وشكل الجدول"""
        table = self.ui.tableAllStudents

        header = table.horizontalHeader()
        header.setStretchLastSection(True)

        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(60)

        # عندك 6 أعمدة: #, ID, NAME, EMAIL, PROGRAM, STATE
        table.setColumnWidth(0, 60)    # #
        table.setColumnWidth(1, 120)   # ID
        table.setColumnWidth(2, 220)   # NAME
        table.setColumnWidth(3, 260)   # EMAIL
        table.setColumnWidth(4, 120)   # PROGRAM
        table.setColumnWidth(5, 100)   # STATE

        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

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
            prog_text = student["program"] or ""
            table.setItem(row_idx, 4, QTableWidgetItem(prog_text))

            # 5: State
            table.setItem(row_idx, 5, QTableWidgetItem(student["state"] or ""))

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
        # نحدّث العداد بناء على الفلتر الحالي؟ لو تبي:
        # self.ui.labelTotalStudentsCount.setText(f"Total Students: {len(filtered)}")
        # أو تخلي العداد يمثل كل الطلاب:
        self.update_total_counter()

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
    ui = Ui_ManageStudents()
    ui.setupUi(window)

    controller = ManageStudentsController(ui, admin_utils)

    window.show()
    sys.exit(app.exec())
