import os
import sys

from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QMessageBox,
)

# نخلي المشروع الأساسي في الـ sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app_ui.admin_ui.submenus_ui.ui_add_course_to_plan_dialog import Ui_AddCourseDialog
from helper_files.shared_utilities import BaseLoginForm
from admin.class_admin_utilities import AdminUtilities  # لو تحتاج الكلاس
from admin.class_admin_utilities import admin  # الكائن الجاهز لو بتشغّل الملف مباشرة


class AddCourseToPlanDialog(QDialog, BaseLoginForm):
    """
    Dialog مسؤول عن:
    - اختيار كورس من قائمة المواد
    - اختيار برنامج من قائمة ثابتة ('PWM','BIO','COMM','COMP')
    - اختيار المستوى (Level)
    - استدعاء admin_add_course_to_plan
    """

    def __init__(self, admin_utils, parent=None):
        QDialog.__init__(self, parent)
        BaseLoginForm.__init__(self, parent)

        self.ui = Ui_AddCourseDialog()
        self.ui.setupUi(self)

        self.admin_utils = admin_utils  # كائن AdminUtilities موجود عندك في الداشبورد

        # تعبئة الكورسات من الداتابيس
        self.populate_courses_combo()

        # تعبئة البرامج بالقيم الأربع الثابتة
        self.populate_programs_combo()

        # زر الحفظ مبدئياً مقفول
        self.ui.buttonSave.setEnabled(False)

        # ربط الأزرار
        self.ui.buttonSave.clicked.connect(self.on_save_clicked)
        self.ui.buttonCancel.clicked.connect(self.reject)

        # ربط تغيّر الحقول مع فحص تفعيل زر الحفظ
        self.ui.comboBoxSelectCourse.currentIndexChanged.connect(self.check_all_fields_filled)
        self.ui.comboBoxSelectProgram.currentIndexChanged.connect(self.check_all_fields_filled)
        self.ui.spinBoxLevel.valueChanged.connect(self.check_all_fields_filled)

        # تشيك أولي
        self.check_all_fields_filled()

    # ------------------------ تعبئة كومبو الكورسات ------------------------

    def populate_courses_combo(self):
        """
        يجيب المواد من جدول courses (list_courses)
        ويحطها في comboBoxSelectCourse
        """
        self.ui.comboBoxSelectCourse.clear()
        self.ui.comboBoxSelectCourse.addItem("Select a course...", None)

        # من كلاس الداتابيس عندك: list_courses يرجع (code, name, credits)
        rows = self.admin_utils.db.ListCourses()

        for code, name, credits in rows:
            display = f"{code} - {name}"
            # نخزن code كـ data عشان نستخدمه مباشرة
            self.ui.comboBoxSelectCourse.addItem(display, code)

    # ------------------------ تعبئة كومبو البرامج ------------------------

    def populate_programs_combo(self):
        """
        تعبئة قائمة البرامج من قيم ثابتة:
        'PWM','BIO','COMM','COMP'
        """
        self.ui.comboBoxSelectProgram.clear()
        self.ui.comboBoxSelectProgram.addItem("Select program...", None)

        programs = [
            ("PWM",  "Power & Machines Engineering"),
            ("BIO",  "Biomedical Engineering"),
            ("COMM", "Communications Engineering"),
            ("COMP", "Computer Engineering"),
        ]

        for code, label in programs:
            text = f"{code} - {label}"
            # نخزن code كـ data (PWM/BIO/COMM/COMP)
            self.ui.comboBoxSelectProgram.addItem(text, code)

    # ------------------------ تفعيل/تعطيل زر الحفظ ------------------------

    def check_all_fields_filled(self):
        """
        يفعّل زر الحفظ لو:
        - اختار كورس
        - اختار برنامج
        - level >= 1
        """
        course_ok = self.ui.comboBoxSelectCourse.currentIndex() > 0
        program_ok = self.ui.comboBoxSelectProgram.currentIndex() > 0
        level_value = self.ui.spinBoxLevel.value()
        level_ok = level_value >= 1

        if course_ok and program_ok and level_ok:
            self.ui.buttonSave.setEnabled(True)
        else:
            self.ui.buttonSave.setEnabled(False)

    # ------------------------ رسائل منبثقة ------------------------

    def show_error(self, message: str):
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Critical)
        box.setWindowTitle("Error")
        box.setText(message)
        box.setStandardButtons(QMessageBox.StandardButton.Ok)
        box.setStyleSheet(
            """
            QMessageBox {
                background-color: white;
                color: black;
            }
            QMessageBox QLabel {
                color: black;
                font-size: 12pt;
            }
            QMessageBox QPushButton {
                color: black;
                padding: 6px 14px;
            }
            """
        )
        box.exec()

    def show_info(self, message: str):
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Information)
        box.setWindowTitle("Success")
        box.setText(message)
        box.setStandardButtons(QMessageBox.StandardButton.Ok)
        box.setStyleSheet(
            """
            QMessageBox {
                background-color: white;
                color: black;
            }
            QMessageBox QLabel {
                color: black;
                font-size: 12pt;
            }
            QMessageBox QPushButton {
                color: black;
                padding: 6px 14px;
            }
            """
        )
        box.exec()

    # ------------------------ حدث زر الحفظ ------------------------

    def on_save_clicked(self):
        """
        يقرأ:
        - course_code من comboBoxSelectCourse
        - program من comboBoxSelectProgram (PWM/BIO/COMM/COMP)
        - level من spinBoxLevel
        ثم يستدعي admin_add_course_to_plan
        """
        course_code = self.ui.comboBoxSelectCourse.currentData()
        program = self.ui.comboBoxSelectProgram.currentData()
        level = self.ui.spinBoxLevel.value()

        # احتياط بس، مع أن زر الحفظ ما يشتغل إلا لو كلها متوفرة


        try:
            msg = self.admin_utils.admin_add_course_to_plan(
                program=program,
                course_code=course_code,
                level=level,
            )
        except Exception as e:
            self.show_error(f"Error while adding course to plan:\n{e}")
            return

        self.show_info(msg)
        self.accept()


# =============================== MAIN لتجربة الدايالوج لوحده ===============================

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # هنا أستخدم الكائن الجاهز admin اللي عندكم
    dlg = AddCourseToPlanDialog(admin)
    dlg.show()

    sys.exit(app.exec())
