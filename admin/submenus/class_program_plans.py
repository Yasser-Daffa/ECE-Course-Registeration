import os
import sys

from PyQt6.QtWidgets import (
    QWidget,
    QApplication,
    QTableWidgetItem,
    QMessageBox,
)
from PyQt6.QtCore import Qt

# نخلي البايثون يشوف مجلد المشروع الرئيسي
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# واجهة الخطة الدراسية (program_plans.ui)
from app_ui.admin_ui.submenus_ui.ui_program_plans import Ui_RegisterCourses

# كائن الأدمن الجاهز
from admin.class_admin_utilities import admin


class ProgramPlansWidget(QWidget):
    """
    شاشة عرض الخطط الدراسية:
    - تعرض كل الكورسات الموجودة في program_plans
    - فلترة حسب البرنامج (Program)
    - فلترة حسب المستوى (Level)
    - زر حذف كورس من الخطة
    - حقل البحث حالياً غير مفعّل (كما طلبت)
    """

    def __init__(self, admin_utils, parent=None):
        super().__init__(parent)
        self.ui = Ui_RegisterCourses()
        self.ui.setupUi(self)

        self.admin_utils = admin_utils

        # نخزن كل الصفوف هنا عشان نقدر نفلتر على المستوى
        # كل عنصر: (program, code, name, credits, level)
        self.all_rows = []

        # تجهيز الكومبوهات
        self.setup_programs_combo()
        self.setup_levels_combo()

        # ربط الأزرار/الكمبوبوكس
        self.ui.buttonRefresh.clicked.connect(self.load_plans)
        self.ui.comboBoxSelectProgram.currentIndexChanged.connect(self.on_program_changed)
        self.ui.comboBoxStatusFilter.currentIndexChanged.connect(self.apply_filters)

        # زر الحذف
        self.ui.buttonRemoveCourse.clicked.connect(self.on_delete_course_clicked)

        # ملاحظة: lineEditSearch ما ربطناه بأي شيء حالياً (مثل ما طلبت)
        # self.ui.lineEditSearch.textChanged.connect(self.apply_filters_by_name)

        # في البداية نحمّل كل الخطط
        self.load_plans()

    # ------------------------- إعداد الكمبوبوكس -------------------------

    def setup_programs_combo(self):
        """
        يجهّز comboBoxSelectProgram بقائمة البرامج:
        - All Programs (None)
        - PWM / BIO / COMM / COMP
        """
        cb = self.ui.comboBoxSelectProgram
        cb.clear()
        cb.addItem("All Programs", None)

        programs = [
            ("PWM",  "Power & Machines Engineering"),
            ("BIO",  "Biomedical Engineering"),
            ("COMM", "Communications Engineering"),
            ("COMP", "Computer Engineering"),
        ]

        for code, label in programs:
            text = f"{code} - {label}"
            cb.addItem(text, code)

    def setup_levels_combo(self):
        """
        يجهّز comboBoxStatusFilter بقائمة المستويات:
        - All Levels
        - Level 1 .. Level 8 (عدل الرقم لو نظامكم مختلف)
        """
        cb = self.ui.comboBoxStatusFilter
        cb.clear()
        cb.addItem("All Levels", None)

        for lvl in range(1, 9):
            cb.addItem(f"Level {lvl}", lvl)

    # ------------------------- تحميل البيانات من الداتابيس -------------------------

    def load_plans(self):
        """
        يجيب الصفوف من الداتابيس (list_plan_courses)
        حسب البرنامج المختار (إن وجد)، ويحفظها في self.all_rows
        ثم يطبق الفلاتر ويعبّي الجدول.
        """
        program_code = self.ui.comboBoxSelectProgram.currentData()  # None أو "PWM" مثلاً

        if program_code is None:
            # كل البرامج
            rows = self.admin_utils.db.list_plan_courses()
        else:
            # برنامج معيّن
            rows = self.admin_utils.db.list_plan_courses(program=program_code)

        self.all_rows = rows
        self.apply_filters()

    def on_program_changed(self):
        """
        إذا تغيّر البرنامج من الكمبوبوكس → نعيد التحميل من الداتابيس.
        """
        self.load_plans()

    # ------------------------- تطبيق الفلاتر و تعبئة الجدول -------------------------

    def apply_filters(self):
        """
        يطبّق فلتر المستوى (Level) على self.all_rows
        ثم يعبّي الجدول النهائي.
        حقل البحث غير مفعّل حالياً.
        """
        level_filter = self.ui.comboBoxStatusFilter.currentData()  # None أو رقم المستوى

        filtered = []

        for program, code, name, credits, level in self.all_rows:
            # فلتر المستوى
            if level_filter is not None and level != level_filter:
                continue

            filtered.append((program, code, name, credits, level))

        self.fill_table(filtered)

    def fill_table(self, rows):
        """
        تعبئة tableAllCourses بالصفوف المعطاة.
        كل صف: (program, code, name, credits, level)
        الأعمدة:
        0: #
        1: LEVEL
        2: COURSE CODE
        3: COURSE NAME
        4: CREDIT HOURS
        5: PREREQUISITES (مؤقتاً نعرض اسم الخطة / البرنامج)
        6: ACTION (حالياً فاضية)
        """
        table = self.ui.tableAllCourses
        table.setRowCount(len(rows))

        for i, (program, code, name, credits, level) in enumerate(rows):
            # رقم تسلسلي
            item0 = QTableWidgetItem(str(i + 1))
            item0.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 0, item0)

            # LEVEL
            item1 = QTableWidgetItem(str(level))
            item1.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 1, item1)

            # COURSE CODE
            item2 = QTableWidgetItem(code)
            item2.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 2, item2)

            # COURSE NAME
            item3 = QTableWidgetItem(name)
            item3.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 3, item3)

            # CREDIT HOURS
            item4 = QTableWidgetItem(str(credits))
            item4.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 4, item4)

            # PREREQUISITES (مؤقتاً: اسم الخطة / البرنامج)
            item5 = QTableWidgetItem(program)
            item5.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 5, item5)

            # ACTION (حالياً فاضي)
            item6 = QTableWidgetItem("")
            item6.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 6, item6)

    # ------------------------- زر الحذف -------------------------

    def on_delete_course_clicked(self):
        """
        يحذف الكورس المختار من الخطة باستخدام
        admin_delete_course_from_plan في كلاس الأدمن.
        """
        table = self.ui.tableAllCourses
        selected_row = table.currentRow()

        if selected_row < 0:
            QMessageBox.warning(self, "Delete", "Please select a course to delete.")
            return

        # الأعمدة:
        # 0: #
        # 1: LEVEL
        # 2: COURSE CODE
        # 3: COURSE NAME
        # 4: CREDIT HOURS
        # 5: PROGRAM (مؤقتاً في عمود PREREQUISITES)
        # 6: ACTION

        course_item = table.item(selected_row, 2)
        program_item = table.item(selected_row, 5)

        if course_item is None or program_item is None:
            QMessageBox.warning(self, "Delete", "Invalid selected row.")
            return

        course_code = course_item.text().strip()
        program = program_item.text().strip()

        # تأكيد
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to remove course:\n{course_code}\nfrom plan: {program}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        # استدعاء دالة الأدمن (مو الداتابيس مباشرة)
        try:
            msg = self.admin_utils.admin_delete_course_from_plan(program, course_code)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error while deleting course:\n{e}")
            return

        QMessageBox.information(self, "Deleted", msg)

        # إعادة تحميل الجدول بعد الحذف
        self.load_plans()

    # ------------------------- أزرار أخرى (مستقبلية) -------------------------

    def on_add_course_clicked(self):
        """
        مخصص لاحقاً لفتح AddCourseToPlanDialog.
        """
        pass

    def on_edit_plan_clicked(self):
        """
        مخصص لاحقاً لتعديل الخطة.
        """
        pass


# =============================== MAIN للتجربة المباشرة ===============================

if __name__ == "__main__":
    app = QApplication(sys.argv)

    w = ProgramPlansWidget(admin)
    w.show()

    sys.exit(app.exec())
