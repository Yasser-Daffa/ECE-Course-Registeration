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

        # في البداية نعطّل زر الحفظ
        self.ui.buttonSave.setEnabled(False)

        # ربط الأزرار
        self.ui.buttonSave.clicked.connect(self.on_save_clicked)
        self.ui.buttonCancel.clicked.connect(self.reject)
        if hasattr(self.ui, "buttonClose"):
            self.ui.buttonClose.clicked.connect(self.reject)

        # فاليديشن الحقول (من الهيلبر)
        self.attach_non_empty_validator(self.ui.lineEditCourseCode, "Course code")
        self.attach_non_empty_validator(self.ui.lineEditCourseName, "Course name")
        self.attach_non_empty_validator(self.ui.lineEditCreditHours, "Credit hours")

        # كل ما تغيّر أي حقل → نراجع إذا كلها ممتلئة
        self.ui.lineEditCourseCode.textChanged.connect(self.check_all_fields_filled)
        self.ui.lineEditCourseName.textChanged.connect(self.check_all_fields_filled)
        self.ui.lineEditCreditHours.textChanged.connect(self.check_all_fields_filled)

        # تشيك أولي
        self.check_all_fields_filled()

    # ------------------------ تفعيل/تعطيل زر الحفظ ------------------------
    def check_all_fields_filled(self):
        code = self.ui.lineEditCourseCode.text().strip()
        name = self.ui.lineEditCourseName.text().strip()
        credits = self.ui.lineEditCreditHours.text().strip()

        if code and name and credits:
            self.ui.buttonSave.setEnabled(True)
        else:
            self.ui.buttonSave.setEnabled(False)

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

        # احتياطي: الزر أصلاً ما يتفعل إلا إذا الحقول ممتلئة
        if not (code and name and credits_text):
            self.show_error("Please fill in all fields.")
            return

        # نرجع البوردر للوضع الطبيعي أولاً
        self.reset_lineedit_border(self.ui.lineEditCourseCode)
        self.reset_lineedit_border(self.ui.lineEditCourseName)
        self.reset_lineedit_border(self.ui.lineEditCreditHours)

        # ===== التحقق من الساعات =====
        # أولاً: هل هي رقم أصلاً؟ (السالب "-3" هنا مو رقم صحيح)
        if not credits_text.isdigit():
            self.highlight_invalid_lineedit(
                self.ui.lineEditCreditHours,
                "Credit hours must be a positive integer."
            )
            self.shake_widget(self.ui.lineEditCreditHours)
            self.show_error("Credit hours must be a positive integer.")
            return

        credits = int(credits_text)

        # ثانياً: هل هي أكبر من 0 ؟
        if credits <= 0:
            self.highlight_invalid_lineedit(
                self.ui.lineEditCreditHours,
                "Credit hours must be greater than 0."
            )
            self.shake_widget(self.ui.lineEditCreditHours)
            self.show_error("Credit hours must be greater than 0.")
            return

        # ===== لو وصلنا هنا فكل شيء سليم =====
        msg = self.admin_utils.add_course(code, name, credits)

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
