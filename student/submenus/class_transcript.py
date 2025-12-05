import os
import sys

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QTableWidgetItem,
    QMessageBox,
)
from PyQt6.QtCore import Qt

# عشان نضمن الوصول للمجلد الرئيسي للمشروع
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# واجهة الـ Transcript من Qt Designer
from app_ui.student_ui.submenus_ui.ui_transcript import Ui_Transcript

# كلاس الطالب + الداتابيس
from student.class_student_utilities import StudentUtilities, db


class TranscriptWidget(QWidget):
    """
    واجهة تعرض هيستوري الطالب (Transcript) فقط:
    - تجيب كل مواد الطالب من جدول transcripts.
    - تعبي جدول tableCourses بالمعلومات:
        #, COURSE CODE, COURSE NAME, CREDIT, GRADE, SEMESTER
    - تحدث الـ GPA و الـ Completed Credits و Current Credits بشكل بسيط.
    """

    def __init__(self, student_id: int, parent=None):
        super().__init__(parent)

        # تجهيز الواجهة
        self.ui = Ui_Transcript()
        self.ui.setupUi(self)

        self.student_id = student_id
        self.student_utils = StudentUtilities(db, student_id)

        # نبي بس جدول واحد للعرض، فنخفي الجدول الثاني وعنوانه
        # (عشان "بس يستعرض الهيستوري حق الطالب")
        if hasattr(self.ui, "tableHeader_2"):
            self.ui.tableHeader_2.hide()
        if hasattr(self.ui, "tableCourses_2"):
            self.ui.tableCourses_2.hide()

        # إعداد الجدول الأساسي
        self.setup_table()

        # ربط زر التحديث
        self.ui.buttonRefresh.clicked.connect(self.load_transcript)

        # تحميل بيانات الطالب + الهيستوري
        self.load_student_info()
        self.load_transcript()

    # ==================== إعداد الجدول ====================

    def setup_table(self):
        table = self.ui.tableCourses
        table.setSelectionBehavior(table.SelectionBehavior.SelectRows)
        table.setSelectionMode(table.SelectionMode.SingleSelection)
        table.setEditTriggers(table.EditTrigger.NoEditTriggers)
        table.setColumnCount(6)
        headers = ["#", "COURSE CODE", "COURSE NAME", "CREDIT", "GRADE", "SEMESTER"]
        table.setHorizontalHeaderLabels(headers)

        # عرض بسيط للأعمدة
        table.setColumnWidth(0, 60)
        table.setColumnWidth(1, 140)
        table.setColumnWidth(2, 320)
        table.setColumnWidth(3, 80)
        table.setColumnWidth(4, 80)
        table.setColumnWidth(5, 140)

    # ==================== معلومات الطالب (اللي فوق) ====================

    def load_student_info(self):
        try:
            user = self.student_utils.db.get_user_by_id(self.student_id)
            # شكلها: (user_id, name, email, program, state, account_status)
        except Exception as e:
            print(f"[ERROR] load_student_info: {e}")
            user = None

        if not user:
            # ما عندنا إلا الـ student_id، نوريه فوق
            if hasattr(self.ui, "labelMajor"):
                self.ui.labelMajor.setText(f"Student ID: {self.student_id}")
            return

        user_id, name, email, program, state, account_status = user

        # نستخدم العناصر الموجودة في التصميم كـ "مساحة عرض"
        # labelMajor = نعرض فيها البرنامج + الاسم
        if hasattr(self.ui, "labelMajor"):
            major_text = program or "N/A"
            self.ui.labelMajor.setText(f"{major_text}  |  {name} (ID: {user_id})")

        # القسم نخليه ثابت أو حسب برنامجك لو حاب تضبطه لاحقاً
        if hasattr(self.ui, "labelDepartment"):
            self.ui.labelDepartment.setText("Electrical Engineering Department")

    # ==================== تحميل الـ Transcript ====================

    def load_transcript(self):
        """
        يقرأ جدول transcripts لهذا الطالب ويعبي الجدول.
        ويحسب:
        - Completed Credits
        - Current Credits (مسجّلة الآن)
        - GPA بسيطة (اختيارية)
        """
        table = self.ui.tableCourses
        table.setRowCount(0)

        try:
            # (course_code, semester, grade)
            rows = self.student_utils.db.list_transcript(self.student_id)
        except Exception as e:
            QMessageBox.critical(self, "DB Error", f"Failed to load transcript:\n{e}")
            return

        # نجيب معلومات المواد عشان الاسم + الساعات
        courses_info = self.student_utils.db.ListCourses()  # (code, name, credits)
        course_map = {c[0]: (c[1], c[2]) for c in courses_info}

        total_completed_credits = 0
        total_points = 0.0
        total_credits_for_gpa = 0

        # خريطة بسيطة من حرف الدرجة إلى نقاط (تقديرية، عدلها لو عندكم نظام معين)
        grade_points = {
            "A+": 5.0,
            "A": 4.75,
            "B+": 4.5,
            "B": 4.0,
            "C+": 3.5,
            "C": 3.0,
            "D+": 2.5,
            "D": 2.0,
            "F": 1.0,
        }

        table.setRowCount(len(rows))

        for i, (course_code, semester, grade) in enumerate(rows):
            name, credits = course_map.get(course_code, (course_code, 0))
            credits = credits or 0

            # # (index)
            item_idx = QTableWidgetItem(str(i + 1))
            item_idx.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            table.setItem(i, 0, item_idx)

            # COURSE CODE
            item_code = QTableWidgetItem(course_code)
            item_code.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            table.setItem(i, 1, item_code)

            # COURSE NAME
            item_name = QTableWidgetItem(str(name))
            item_name.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            table.setItem(i, 2, item_name)

            # CREDIT
            item_credits = QTableWidgetItem(str(credits))
            item_credits.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            table.setItem(i, 3, item_credits)

            # GRADE
            grade_text = grade if grade is not None else ""
            item_grade = QTableWidgetItem(grade_text)
            item_grade.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            table.setItem(i, 4, item_grade)

            # SEMESTER
            item_semester = QTableWidgetItem(str(semester))
            item_semester.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            table.setItem(i, 5, item_semester)

            # نحسب الـ credits المكتملة (نفترض أي درجة غير None تعتبر مادة منتهية)
            if grade is not None and grade != "":
                total_completed_credits += credits

                # حساب بسيط لـ GPA إذا الدرجة موجودة في القيم
                gp = grade_points.get(str(grade).upper())
                if gp is not None and credits > 0:
                    total_points += gp * credits
                    total_credits_for_gpa += credits

        # ==== نحدّث البوكسات اللي فوق ====

        # Completed Credits
        if hasattr(self.ui, "labelCompletedCreditsCount"):
            self.ui.labelCompletedCreditsCount.setText(str(total_completed_credits))

        # Current Credits = مجموع الكردتس للمواد المسجّلة حالياً (من جدول registrations)
        current_credits = 0
        try:
            current_regs = self.student_utils.get_registered_courses_full()
            for reg in current_regs:
                current_credits += reg.get("credit", 0)
        except Exception as e:
            print(f"[WARN] Failed to compute current credits: {e}")

        if hasattr(self.ui, "labelCurrentCreditsCount"):
            self.ui.labelCurrentCreditsCount.setText(str(current_credits))

        # Overall GPA
        if total_credits_for_gpa > 0:
            gpa = total_points / total_credits_for_gpa
            gpa_text = f"{gpa:.2f}"
        else:
            gpa_text = "N/A"

        if hasattr(self.ui, "labelGPACount"):
            self.ui.labelGPACount.setText(gpa_text)

        # نقدر نخلي Semester GPA والـ Credits في الهيدر تمثّل مثلاً آخر سمستر
        # أو نخليها N/A حالياً
        if hasattr(self.ui, "labelSemesterGPA"):
            self.ui.labelSemesterGPA.setText("Semester GPA: N/A")
        if hasattr(self.ui, "labelSemesterCreditsCount"):
            self.ui.labelSemesterCreditsCount.setText("Credits: N/A")


# ===== تجربة سريعة من نفس الملف =====
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # غيّر الـ ID حسب طالب حقيقي موجود عندك في جدول users / transcripts
    test_student_id = 2500001

    w = TranscriptWidget(test_student_id)
    w.show()

    sys.exit(app.exec())
