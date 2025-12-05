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

# واجهة عرض السكاشن (تأكد من المسار واسم الكلاس)
from app_ui.student_ui.submenus_ui.ui_view_sections import Ui_ViewSections

# منطق الطالب + الداتا بيس
from student.class_student_utilities import StudentUtilities, db


class ViewSectionsWidget(QWidget):
    """
    واجهة عرض السكاشن للمواد اللي الطالب اختارها من صفحة RegisterCourses:
    - تستقبل student_id + semester + قائمة بأكواد المواد المختارة.
    - تجيب السكاشن من الداتا بيس (لكل كورس).
    - ما تعرض السكاشن اللي الطالب مسجلها مسبقاً (حسب registrations) في نفس السمستر.
    - اختيار السكاشن عن طريق CheckBox في عمود REGISTERATION:
        * يلون الصف بالأصفر لما يتحدد.
    - تمنع تسجيل أكثر من شعبة لنفس الكورس في نفس السمستر.
    - تفحص التعارض الزمني بين السكاشن المختارة.
    - تسجّل في جدول registrations عن طريق:
        StudentUtilities.register_section(section_id, course_code, semester)
    """

    def __init__(self, student_id: int, semester: str, course_codes, parent=None):
        super().__init__(parent)

        # واجهة Qt Designer
        self.ui = Ui_ViewSections()
        self.ui.setupUi(self)

        self.student_utils = StudentUtilities(db, student_id)
        self.student_id = student_id
        self.semester = semester          # السمستر الحالي
        self.course_codes = list(course_codes)

        # list[dict]: كل سكشن معروض (غير مسجل مسبقاً)
        self.sections = []
        # row_index -> dict سكشن (نستثني الصفوف الفاصلة)
        self.row_to_section = {}
        # نستخدم None كصف فاصل بين كل مادة والثانية
        self.display_rows = []

        table = self.ui.tableSections
        table.setSelectionBehavior(table.SelectionBehavior.SelectRows)
        table.setSelectionMode(table.SelectionMode.SingleSelection)
        table.setEditTriggers(table.EditTrigger.NoEditTriggers)

        # نخلي عمود REGISTERATION واضح
        table.setColumnWidth(8, 130)

        # الضغط على أي خلية يبدّل حالة الـ CheckBox ويحدّث اللون
        table.cellClicked.connect(self.handle_cell_clicked)

        # زر التسجيل
        self.ui.buttonRegisterCourse.clicked.connect(self.handle_confirm_registration)

        # تحميل السكاشن
        self.load_sections()

    # ==================== تحميل السكاشن ====================

    def load_sections(self):
        """
        يجيب السكاشن من الداتا بيس لكل كورس في course_codes:
        - يستخدم get_sections_for_course من StudentUtilities.
        - يستثني السكاشن اللي الطالب مسجلها مسبقاً في نفس السمستر.
        """
        self.sections = []

        for code in self.course_codes:
            rows = self.student_utils.get_sections_for_course(code, self.semester)
            # rows: list of tuples من list_sections:
            # section_id, course_code, doctor_id, days, time_start, time_end,
            # room, capacity, enrolled, semester, state
            for sec in rows:
                section_id = sec[0]
                course_code = sec[1]
                doctor_id = sec[2]
                days = sec[3] or ""
                time_start = sec[4]
                time_end = sec[5]
                room = sec[6] or ""
                capacity = sec[7]
                enrolled = sec[8]
                semester = sec[9]
                state = sec[10] or ""

                # نستثني السكاشن المسجّلة مسبقاً في نفس السمستر
                try:
                    if self.student_utils.db.is_student_registered(
                        self.student_id,
                        section_id,
                        self.semester
                    ):
                        continue
                except AttributeError:
                    # لو لسبب ما ما فيه الدالة، نكمّل بدون الفلترة
                    pass

                self.sections.append({
                    "section_id": section_id,
                    "course_code": course_code,
                    "doctor_id": doctor_id,
                    "days": days,
                    "time_start": time_start,
                    "time_end": time_end,
                    "room": room,
                    "capacity": capacity,
                    "enrolled": enrolled,
                    "semester": semester,
                    "state": state,
                })

        self.fill_table()

    # ==================== تعبئة الجدول + صفوف فاصل ====================

    def fill_table(self):
        """
        يعرض السكاشن في tableSections:
        - يجمع السكاشن حسب course_code.
        - يحط صف رمادي فاصل بين كل مادة والثانية.
        - يربط الـ CheckBox مع تلوين الصف.
        """
        table = self.ui.tableSections
        table.clearContents()

        self.display_rows = []
        self.row_to_section = {}

        # ترتيب: أولاً حسب كود المادة، ثم رقم السكشن
        sorted_secs = sorted(
            self.sections,
            key=lambda s: (s["course_code"], s["section_id"])
        )

        last_code = None
        for sec in sorted_secs:
            code = sec["course_code"]
            if last_code is not None and code != last_code:
                # صف فاصل (رمادي)
                self.display_rows.append(None)
            self.display_rows.append(sec)
            last_code = code

        table.setRowCount(len(self.display_rows))

        for row, sec in enumerate(self.display_rows):
            if sec is None:
                # صف فاصل
                for col in range(table.columnCount()):
                    item = QTableWidgetItem("")
                    item.setFlags(Qt.ItemFlag.NoItemFlags)
                    item.setBackground(Qt.GlobalColor.lightGray)
                    table.setItem(row, col, item)
                continue

            self.row_to_section[row] = sec

            section_id = sec["section_id"]
            course_code = sec["course_code"]
            days = sec["days"]
            time_start = sec["time_start"]
            time_end = sec["time_end"]
            room = sec["room"]
            enrolled = sec["enrolled"]
            capacity = sec["capacity"]
            state = (sec["state"] or "").capitalize()

            # 0: #
            item_index = QTableWidgetItem(str(row + 1))
            item_index.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(row, 0, item_index)

            # 1: ID (رقم السكشن)
            item_id = QTableWidgetItem(str(section_id))
            item_id.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(row, 1, item_id)

            # 2: COURSE
            item_course = QTableWidgetItem(course_code)
            item_course.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(row, 2, item_course)

            # 3: INSTRUCTOR (فاضي حالياً)
            item_instr = QTableWidgetItem("")
            item_instr.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(row, 3, item_instr)

            # 4: SCHEDULE (days + time + room)
            schedule_str = days
            if time_start and time_end:
                schedule_str += f"  {time_start}-{time_end}"
            if room:
                schedule_str += f"  ({room})"
            item_sched = QTableWidgetItem(schedule_str.strip())
            item_sched.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(row, 4, item_sched)

            # 5: ENROLLED
            item_enrolled = QTableWidgetItem(
                "" if enrolled is None else str(enrolled)
            )
            item_enrolled.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(row, 5, item_enrolled)

            # 6: CAPACITY
            item_cap = QTableWidgetItem(
                "" if capacity is None else str(capacity)
            )
            item_cap.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(row, 6, item_cap)

            # 7: STATUS
            item_status = QTableWidgetItem(state)
            item_status.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(row, 7, item_status)

            # 8: REGISTERATION (CheckBox)
            checkbox = QCheckBox()
            checkbox.setStyleSheet(
                "QCheckBox::indicator { width: 20px; height: 20px; }"
            )

            # لما يتغير الـ CheckBox => نحدّث لون الصف
            checkbox.stateChanged.connect(
                lambda _state, r=row: self.update_row_highlight(r)
            )

            layout = QHBoxLayout()
            layout.addWidget(checkbox)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cell = QWidget()
            cell.setLayout(layout)
            table.setCellWidget(row, 8, cell)

            # لون افتراضي
            self.update_row_highlight(row)

        table.setColumnWidth(8, 130)

    # ==================== تلوين الصف حسب التحديد ====================

    def update_row_highlight(self, row: int):
        """
        يلوّن الصف بالأصفر إذا الـ CheckBox في هذا الصف محدد،
        ويرجع للون الأبيض إذا ملغي.
        """
        if row not in self.row_to_section:
            return  # صف فاصل

        table = self.ui.tableSections
        cell = table.cellWidget(row, 8)
        if not cell:
            return

        checkbox = cell.layout().itemAt(0).widget()
        checked = checkbox.isChecked()

        bg_color = Qt.GlobalColor.yellow if checked else Qt.GlobalColor.white

        for col in range(table.columnCount()):
            item = table.item(row, col)
            if item:
                item.setBackground(bg_color)

    # ==================== الضغط على الصف يقلب الـ CheckBox ====================

    def handle_cell_clicked(self, row: int, column: int):
        """
        لما تضغط أي خلية في صف حقيقي:
        - نقلب حالة الـ CheckBox في عمود REGISTERATION (8).
        """
        if row not in self.row_to_section:
            return  # صف فاصل

        table = self.ui.tableSections
        cell = table.cellWidget(row, 8)
        if not cell:
            return

        checkbox = cell.layout().itemAt(0).widget()
        checkbox.setChecked(not checkbox.isChecked())

    # ==================== السكاشن المختارة ====================

    def get_selected_sections(self):
        """
        ترجع list بالسكاشن اللي عليها صح (CheckBox).
        """
        table = self.ui.tableSections
        selected = []

        for row, sec in self.row_to_section.items():
            cell = table.cellWidget(row, 8)
            if not cell:
                continue
            checkbox = cell.layout().itemAt(0).widget()
            if checkbox.isChecked():
                selected.append(sec)

        return selected

    # ==================== التعارض + منع نفس الكورس + التسجيل ====================

    def handle_confirm_registration(self):
        """
        1) تجمع السكاشن المختارة.
        2) تمنع تسجيل أكثر من شعبة لنفس الكورس في نفس السمستر.
        3) تفحص التعارض الزمني.
        4) تسجّل في جدول registrations.
        5) تشيل الكورسات اللي تسجلت من الجدول.
        """
        selected = self.get_selected_sections()

        if not selected:
            QMessageBox.warning(self, "No Sections", "Please select at least one section.")
            return

        # منع تسجيل أكثر من شعبة لنفس الكورس في نفس السمستر
        code_counts = {}
        for sec in selected:
            code = sec["course_code"]
            code_counts[code] = code_counts.get(code, 0) + 1

        duplicates = [c for c, n in code_counts.items() if n > 1]
        if duplicates:
            msg = "لا يمكنك تسجيل أكثر من شعبة لنفس المادة في نفس السمستر:\n\n"
            msg += "\n".join(f"- {c}" for c in duplicates)
            QMessageBox.warning(self, "Invalid Selection", msg)
            return

        # فحص التعارض الزمني بين السكاشن المختارة
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

        # التسجيل الفعلي + تحديث الجدول
        self.register_selected_sections(selected)

    def register_selected_sections(self, sections):
        """
        يسجّل السكاشن في الداتا بيس باستخدام
        StudentUtilities.register_section(section_id, course_code, semester)
        ثم يشيل هذه الكورسات من self.sections ويعيد تعبئة الجدول.
        """
        success = 0
        fail = 0
        registered_codes = set()

        for sec in sections:
            section_id = sec["section_id"]
            course_code = sec["course_code"]
            ok = self.student_utils.register_section(
                section_id,
                course_code,
                self.semester
            )
            if ok:
                success += 1
                registered_codes.add(course_code)
            else:
                fail += 1

        # نشيل الكورسات اللي تسجلت من القائمة الداخلية
        if registered_codes:
            self.sections = [
                s for s in self.sections if s["course_code"] not in registered_codes
            ]
            self.fill_table()

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


# ===== تجربة سريعة من نفس الملف =====
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # عدّل القيم حسب الداتا بيس عندك
    test_student_id = 2500001
    test_semester = "First"
    selected_course_codes = ["MATH204", "CIPT", "IE204", "A", "W"]

    w = ViewSectionsWidget(test_student_id, test_semester, selected_course_codes)
    w.show()

    sys.exit(app.exec())
