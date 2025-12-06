import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import (
    QWidget, QTableWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt

from app_ui.admin_ui.submenus_ui.ui_manage_students import Ui_ManageStudents
from helper_files.shared_utilities import BaseLoginForm
from database_files.initialize_database import initialize_database
from database_files.class_database_uitlities import DatabaseUtilities
from admin.class_admin_utilities import AdminUtilities

# صفحة تسجيل المواد للطالب
from student.submenus.class_register_courses import RegisterCoursesWidget
# صفحة الجدول الحالي (حذف الشعب) 👈 الجديد
from student.submenus.class_current_schedule import CurrentScheduleWidget


class ManageStudentsController:
    """
    نفس فكرة AllStudentsController لكن شغالة مع Ui_ManageStudents:
    - تعرض فقط الطلاب (state = 'student' و account_status = 'active')
    - فلتر بالنص (name / id / email / program)
    - فلتر بالبرنامج من comboBoxSelectProgram
    - تحدث عدّاد الطلاب في labelTotalStudentsCount
    - أزرار:
        * buttonAddGrades      -> لا مربوطة الآن
        * buttonAddStudent     -> تفتح صفحة RegisterCoursesWidget للطالب المحدد
        * buttonRemoveSelected -> تفتح صفحة CurrentScheduleWidget للطالب المحدد
    """

    def __init__(self, ui: Ui_ManageStudents, admin_utils: AdminUtilities):
        self.ui = ui
        self.admin = admin_utils          # كائن الأدمن
        self.db = admin_utils.db          # نفس الـ DatabaseUtilities
        self.students_data = []           # كل الطلاب (active فقط)
        self.blf = BaseLoginForm()

        # نحتفظ بالنوافذ عشان ما تنحذف من الـ GC
        self.register_window = None
        self.current_schedule_window = None

        # نخلي الأزرار مقفلة مبدئياً
        self.ui.buttonAddStudent.setEnabled(False)
        self.ui.buttonRemoveSelected.setEnabled(False)

        # --- ربط إشارات الواجهة المهمة فقط ---
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

        # زر التحديث
        self.ui.buttonRefresh.clicked.connect(self.handle_refresh)

        # زر Register Course for student
        self.ui.buttonAddStudent.clicked.connect(self.handle_add_student_courses)

        # زر Remove Course for student 👈 الجديد
        self.ui.buttonRemoveSelected.clicked.connect(self.handle_remove_student_courses)

        # لما يتغيّر الاختيار في الجدول → نفعّل/نلغي الأزرار
        self.ui.tableAllStudents.selectionModel().selectionChanged.connect(
            self.on_selection_changed
        )

        # أول مرة نعمل Refresh أنيميشن + تحميل
        self.handle_refresh()

    # ----------------- LOAD / POPULATE TABLE -----------------
    def load_students(self):
        """
        تجيب كل المستخدمين من db.list_users
        ثم نفلترهم:
          - account_status = 'active'
          - state = 'student'
        ونخزنهم في self.students_data
        """
        self.students_data.clear()
        self.ui.tableAllStudents.setRowCount(0)

        rows = self.db.list_users()
        # row = (user_id, name, email, program, state, account_status, password_h)

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
        """
        أنيميشن بسيطة على العداد وبعدين تعيد تحميل الطلاب.
        """
        BaseLoginForm.animate_label_with_dots(
            self.ui.labelTotalStudentsCount,
            base_text="Refreshing",
            interval=400,
            duration=2000,
            on_finished=self.load_students
        )

    def format_table(self):
        """
        تنسيق أعمدة الجدول (عدد الأعمدة مضبوط أصلاً من الـ UI: 6 أعمدة)
        (#, ID, NAME, EMAIL, PROGRAM, STATE)
        """
        table = self.ui.tableAllStudents
        header = table.horizontalHeader()
        header.setStretchLastSection(True)

        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(60)

        table.setColumnWidth(0, 60)    # #
        table.setColumnWidth(1, 100)   # ID
        table.setColumnWidth(2, 220)   # NAME
        table.setColumnWidth(3, 260)   # EMAIL
        table.setColumnWidth(4, 110)   # PROGRAM
        table.setColumnWidth(5, 100)   # STATE

    # ----------------- POPULATE TABLE -----------------
    def fill_table(self, students):
        """
        تعبئة الجدول بالطلاب المعطين في list[dict].
        """
        table = self.ui.tableAllStudents
        table.setRowCount(len(students))

        for row_idx, student in enumerate(students):
            # 0: Row number
            item_number = QTableWidgetItem(str(row_idx + 1))
            item_number.setFlags(
                Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
            )
            table.setItem(row_idx, 0, item_number)

            # 1: Student ID
            item_id = QTableWidgetItem(str(student["user_id"]))
            item_id.setFlags(
                Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
            )
            table.setItem(row_idx, 1, item_id)

            # 2: Name
            table.setItem(row_idx, 2, QTableWidgetItem(student["name"] or ""))

            # 3: Email
            table.setItem(row_idx, 3, QTableWidgetItem(student["email"] or ""))

            # 4: Program
            prog_text = student["program"] or ""   # مهم عشان ما يكرش لو None
            table.setItem(row_idx, 4, QTableWidgetItem(prog_text))

            # 5: State
            table.setItem(row_idx, 5, QTableWidgetItem(student["state"] or ""))

    # ----------------- SEARCH + PROGRAM FILTER -----------------
    def search_and_filter(self):
        """
        يطبق فلتر النص + فلتر البرنامج معاً.
        - النص: name / id / email / program
        - البرنامج: من الكومبو بوكس (All Programs / Computer / Communication / Power / Biomedical)
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

    # ----------------- تفعيل الأزرار حسب الاختيار -----------------
    def on_selection_changed(self, *_):
        """
        يتفعّل الأزرار فقط إذا فيه طالب واحد على الأقل محدد.
        (لو تبغاهم لطالب واحد فقط نقدر نغيّر الشرط لـ == 1)
        """
        selected_rows = self.ui.tableAllStudents.selectionModel().selectedRows()
        has_selection = len(selected_rows) > 0

        self.ui.buttonAddStudent.setEnabled(has_selection)
        self.ui.buttonRemoveSelected.setEnabled(has_selection)

    # ----------------- زر Register Course for student -----------------
    def handle_add_student_courses(self):
        """
        - يتأكد إن فيه طالب واحد بس محدد.
        - ياخذ الـ ID من العمود 1.
        - يفتح RegisterCoursesWidget لهذا الطالب.
        """
        table = self.ui.tableAllStudents
        selected_rows = table.selectionModel().selectedRows()

        if not selected_rows:
            QMessageBox.warning(
                None,
                "No Student Selected",
                "Please select a student first."
            )
            return

        if len(selected_rows) > 1:
            QMessageBox.warning(
                None,
                "Multiple Students Selected",
                "Please select only ONE student to register courses."
            )
            return

        row = selected_rows[0].row()
        id_item = table.item(row, 1)  # عمود ID

        if not id_item:
            QMessageBox.warning(
                None,
                "Error",
                "Cannot read student ID from the selected row."
            )
            return

        try:
            student_id = int(id_item.text())
        except ValueError:
            QMessageBox.warning(
                None,
                "Error",
                "Invalid student ID value."
            )
            return

        # هنا تقدر تحدد السمستر لو عندك قيمة معيّنة، حالياً None
        self.register_window = RegisterCoursesWidget(student_id, semester=None)
        self.register_window.show()

    # ----------------- زر Remove Course for student (يفتح CurrentSchedule) -----------------
    def handle_remove_student_courses(self):
        """
        - يتأكد إن فيه طالب واحد بس محدد.
        - ياخذ الـ ID من العمود 1.
        - يفتح CurrentScheduleWidget لهذا الطالب عشان يحذف الشعب.
        """
        table = self.ui.tableAllStudents
        selected_rows = table.selectionModel().selectedRows()

        if not selected_rows:
            QMessageBox.warning(
                None,
                "No Student Selected",
                "Please select a student first."
            )
            return

        if len(selected_rows) > 1:
            QMessageBox.warning(
                None,
                "Multiple Students Selected",
                "Please select only ONE student to remove sections."
            )
            return

        row = selected_rows[0].row()
        id_item = table.item(row, 1)  # عمود ID

        if not id_item:
            QMessageBox.warning(
                None,
                "Error",
                "Cannot read student ID from the selected row."
            )
            return

        try:
            student_id = int(id_item.text())
        except ValueError:
            QMessageBox.warning(
                None,
                "Error",
                "Invalid student ID value."
            )
            return

        # نفتح صفحة الجدول الحالي للطالب (CurrentScheduleWidget)
        self.current_schedule_window = CurrentScheduleWidget(student_id)
        self.current_schedule_window.show()

    # ----------------- UPDATE TOTAL COUNTER -----------------
    def update_total_counter(self):
        self.ui.labelTotalStudentsCount.setText(
            f"Total Students: {len(self.students_data)}"
        )


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
