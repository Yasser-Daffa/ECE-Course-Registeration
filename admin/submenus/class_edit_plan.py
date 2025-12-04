import os
import sys

from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
)

# نخلي المشروع الأساسي في الـ sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app_ui.admin_ui.submenus_ui.ui_edit_course_to_plan_dialog import Ui_AddCourseDialog
from admin.class_admin_utilities import admin
from helper_files.shared_utilities import warning, info, error


class EditCourseToPlanDialog(QDialog):
    """
    Dialog لتعديل كورس داخل خطة:
    - يستقبل القيم القديمة (program, course_code, level) من الجدول
    - يعرضها في الواجهة
    - عند Save:
        يستدعي admin_update_course_to_plan (اللي جوّاه SQL UPDATE)
    """

    def __init__(self, admin_utils, old_program, old_course_code, old_level, parent=None):
        super().__init__(parent)

        self.ui = Ui_AddCourseDialog()
        self.ui.setupUi(self)

        self.admin_utils = admin_utils

        # نخزن القيم القديمة (نشيّل أي مسافات ونثبت الكيس)
        self.old_program = (old_program or "").strip().upper()
        self.old_course_code = (old_course_code or "").strip().upper()
        self.old_level = old_level

        # نعبّي الكومبوهات
        self.populate_courses_combo()
        self.populate_programs_combo()

        # نختار القيم القديمة في الواجهة
        self.preselect_old_values()

        # زر الحفظ مبدئياً مقفول
        self.ui.buttonSave.setEnabled(False)

        # ربط الأزرار
        self.ui.buttonSave.clicked.connect(self.on_save_clicked)
        self.ui.buttonCancel.clicked.connect(self.reject)

        # فحص الحقول
        self.ui.comboBoxSelectCourse.currentIndexChanged.connect(self.check_all_fields_filled)
        self.ui.comboBoxSelectProgram.currentIndexChanged.connect(self.check_all_fields_filled)
        self.ui.spinBoxLevel.valueChanged.connect(self.check_all_fields_filled)

        self.check_all_fields_filled()

    # ------------------------ تعبئة الكومبوهات ------------------------

    def populate_courses_combo(self):
        """يعبّي قائمة الكورسات من جدول courses"""
        cb = self.ui.comboBoxSelectCourse
        cb.clear()
        cb.addItem("Select a course...", None)

        rows = self.admin_utils.db.ListCourses()  # (code, name, credits)
        for code, name, credits in rows:
            # اللي يبان للمستخدم:
            display = f"{code} - {name}"
            # اللي نخزّنه كـ data (هذا اللي نرسله للداتابيس):
            cb.addItem(display, code.upper())

    def populate_programs_combo(self):
        """يعبّي البرامج بقائمة ثابتة"""
        cb = self.ui.comboBoxSelectProgram
        cb.clear()
        cb.addItem("Select program...", None)

        programs = [
            ("PWM",  "Power & Machines Engineering"),
            ("BIO",  "Biomedical Engineering"),
            ("COMM", "Communications Engineering"),
            ("COMP", "Computer Engineering"),
        ]

        for code, label in programs:
            cb.addItem(f"{code} - {label}", code.upper())

    def preselect_old_values(self):
        """
        يحدد الكورس والبرنامج والـ level القديمة في الواجهة.
        يعتمد على الـ data (مو النص المعروض).
        """
        # 1) الكورس
        cb_course = self.ui.comboBoxSelectCourse
        for i in range(cb_course.count()):
            data = cb_course.itemData(i)
            if data is not None and str(data).upper() == self.old_course_code:
                cb_course.setCurrentIndex(i)
                break

        # 2) البرنامج
        cb_prog = self.ui.comboBoxSelectProgram
        for i in range(cb_prog.count()):
            data = cb_prog.itemData(i)
            if data is not None and str(data).upper() == self.old_program:
                cb_prog.setCurrentIndex(i)
                break

        # 3) المستوى
        try:
            lvl = int(self.old_level)
        except (TypeError, ValueError):
            lvl = 1
        self.ui.spinBoxLevel.setValue(lvl)

    # ------------------------ تفعيل زر الحفظ ------------------------

    def check_all_fields_filled(self):
        course_ok = self.ui.comboBoxSelectCourse.currentIndex() > 0
        program_ok = self.ui.comboBoxSelectProgram.currentIndex() > 0
        level_ok = self.ui.spinBoxLevel.value() >= 1

        self.ui.buttonSave.setEnabled(course_ok and program_ok and level_ok)

    # ------------------------ حدث زر الحفظ ------------------------

    def on_save_clicked(self):
        # 🧠 القيم الجديدة من الـ data (مو النص المعروض)
        new_course_code = self.ui.comboBoxSelectCourse.currentData()
        new_program = self.ui.comboBoxSelectProgram.currentData()
        new_level = self.ui.spinBoxLevel.value()

        if not new_course_code or not new_program or new_level < 1:
            error(self, "Please fill all required fields.")
            return

        # نطبّعهم مثل القديم:
        new_course_code = str(new_course_code).strip().upper()
        new_program = str(new_program).strip().upper()

        try:
            old_level_int = int(self.old_level)
        except (TypeError, ValueError):
            old_level_int = new_level

        # ننادي ميثود الأدمن اللي يسوي UPDATE
        try:
            msg = self.admin_utils.admin_update_course_to_plan(
                old_program=self.old_program,
                old_course_code=self.old_course_code,
                old_level=old_level_int,
                new_program=new_program,
                new_course_code=new_course_code,
                new_level=new_level,
            )
        except Exception as e:
            error(self, f"Error while updating course in plan:\n{e}")
            return

        # لو الداتابيس رجعت فشل → نظهرها كخطأ
        if msg.startswith("✗") or "already" in msg.lower():
            error(self, msg)
            return

        # نجاح ✅
        info(self, msg)

        # نحدّث القيم القديمة عشان لو عدّل مرة ثانية
        self.old_program = new_program
        self.old_course_code = new_course_code
        self.old_level = new_level

        # نقفل بعد تعديل ناجح
        self.accept()


# =============== MAIN للتجربة اليدوية ===============
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # مثال بسيط لو حاب تختبره لحاله
    dlg = EditCourseToPlanDialog(admin, "COMP", "CPE101", 1)
    dlg.show()

    sys.exit(app.exec())


