import sys
from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox

# واجهة إضافة الكورس (مولدة من Qt Designer)
from app_ui.admin_ui.submenus_ui.ui_add_courses_dialog import Ui_AddCourseDialog

# كلاس الأدوات المشتركة اللي فيه الهز + اللون الأحمر + الفاليديشن
from helper_files.shared_utilities import BaseLoginForm

# نستعمل الكائن الجاهز admin اللي في class_admin_utilities
from admin.class_admin_utilities import admin   # انتبه: هنا نجيب الـ instance الجاهز, مو الكلاس فقط


class AddCourseDialog(QDialog, BaseLoginForm):
    """
    Dialog مسؤول عن:
    - قراءة الحقول
    - التحقق من المدخلات
    - استخدام الاهتزاز
    - استدعاء add_course
    """

    def __init__(self, admin_utils, parent=None):
        QDialog.__init__(self, parent)
        BaseLoginForm.__init__(self, parent)

        self.ui = Ui_AddCourseDialog()
        self.ui.setupUi(self)

        self.admin_utils = admin_utils

        self.ui.buttonSave.clicked.connect(self.on_save_clicked)
        self.ui.buttonCancel.clicked.connect(self.reject)
        if hasattr(self.ui, "buttonClose"):
            self.ui.buttonClose.clicked.connect(self.reject)

        self.attach_non_empty_validator(self.ui.lineEditCourseCode, "Course code")
        self.attach_non_empty_validator(self.ui.lineEditCourseName, "Course name")
        self.attach_non_empty_validator(self.ui.lineEditCreditHours, "Credit hours")

    # ------------------------ رسائل منبثقة بخط أسود وخلفية بيضاء ------------------------

    def show_error(self, message: str):
        """عرض رسالة خطأ بخط أسود."""
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Critical)
        box.setWindowTitle("Error")
        box.setText(message)
        box.setStandardButtons(QMessageBox.StandardButton.Ok)

        box.setStyleSheet("""
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
        """)

        box.exec()

    def show_info(self, message: str):
        """عرض رسالة نجاح بخط أسود."""
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Information)
        box.setWindowTitle("Success")
        box.setText(message)
        box.setStandardButtons(QMessageBox.StandardButton.Ok)

        box.setStyleSheet("""
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
        """)

        box.exec()

    # ------------------------ حدث زر الحفظ ------------------------

    def on_save_clicked(self):
        code = self.ui.lineEditCourseCode.text().strip().upper()
        name = self.ui.lineEditCourseName.text().strip()
        credits_text = self.ui.lineEditCreditHours.text().strip()

        has_error = False

        if code == "":
            self.highlight_invalid_lineedit(self.ui.lineEditCourseCode, "Course code cannot be empty.")
            self.shake_widget(self.ui.lineEditCourseCode)
            has_error = True
        else:
            self.reset_lineedit_border(self.ui.lineEditCourseCode)

        if name == "":
            self.highlight_invalid_lineedit(self.ui.lineEditCourseName, "Course name cannot be empty.")
            self.shake_widget(self.ui.lineEditCourseName)
            has_error = True
        else:
            self.reset_lineedit_border(self.ui.lineEditCourseName)

        if credits_text == "":
            self.highlight_invalid_lineedit(self.ui.lineEditCreditHours, "Credit hours cannot be empty.")
            self.shake_widget(self.ui.lineEditCreditHours)
            has_error = True
        else:
            if not credits_text.isdigit():
                self.highlight_invalid_lineedit(self.ui.lineEditCreditHours, "Credit hours must be a positive integer.")
                self.shake_widget(self.ui.lineEditCreditHours)
                has_error = True
            else:
                credits = int(credits_text)
                if credits <= 0:
                    self.highlight_invalid_lineedit(self.ui.lineEditCreditHours, "Credit hours must be greater than 0.")
                    self.shake_widget(self.ui.lineEditCreditHours)
                    has_error = True
                else:
                    self.reset_lineedit_border(self.ui.lineEditCreditHours)

        if has_error:
            self.show_error("Please fix the highlighted fields.")
            return

        msg = self.admin_utils.add_course(code, name, int(credits_text))

        if msg.lower().startswith("course already"):
            self.highlight_invalid_lineedit(self.ui.lineEditCourseCode, msg)
            self.shake_widget(self.ui.lineEditCourseCode)
            self.show_error(msg)
            return

        self.show_info(msg)
        self.accept()


# =============================== MAIN ===============================

if __name__ == "__main__":
    app = QApplication(sys.argv)

    dialog = AddCourseDialog(admin)
    dialog.show()

    sys.exit(app.exec())
