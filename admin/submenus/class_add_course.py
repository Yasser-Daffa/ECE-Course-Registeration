import sys
from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox

# واجهة إضافة الكورس (مولدة من Qt Designer)
from app_ui.admin_ui.submenus_ui.ui_add_courses_dialog import Ui_AddCourseDialog

# كلاس الأدوات المشتركة اللي فيه الهز + اللون الأحمر + الفاليديشن
from helper_files.shared_utilities import BaseLoginForm

# نستعمل الكائن الجاهز admin اللي في class_admin_utilities
# هذا الكائن مربوط مسبقاً بـ DatabaseUtilities و initialize_database
from admin.class_admin_utilities import admin   # انتبه: هنا نجيب الـ instance الجاهز, مو الكلاس فقط


class AddCourseDialog(QDialog, BaseLoginForm):
    """
    Dialog مسؤول عن:
    - قراءة الحقول من واجهة Ui_AddCourseDialog
    - التحقق من المدخلات (فاضي/رقم/الخ)
    - استخدام الاهتزاز + إطار أحمر للحقول الغلط
    - استدعاء admin.add_course وإظهار النتيجة
    """

    def __init__(self, admin_utils, parent=None):
        QDialog.__init__(self, parent)
        BaseLoginForm.__init__(self, parent)

        self.ui = Ui_AddCourseDialog()
        self.ui.setupUi(self)

        # نخزن كائن الأدمن (AdminUtilities)
        self.admin_utils = admin_utils

        # ربط الأزرار
        self.ui.buttonSave.clicked.connect(self.on_save_clicked)
        self.ui.buttonCancel.clicked.connect(self.reject)
        # لو ما عندك buttonClose احذف السطر اللي تحت
        if hasattr(self.ui, "buttonClose"):
            self.ui.buttonClose.clicked.connect(self.reject)

        # نفعّل فاليديشن "غير فارغ" على الحقول الثلاثة
        # (هذه تستخدم attach_non_empty_validator من BaseLoginForm)
        self.attach_non_empty_validator(self.ui.lineEditCourseCode, "Course code")
        self.attach_non_empty_validator(self.ui.lineEditCourseName, "Course name")
        self.attach_non_empty_validator(self.ui.lineEditCreditHours, "Credit hours")

    # ------------------------ دوال مساعدة UI ------------------------

    def show_error(self, message: str):
        """عرض رسالة خطأ كلاسيك."""
        QMessageBox.critical(self, "Error", message)

    def show_info(self, message: str):
        """عرض رسالة نجاح."""
        QMessageBox.information(self, "Success", message)

    # ------------------------ حدث زر الحفظ ------------------------

    def on_save_clicked(self):
        # نقرأ القيم من الواجهة
        code = self.ui.lineEditCourseCode.text().strip().upper()
        name = self.ui.lineEditCourseName.text().strip()
        credits_text = self.ui.lineEditCreditHours.text().strip()

        has_error = False

        # ===== التحقق من كود الكورس =====
        if code == "":
            self.highlight_invalid_lineedit(self.ui.lineEditCourseCode, "Course code cannot be empty.")
            self.shake_widget(self.ui.lineEditCourseCode)
            has_error = True
        else:
            self.reset_lineedit_border(self.ui.lineEditCourseCode)

        # ===== التحقق من اسم الكورس =====
        if name == "":
            self.highlight_invalid_lineedit(self.ui.lineEditCourseName, "Course name cannot be empty.")
            self.shake_widget(self.ui.lineEditCourseName)
            has_error = True
        else:
            self.reset_lineedit_border(self.ui.lineEditCourseName)

        # ===== التحقق من عدد الساعات =====
        if credits_text == "":
            self.highlight_invalid_lineedit(self.ui.lineEditCreditHours, "Credit hours cannot be empty.")
            self.shake_widget(self.ui.lineEditCreditHours)
            has_error = True
        else:
            if not credits_text.isdigit():
                self.highlight_invalid_lineedit(
                    self.ui.lineEditCreditHours,
                    "Credit hours must be a positive integer.",
                )
                self.shake_widget(self.ui.lineEditCreditHours)
                has_error = True
            else:
                credits = int(credits_text)
                if credits <= 0:
                    self.highlight_invalid_lineedit(
                        self.ui.lineEditCreditHours,
                        "Credit hours must be greater than 0.",
                    )
                    self.shake_widget(self.ui.lineEditCreditHours)
                    has_error = True
                else:
                    self.reset_lineedit_border(self.ui.lineEditCreditHours)

        # لو فيه أي خطأ في المدخلات نوقف هنا
        if has_error:
            self.show_error("Please fix the highlighted fields.")
            return

        # ===== استدعاء دالة الأدمن add_course =====
        msg = self.admin_utils.add_course(code, name, int(credits_text))

        # لو الرسالة تفيد إن الكورس مضاف من قبل
        if msg.lower().startswith("course already"):
            self.highlight_invalid_lineedit(self.ui.lineEditCourseCode, msg)
            self.shake_widget(self.ui.lineEditCourseCode)
            self.show_error(msg)
            return

        # نجاح
        self.show_info(msg)
        self.accept()


# =============================== MAIN ===============================

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # نمرر الكائن الجاهز admin (من class_admin_utilities)
    dialog = AddCourseDialog(admin)
    dialog.show()

    sys.exit(app.exec())
