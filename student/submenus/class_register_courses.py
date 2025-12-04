import sys

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QTableWidgetItem,
    QCheckBox,
    QHBoxLayout,
    QMessageBox,
)
from PyQt6.QtCore import Qt

# واجهة اختيار المواد (Qt Designer)
from app_ui.student_ui.submenus_ui.ui_register_courses import Ui_RegisterCourses

# منطق الطالب + اتصال قاعدة البيانات
from student.class_student_utilities import StudentUtilities, db


class RegisterCoursesWidget(QWidget):
    """
    واجهة اختيار المواد للتسجيل للطالب:
    - تحدد الطالب عن طريق student_id
    - تجيب برنامجه من جدول users (عن طريق StudentUtilities)
    - تجيب المواد المتاحة من خطة برنامجه (وتستثني اللي خلصها / مسجّلها / ناقصة متطلبات)
    """

    def __init__(self, student_id: int, semester: str, parent=None):
        super().__init__(parent)

        # تجهيز واجهة Qt Designer
        self.ui = Ui_RegisterCourses()
        self.ui.setupUi(self)

        # كلاس الطالب
        self.student_utils = StudentUtilities(db, student_id)
        self.semester = semester

        # نخزن المواد هنا للبحث
        self.all_courses = []

        # إعداد الجدول
        table = self.ui.tableAllCourses
        table.setSelectionBehavior(table.SelectionBehavior.SelectRows)
        table.setSelectionMode(table.SelectionMode.SingleSelection)
        table.setEditTriggers(table.EditTrigger.NoEditTriggers)

        # ربط الأزرار
        self.ui.buttonRefresh.clicked.connect(self.load_courses)
        self.ui.lineEditSearch.textChanged.connect(self.apply_search_filter)
        self.ui.buttonViewSections.clicked.connect(self.handle_view_sections)

        # أول تحميل
        self.load_courses()

    # ==================== تحميل المواد المتاحة ====================

    def load_courses(self):
        """
        يجيب المواد المتاحة من StudentUtilities حسب برنامج الطالب والسمستر
        """
        courses = self.student_utils.get_available_courses(self.semester)
        self.all_courses = courses
        self.fill_table(courses)

        if not courses:
            QMessageBox.information(
                self,
                "No Courses",
                "لا توجد مواد متاحة للتسجيل لهذا الطالب في هذا السمستر.\n"
                "تأكّد أن الطالب له برنامج (program) وأن الخطة فيها مواد."
            )

    def fill_table(self, rows):
        """
        تعبئة الجدول بالمواد المتاحة
        rows: list of dict from get_available_courses
        """
        table = self.ui.tableAllCourses
        table.setRowCount(len(rows))

        for i, course in enumerate(rows):
            code = course["course_code"]
            name = course["course_name"]
            credits = course["credits"]
            can_register = course["can_register"]

            # --- عمود الاختيار (CHECKBOX) ---
            checkbox = QCheckBox()
            checkbox.setEnabled(can_register)  # لو ناقص متطلبات ما نسمح يختارها
            checkbox.setStyleSheet("margin-left: 20px;")

            layout = QHBoxLayout()
            layout.addWidget(checkbox)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            cell = QWidget()
            cell.setLayout(layout)
            table.setCellWidget(i, 0, cell)

            # --- رقم الصف (#) ---
            index_item = QTableWidgetItem(str(i + 1))
            index_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 1, index_item)

            # --- COURSE CODE ---
            code_item = QTableWidgetItem(code)
            code_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 2, code_item)

            # --- COURSE NAME ---
            name_item = QTableWidgetItem(name)
            name_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 3, name_item)

            # --- CREDIT HOURS ---
            credits_item = QTableWidgetItem(str(credits))
            credits_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 4, credits_item)

            # --- LEVEL (حالياً ما نعرفه من StudentUtilities، نخليه "-") ---
            level_item = QTableWidgetItem("-")
            level_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 5, level_item)

            # --- ACTION (فاضي) ---
            action_item = QTableWidgetItem("")
            action_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 6, action_item)

            # لو ما يقدر يسجلها (متطلبات ناقصة) ممكن نلوّن الصف (اختياري)
            if not can_register:
                for col in range(1, 7):  # نخلي عمود الـ checkbox كما هو
                    item = table.item(i, col)
                    if item:
                        item.setBackground(Qt.GlobalColor.lightGray)

    # ==================== البحث ====================

    def apply_search_filter(self):
        """
        بحث بالكود أو الاسم
        """
        text = self.ui.lineEditSearch.text().strip().lower()

        if not text:
            self.fill_table(self.all_courses)
            return

        filtered = []
        for c in self.all_courses:
            if text in c["course_code"].lower() or text in c["course_name"].lower():
                filtered.append(c)

        self.fill_table(filtered)

    # ==================== اختيار مادة ====================

    def get_selected_course_code(self):
        """
        ترجع كود أول مادة مختارة (من الـ checkbox)
        """
        table = self.ui.tableAllCourses

        for row in range(table.rowCount()):
            cell = table.cellWidget(row, 0)
            if not cell:
                continue

        # استرجاع مادة مختارة
            checkbox = cell.layout().itemAt(0).widget()
            if checkbox.isChecked():
                code_item = table.item(row, 2)
                if code_item:
                    return code_item.text()

        return None

    # ==================== زر View Sections ====================

    def handle_view_sections(self):
        """
        حالياً: بس يطبع كود المادة المختارة (بعدين نربطها بواجهة السكاشن)
        """
        code = self.get_selected_course_code()
        if not code:
            QMessageBox.warning(self, "No Selection", "Please select one course first.")
            return

        print("SELECTED COURSE FOR SECTIONS:", code)
        QMessageBox.information(self, "DEBUG", f"Selected course: {code}")


# ==================== تشغيل الواجهة مباشرة ====================

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # غيّر هذي القيم حسب الطالب والسمستر اللي تبي تختبر عليه
    student_id = 1         # لازم يكون موجود في جدول users وله program
    semester = "2025-1"    # حسب شكل السمستر عندك

    window = RegisterCoursesWidget(student_id, semester)
    window.show()

    sys.exit(app.exec())
