import os
import sys

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QTableWidgetItem,
    QCheckBox,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt

# عشان نضمن الوصول للمجلد الرئيسي للمشروع
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# واجهة عرض السكاشن (تأكد من المسار واسم الكلاس)
from app_ui.student_ui.submenus_ui.ui_view_sections import Ui_ViewSections

# منطق الطالب + الداتا بيس
from student.class_student_utilities import StudentUtilities, db

# استبدال QMessageBox بـ info, warning, error
from helper_files.shared_utilities import info, warning, error


class ViewSectionsWidget(QWidget):
    """
    واجهة عرض السكاشن للمواد اللي الطالب اختارها من صفحة RegisterCourses:
    - تستقبل student_id + semester + قائمة بأكواد المواد المختارة.
    - تجيب السكاشن من الداتا بيس (لكل كورس).
    - ما تعرض السكاشن اللي الطالب مسجلها مسبقاً (حسب registrations).
    - اختيار السكاشن عن طريق CheckBox في عمود REGISTERATION:
        * يلون الصف بالأصفر لما يتحدد.
    - تمنع تسجيل أكثر من شعبة لنفس الكورس.
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
        self.semester = semester          # فقط تستخدم كفلتر أولي في get_sections_for_course (إذا احتجته)
        self.course_codes = list(course_codes)

        # list[dict]: كل سكشن معروض (غير مسجل مسبقاً)
        self.sections = []
        # row_index -> dict سكشن (نستثني الصفوف الفاصلة)
        self.row_to_section = {}
        # نستخدم None كصف فاصل بين كل مادة والثانية
        self.display_rows = []

        table = self.ui.tableSections
        table.setSelectionBehavior(table.SelectionBehavior.SelectRows)
        table.setSelectionMode(table.SelectionMode.ExtendedSelection)
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
        - يستثني السكاشن اللي الطالب مسجلها مسبقاً في نفس سمستر الشعبة نفسها.
        """
        self.sections = []

        for code in self.course_codes:
            rows = self.student_utils.get_sections_for_course(code, self.semester)

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
                semester = sec[9]      # سمستر الشعبة نفسها
                state = sec[10] or ""

                # نستثني السكاشن المسجّلة مسبقاً في نفس سمستر الشعبة
                try:
                    if self.student_utils.db.is_student_registered(
                        self.student_id,
                        section_id,
                        semester
                    ):
                        continue
                except AttributeError:
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
        table = self.ui.tableSections
        table.clearContents()

        self.display_rows = []
        self.row_to_section = {}

        sorted_secs = sorted(
            self.sections,
            key=lambda s: (s["course_code"], s["section_id"])
        )

        last_code = None
        for sec in sorted_secs:
            code = sec["course_code"]
            if last_code is not None and code != last_code:
                self.display_rows.append(None)
            self.display_rows.append(sec)
            last_code = code

        table.setRowCount(len(self.display_rows))

        for row, sec in enumerate(self.display_rows):
            if sec is None:
                for col in range(table.columnCount()):
                    item = QTableWidgetItem("")
                    item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
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

            item_index = QTableWidgetItem(str(row + 1))
            item_index.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            table.setItem(row, 0, item_index)

            item_id = QTableWidgetItem(str(section_id))
            item_id.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            table.setItem(row, 1, item_id)

            item_course = QTableWidgetItem(course_code)
            item_course.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            table.setItem(row, 2, item_course)

            item_instr = QTableWidgetItem("")
            item_instr.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            table.setItem(row, 3, item_instr)

            schedule_str = days
            if time_start and time_end:
                schedule_str += f"  {time_start}-{time_end}"
            if room:
                schedule_str += f"  ({room})"
            item_sched = QTableWidgetItem(schedule_str.strip())
            item_sched.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            table.setItem(row, 4, item_sched)

            item_enrolled = QTableWidgetItem("" if enrolled is None else str(enrolled))
            item_enrolled.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            table.setItem(row, 5, item_enrolled)

            item_cap = QTableWidgetItem("" if capacity is None else str(capacity))
            item_cap.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            table.setItem(row, 6, item_cap)

            item_status = QTableWidgetItem(state)
            item_status.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            table.setItem(row, 7, item_status)

            checkbox = QCheckBox()
            checkbox.setStyleSheet("QCheckBox::indicator { width: 20px; height: 20px; }")
            checkbox.stateChanged.connect(lambda _state, r=row: self.update_row_highlight(r))

            layout = QHBoxLayout()
            layout.addWidget(checkbox)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cell = QWidget()
            cell.setLayout(layout)
            table.setCellWidget(row, 8, cell)

            self.update_row_highlight(row)

        table.setColumnWidth(8, 130)

    # ==================== تلوين الصف ====================

    def update_row_highlight(self, row: int):
        if row not in self.row_to_section:
            return

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

    # ==================== الضغط على صف ====================

    def handle_cell_clicked(self, row: int, column: int):
        if row not in self.row_to_section:
            return

        table = self.ui.tableSections
        cell = table.cellWidget(row, 8)
        if not cell:
            return

        checkbox = cell.layout().itemAt(0).widget()
        checkbox.setChecked(not checkbox.isChecked())

    # ==================== السكاشن المختارة ====================

    def get_selected_sections(self):
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

    # ==================== التعارض + التسجيل ====================

    def handle_confirm_registration(self):
        selected = self.get_selected_sections()

        if not selected:
            warning(self, "Please select at least one section.")
            return

        code_counts = {}
        for sec in selected:
            code = sec["course_code"]
            code_counts[code] = code_counts.get(code, 0) + 1

        duplicates = [c for c, n in code_counts.items() if n > 1]
        if duplicates:
            msg = "لا يمكنك تسجيل أكثر من شعبة لنفس المادة:\n\n"
            msg += "\n".join(f"- {c}" for c in duplicates)
            warning(self, msg)
            return

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
                        warning(self, msg)
                        return

        self.register_selected_sections(selected)

    def register_selected_sections(self, sections):
        success = 0
        fail = 0
        registered_codes = set()

        for sec in sections:
            section_id = sec["section_id"]
            course_code = sec["course_code"]
            semester = sec["semester"]

            ok = self.student_utils.register_section(section_id, course_code, semester)

            try:
                really_registered = self.student_utils.db.is_student_registered(
                    self.student_utils.student_id,
                    section_id,
                    semester
                )
            except Exception:
                really_registered = False

            if ok and really_registered:
                success += 1
                registered_codes.add(course_code)
            else:
                fail += 1

        if registered_codes:
            self.sections = [
                s for s in self.sections
                if s["course_code"] not in registered_codes
            ]
            self.fill_table()

        if success and not fail:
            info(self, "All sections have been registered successfully.")
        elif success and fail:
            warning(self, f"Registered {success} sections successfully, and {fail} failed.")
        else:
            error(self, "Failed to register all sections. Make sure there are no time conflicts.")


# ===== تجربة سريعة =====
if __name__ == "__main__":
    app = QApplication(sys.argv)

    test_student_id = 2500001
    test_semester = "First"
    selected_course_codes = ["MATH204", "CIPT", "IE204", "A", "W"]

    w = ViewSectionsWidget(test_student_id, test_semester, selected_course_codes)
    w.show()

    sys.exit(app.exec())
