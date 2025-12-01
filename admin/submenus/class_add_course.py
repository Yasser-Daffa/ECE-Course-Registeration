import sys
from PyQt6.QtWidgets import QWidget, QMessageBox
# تأكد من استيراد الملفات الصحيحة حسب أسماء ملفاتك
from app_ui.admin_ui.submenus_ui.ui_add_courses_dialog import Ui_AddCourseDialog
from helper_files.shared_utilities import BaseLoginForm  # استيراد الكلاس المساعد
from admin.class_admin_utilities import admin_


class AddCourseController(BaseLoginForm, Ui_AddCourseDialog):
    def __init__(self, db_instance):
        # نستدعي BaseLoginForm لأنه هو الـ QWidget الأساسي هنا
        super().__init__()
        self.setupUi(self)
        self.db = db_instance

        # 1. إخفاء الزر الدخيل (الرابع)
        self.pushButton.hide()

        # 2. ربط أزرار الإغلاق
        self.buttonClose.clicked.connect(self.close)
        self.buttonCancel.clicked.connect(self.close)

        # 3. ربط زر الحفظ
        self.buttonSave.clicked.connect(self.submit_course)

        # 4. إعادة تعيين الستايل (إزالة اللون الأحمر) بمجرد الكتابة
        # نستخدم دالة reset_lineedit_border الموجودة في الهيلبر
        self.lineEditCourseCode.textChanged.connect(
            lambda: self.reset_lineedit_border(self.lineEditCourseCode))
        self.lineEditCourseName.textChanged.connect(
            lambda: self.reset_lineedit_border(self.lineEditCourseName))
        self.lineEditCreditHours.textChanged.connect(
            lambda: self.reset_lineedit_border(self.lineEditCreditHours))

    def submit_course(self):
        """تجميع البيانات، التحقق منها، ثم إرسالها لقاعدة البيانات"""

        # جلب البيانات
        code = self.lineEditCourseCode.text().strip()
        name = self.lineEditCourseName.text().strip()
        credits_text = self.lineEditCreditHours.text().strip()

        # متغير لتتبع حالة الخطأ
        has_error = False

        # --- التحقق من الحقول الفارغة باستخدام دوال الهيلبر ---
        if not code:
            self.highlight_invalid_lineedit(self.lineEditCourseCode, "Course Code cannot be empty")
            self.shake_widget(self.lineEditCourseCode)
            has_error = True

        if not name:
            self.highlight_invalid_lineedit(self.lineEditCourseName, "Course Name cannot be empty")
            self.shake_widget(self.lineEditCourseName)
            has_error = True

        if not credits_text:
            self.highlight_invalid_lineedit(self.lineEditCreditHours, "Credits cannot be empty")
            self.shake_widget(self.lineEditCreditHours)
            has_error = True

        if has_error:
            return

        # --- التحقق من أن الساعات رقم وصحيح (غير سالب) ---
        try:
            credits_int = int(credits_text)

            # الشرط المطلوب: لا يكون أقل من صفر
            if credits_int < 0:
                self.highlight_invalid_lineedit(self.lineEditCreditHours, "Credit hours cannot be negative (< 0)")
                self.shake_widget(self.lineEditCreditHours)
                return

        except ValueError:
            # إذا أدخل المستخدم نصاً بدلاً من رقم
            self.highlight_invalid_lineedit(self.lineEditCreditHours, "Credit hours must be a number")
            self.shake_widget(self.lineEditCreditHours)
            return

        # --- الإرسال إلى قاعدة البيانات ---
        result = self.db.AddCourse(code, name, credits_int)

        # التعامل مع النتائج
        if result == "Course added successfully":
            QMessageBox.information(self, "Success", "Course added successfully! ✅")
            self.close()  # إغلاق النافذة بعد النجاح

        elif result == "course already added":
            # هنا نستخدم دوال الهيلبر كما طلبت عند التكرار
            # 1. إظهار حدود حمراء ورسالة (Tooltip)
            self.highlight_invalid_lineedit(self.lineEditCourseCode, "This Course Code already exists in the database!")
            # 2. اهتزاز الحقل
            self.shake_widget(self.lineEditCourseCode)

        else:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {result}")


# --- جزء لتجربة الكود (Main) ---
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sqlite3


    # 1. محاكاة كلاس الداتابيس (للتجربة السريعة بدون ملف الداتابيس الكامل)

    def add_course(self, code, name, credits):
        print(f"Trying to add: {code}, {name}, {credits}")
        if code == "CS101":  # محاكاة أن المادة مكررة
            return "course already added"
        return "Course added successfully"


    # 2. تشغيل التطبيق
    app = QApplication(sys.argv)

    # هنا نمرر الداتابيس الوهمية، في مشروعك مرر الداتابيس الحقيقية
    # db = DatabaseUtilities(con, cur)
    mock_db = DatabaseUtilities()

    window = AddCourseController(mock_db)
    window.show()
    sys.exit(app.exec())