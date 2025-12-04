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
from admin.class_admin_utilities import admin


class AddCourseToPlanDialog(QDialog):
    """
    Dialog لإضافة كورس إلى خطة:
    - اختيار كورس
    - اختيار برنامج (PWM/BIO/COMM/COMP)
    - اختيار Level
    - استدعاء admin_add_course_to_plan
    """

    def __init__(self, admin_utils, parent=None):
        super().__init__(parent)

        self.ui = Ui_AddCourseDialog()
        self.ui.setupUi(self)

        self.admin_utils = admin_utils

        self.populate_courses_combo()
        self.populate_programs_combo()

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
            cb.addItem(f"{code} - {name}", code)

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
            cb.addItem(f"{code} - {label}", code)

    # ------------------------ تفعيل زر الحفظ ------------------------

    def check_all_fields_filled(self):
        course_ok = self.ui.comboBoxSelectCourse.currentIndex() > 0
        program_ok = self.ui.comboBoxSelectProgram.currentIndex() > 0
        level_ok = self.ui.spinBoxLevel.value() >= 1

        self.ui.buttonSave.setEnabled(course_ok and program_ok and level_ok)

    # ------------------------ رسائل كلاسيكية (زي زمان) ------------------------

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
        course_code = self.ui.comboBoxSelectCourse.currentData()
        program = self.ui.comboBoxSelectProgram.currentData()
        level = self.ui.spinBoxLevel.value()

        # احتياط فقط (الزر ما يشتغل إلا لو كل شيء جاهز)
        if not course_code or not program or level < 1:
            self.show_error("Please fill all required fields.")
            return

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


# =============== MAIN للتجربة ===============

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dlg = AddCourseToPlanDialog(admin)
    dlg.show()
    sys.exit(app.exec())
