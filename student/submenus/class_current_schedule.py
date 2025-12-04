import os
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

# عشان نضمن الوصول للمجلد الرئيسي للمشروع
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app_ui.student_ui.submenus_ui.ui_current_schedule import Ui_AllStudents
from student.class_student_utilities import StudentUtilities, db


class ViewSectionsWidget(QWidget):
    """
    واجهة عرض السكاشن للمواد اللي الطالب اختارها من صفحة RegisterCourses:
    - تستقبل student_id + semester + قائمة بأكواد المواد المختارة.
    - تجيب كل السكاشن لهذه المواد من StudentUtilities.get_sections_for_courses.
    - تعرضها في جدول current_schedule (tableCourses).
    - تسمح باختيار سكاشن متعددة.
    - تفحص التعارض بين الأوقات/الأيام قبل التسجيل.
    - لو فيه تعارض -> رسالة تحذير ولا يسجل.
    - لو مافيه -> يسوي تسجيل فعلي بالـ DB.
    """

    def __init__(self, student_id: int, semester: str, course_codes, parent=None):
        super().__init__(parent)

        # واجهة Qt Designer
        self.ui = Ui_AllStudents()
        self.ui.setupUi(self)

        # نعدّل العناوين عشان توضح أنها صفحة اختيار سكاشن
        self.ui.labelTitle.setText("Available Sections")
        self.ui.tableTitle.setText("Choose Sections for Registration")

        # نستخدم زر Remove كزر تأكيد تسجيل
        self.ui.buttonRemoveSelected.setText("✅ Confirm Registration")
        self.ui.buttonRemoveSelected.setEnabled(True)
        self.ui.buttonRemoveSelected.clicked.connect(self.handle_confirm_registration)

        # منطق الطالب
        self.student_utils = StudentUtilities(db, student_id)
        self.semester = semester
        self.course_codes = course_codes  # list of course codes

        # نخزن السكاشن هنا بنفس ترتيب الجدول
        # كل عنصر dict: section_id, course_code, days, time_start, time_end, room
        self.sections = []

        # إعداد الجدول
        table = self.ui.tableCourses
        table.setSelectionBehavior(table.SelectionBehavior.SelectRows)
        table.setSelectionMode(table.SelectionMode.SingleSelection)
        table.setEditTriggers(table.EditTrigger.NoEditTriggers)

        # نخلي عمود الـ SELECT عريض من البداية
        table.setColumnWidth(0, 70)

        # لما نضغط على أي خلية في الصف، نبدّل حالة الـ checkbox
        table.cellClicked.connect(self.handle_cell_clicked)

        # تحميل السكاشن
        self.load_sections()

    # ==================== تحميل السكاشن ====================

    def load_sections(self):
        """
        يجيب كل السكاشن لكل المواد المختارة ويعرضها في الجدول.
        """
        self.sections = self.student_utils.get_sections_for_courses(
            self.course_codes,
            self.semester,
        )

        table = self.ui.tableCourses
        table.setRowCount(len(self.sections))

        for row, sec in enumerate(self.sections):
            section_id = sec["section_id"]
            course_code = sec["course_code"]
            days = sec["days"]
            time_start = sec["time_start"]
            time_end = sec["time_end"]
            room = sec["room"]

            # 0: SELECT (checkbox) — خليّناه كبير وواضح
            checkbox = QCheckBox()
            checkbox.setStyleSheet(
                "QCheckBox::indicator { width: 22px; height: 22px; }"
            )
            layout = QHBoxLayout()
            layout.addWidget(checkbox)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cell = QWidget()
            cell.setLayout(layout)
            table.setCellWidget(row, 0, cell)

            # 1: # (رقم تسلسلي)
            item_index = QTableWidgetItem(str(row + 1))
            item_index.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(row, 1, item_index)

            # 2: COURSE ID (كود المادة)
            item_course = QTableWidgetItem(course_code)
            item_course.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(row, 2, item_course)

            # 3: CREDIT (ما عندنا هنا -> نخليها "-")
            item_credits = QTableWidgetItem("-")
            item_credits.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(row, 3, item_credits)

            # 4: SECTION (رقم السكشن)
            item_section = QTableWidgetItem(str(section_id))
            item_section.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(row, 4, item_section)

            # 5: DAYS
            item_days = QTableWidgetItem(days)
            item_days.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(row, 5, item_days)

            # 6: TIME
            time_str = ""
            if time_start and time_end:
                time_str = f"{time_start} - {time_end}"
            item_time = QTableWidgetItem(time_str)
            item_time.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(row, 6, item_time)

            # 7: ROOM
            item_room = QTableWidgetItem(room)
            item_room.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(row, 7, item_room)

            # 8: INSTRUCTOR (نخليها فاضية حالياً)
            item_instr = QTableWidgetItem("")
            item_instr.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(row, 8, item_instr)

        # نتأكد بعد التعبئة إن العمود 0 واضح
        table.setColumnWidth(0, 70)

    # ==================== جعل الضغط على الصف يبدّل الـ checkbox ====================

    def handle_cell_clicked(self, row: int, column: int):
        """
        لما يضغط على أي خلية في الصف، نقلب حالة الـ checkbox في عمود SELECT (0).
        """
        table = self.ui.tableCourses
        cell = table.cellWidget(row, 0)
        if not cell:
            return

        checkbox = cell.layout().itemAt(0).widget()
        checkbox.setChecked(not checkbox.isChecked())

    # ==================== السكاشن المختارة ====================

    def get_selected_sections(self):
        """
        ترجع list بالسكاشن اللي عليها صح (checkbox)
        كل عنصر dict من self.sections.
        """
        selected = []
        table = self.ui.tableCourses

        for row in range(table.rowCount()):
            cell = table.cellWidget(row, 0)
            if not cell:
                continue

            checkbox = cell.layout().itemAt(0).widget()
            if checkbox.isChecked():
                selected.append(self.sections[row])

        return selected

    # ==================== التعارض + التسجيل ====================

    def handle_confirm_registration(self):
        """
        1) تجمع السكاشن المختارة.
        2) تفحص التعارض بينها باستخدام check_time_conflict.
        3) لو فيه تعارض -> رسالة تحذير وعدم تسجيل.
        4) لو مافيه -> تسجيل السكاشن.
        """
        selected = self.get_selected_sections()

        if not selected:
            QMessageBox.warning(self, "No Sections", "Please select at least one section.")
            return

        # فحص التعارض لو فيه أكثر من سكشن
        if len(selected) > 1:
            for i in range(len(selected)):
                for j in range(i + 1, len(selected)):
                    s1 = selected[i]
                    s2 = selected[j]
                    if self.student_utils.check_time_conflict(s1, s2):
                        msg = (
                            "لا يمكنك تسجيل هذه الشعب لأنها متعارضة في الوقت أو الأيام:\n\n"
                            f"- {s1['course_code']} (section {s1['section_id']})\n"
                            f"- {s2['course_code']} (section {s2['section_id']})\n\n"
                            "الرجاء تغيير الشعبة لأحد المادتين ثم المحاولة مرة أخرى."
                        )
                        QMessageBox.warning(self, "Time Conflict", msg)
                        return

        # لو وصلنا هنا: مافيه تعارض -> نسجل
        self.register_selected_sections(selected)

    def register_selected_sections(self, sections):
        """
        تسجيل السكاشن المختارة فعلياً في قاعدة البيانات.
        """
        success = 0
        fail = 0

        for sec in sections:
            section_id = sec["section_id"]
            ok = self.student_utils.register_section(section_id)
            if ok:
                success += 1
            else:
                fail += 1

        if success and not fail:
            QMessageBox.information(self, "Registration", "تم تسجيل جميع الشعب بنجاح.")
        elif success and fail:
            QMessageBox.warning(
                self,
                "Registration",
                f"تم تسجيل {success} شعبة، وفشل تسجيل {fail} شعبة.",
            )
        else:
            QMessageBox.critical(
                self,
                "Registration",
                "فشل تسجيل جميع الشعب. تأكد من إعدادات قاعدة البيانات.",
            )


# ===== للتجربة المباشرة =====
if __name__ == "__main__":
    app = QApplication(sys.argv)

    test_student_id = 2500001
    test_semester = "First"
    selected_course_codes = ["SALEM", "SS","EE345"]  # عدّلها حسب موادك الحقيقية

    w = ViewSectionsWidget(test_student_id, test_semester, selected_course_codes)
    w.show()

    sys.exit(app.exec())
