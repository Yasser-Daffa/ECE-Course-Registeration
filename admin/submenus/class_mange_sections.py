import os
import sys

from PyQt6.QtWidgets import (
    QWidget,
    QApplication,
    QTableWidgetItem,
    QMessageBox,
)
from PyQt6.QtCore import Qt

# عشان نقدر نشوف المجلد الرئيسي
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# واجهة المانج سكاشن اللي صدّرتها من Qt Designer
from app_ui.admin_ui.submenus_ui.ui_manage_sections import Ui_ManageSections

# كائن الأدمن الجاهز
from admin.class_admin_utilities import admin


class ManageSectionsWidget(QWidget):
    """
    شاشة إدارة السكاشن (مبسّطة):
    - عرض كل السكاشن في جدول
    - بحث وفلترة
    - حذف سكاشن محددة (عن طريق SELECT)
    - زر Add Section حالياً بس رسالة بسيطة
    """

    def __init__(self, admin_utils, parent=None):
        super().__init__(parent)
        self.ui = Ui_ManageSections()
        self.ui.setupUi(self)

        self.admin_utils = admin_utils

        # نخزن كل السكاشن هنا (list of dicts) عشان الفلترة والبحث
        self._all_rows_cache = []

        # ربط الأزرار
        self.ui.buttonRefresh.clicked.connect(self.refresh_sections)
        self.ui.buttonRemoveSelected.clicked.connect(self.on_remove_selected_clicked)
        self.ui.buttonAddSection.clicked.connect(self.on_add_section_clicked)

        self.ui.lineEditSearch.textChanged.connect(self.apply_filters)
        self.ui.comboBoxFilterCourses.currentIndexChanged.connect(self.apply_filters)
        self.ui.comboBoxStatusFilter.currentIndexChanged.connect(self.apply_filters)

        # نضبط الجدول شوية
        self.setup_table_appearance()

        # أول تحميل
        self.refresh_sections()

    # ------------------------ شكل الجدول ------------------------

    def setup_table_appearance(self):
        table = self.ui.tableSections
        header = table.horizontalHeader()
        header.setStretchLastSection(True)

        # نخلي أول عمود حق الـ SELECT عريض شوي عشان يبان الصح
        header.resizeSection(0, 70)

    # ------------------------ رسائل منبثقة ------------------------

    def show_error(self, message: str):
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Critical)
        box.setWindowTitle("Error")
        box.setText(message)
        box.setStandardButtons(QMessageBox.StandardButton.Ok)
        box.exec()

    def show_info(self, message: str):
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Information)
        box.setWindowTitle("Info")
        box.setText(message)
        box.setStandardButtons(QMessageBox.StandardButton.Ok)
        box.exec()

    # ------------------------ جلب البيانات من الداتا بيس ------------------------

    def refresh_sections(self):
        """
        يستدعي admin_list_sections بدون فلاتر
        ويعبي الكاش + الجدول
        """
        result = self.admin_utils.admin_list_sections()  # course_code=None, semester=None

        if isinstance(result, str):
            # مثال: "No sections found."
            self._all_rows_cache = []
            self.ui.tableSections.setRowCount(0)
            self.update_stats([])
            return

        # نتوقع result list of tuples:
        # (section_id, course_code, doctor_id, days, time_start, time_end,
        #  room, capacity, enrolled, semester, state)

        rows = []
        for (
            section_id,
            course_code,
            doctor_id,
            days,
            time_start,
            time_end,
            room,
            capacity,
            enrolled,
            semester,
            state,
        ) in result:
            rows.append(
                {
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
                }
            )

        self._all_rows_cache = rows
        self.update_stats(self._all_rows_cache)
        self.apply_filters()  # يفلتر ويعبي الجدول حسب الفلاتر الحالية

    # ------------------------ كروت الإحصائيات فوق ------------------------

    def update_stats(self, rows):
        total = len(rows)
        open_count = 0
        full_count = 0
        closed_count = 0

        for r in rows:
            state = (r["state"] or "").lower()
            enrolled = r["enrolled"] or 0
            capacity = r["capacity"] or 0

            if state == "closed":
                closed_count += 1
            elif enrolled >= capacity and capacity > 0:
                full_count += 1
            else:
                open_count += 1

        self.ui.labelTotalSectionsCount.setText(str(total))
        self.ui.labelOpenSectionsCount.setText(str(open_count))
        self.ui.labelFullSectionsCount.setText(str(full_count))
        self.ui.labelClosedSectionsCount.setText(str(closed_count))

    # ------------------------ الفلترة + البحث ------------------------

    def apply_filters(self):
        """
        يفلتر _all_rows_cache حسب:
        - البحث بـ ID من lineEditSearch
        - course من comboBoxFilterCourses
        - status من comboBoxStatusFilter
        """
        search_text = self.ui.lineEditSearch.text().strip().lower()
        course_filter = self.ui.comboBoxFilterCourses.currentText().strip()
        status_filter = self.ui.comboBoxStatusFilter.currentText().strip()

        filtered = []

        for r in self._all_rows_cache:
            # فلتر البحث بالـ ID
            if search_text:
                if search_text not in str(r["section_id"]).lower():
                    continue

            # فلتر الكورس
            if course_filter and course_filter != "All Courses":
                # مثلاً "ECE 101" بينما الكود "ECE101"
                prefix = course_filter.replace(" ", "")
                if not str(r["course_code"]).replace(" ", "").startswith(prefix):
                    continue

            # فلتر الحالة
            if status_filter and status_filter != "All Status":
                if (r["state"] or "").lower() != status_filter.lower():
                    continue

            filtered.append(r)

        self.fill_table(filtered)

    # ------------------------ تعبئة الجدول ------------------------

    def fill_table(self, rows):
        table = self.ui.tableSections
        table.setRowCount(len(rows))

        for row_idx, r in enumerate(rows):
            section_id = r["section_id"]
            course_code = r["course_code"]
            doctor_id = r["doctor_id"]
            days = r["days"]
            time_start = r["time_start"]
            time_end = r["time_end"]
            room = r["room"]
            capacity = r["capacity"]
            enrolled = r["enrolled"]
            semester = r["semester"]
            state = r["state"]

            # 0) SELECT checkbox عن طريق الـ item نفسه
            chk_item = QTableWidgetItem()
            chk_item.setFlags(
                Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsUserCheckable
                | Qt.ItemFlag.ItemIsSelectable
            )
            chk_item.setCheckState(Qt.CheckState.Unchecked)
            chk_item.setText("")  # نخليه فاضي، نستخدمه بس كصح/بدون صح
            table.setItem(row_idx, 0, chk_item)

            # 1) Row number #
            item_num = QTableWidgetItem(str(row_idx + 1))
            item_num.setFlags(item_num.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_num.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row_idx, 1, item_num)

            # 2) ID (section_id)
            item_id = QTableWidgetItem(str(section_id))
            item_id.setFlags(item_id.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row_idx, 2, item_id)

            # 3) COURSE
            item_course = QTableWidgetItem(str(course_code))
            item_course.setFlags(item_course.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(row_idx, 3, item_course)

            # 4) INSTRUCTOR (نحط الـ doctor_id كبداية)
            item_inst = QTableWidgetItem(str(doctor_id) if doctor_id is not None else "-")
            item_inst.setFlags(item_inst.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(row_idx, 4, item_inst)

            # 5) SCHEDULE (نجمع الأيام + الوقت + الغرفة + الترم)
            schedule_text = f"{days or ''} {time_start or ''}-{time_end or ''}"
            if room:
                schedule_text += f" | Room {room}"
            if semester:
                schedule_text += f" | {semester}"

            item_sched = QTableWidgetItem(schedule_text.strip())
            item_sched.setFlags(item_sched.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(row_idx, 5, item_sched)

            # 6) ENROLLED
            item_enrolled = QTableWidgetItem(str(enrolled))
            item_enrolled.setFlags(item_enrolled.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_enrolled.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row_idx, 6, item_enrolled)

            # 7) CAPACITY
            item_cap = QTableWidgetItem(str(capacity))
            item_cap.setFlags(item_cap.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_cap.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row_idx, 7, item_cap)

            # 8) STATUS
            nice_state = (state or "").capitalize()  # open -> Open
            item_state = QTableWidgetItem(nice_state)
            item_state.setFlags(item_state.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_state.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row_idx, 8, item_state)

            # 9) ACTIONS - حالياً فاضي (مافي Edit)
            item_action = QTableWidgetItem("")
            item_action.setFlags(item_action.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(row_idx, 9, item_action)

    # ------------------------ حذف السكاشن المحددة ------------------------

    def on_remove_selected_clicked(self):
        table = self.ui.tableSections
        rows_to_delete = []

        for row in range(table.rowCount()):
            item_select = table.item(row, 0)  # عمود SELECT
            if not item_select:
                continue

            if item_select.checkState() == Qt.CheckState.Checked:
                item_id = table.item(row, 2)  # عمود ID
                if item_id:
                    try:
                        sid = int(item_id.text().strip())
                        rows_to_delete.append(sid)
                    except ValueError:
                        continue

        if not rows_to_delete:
            self.show_info("No sections selected for deletion.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm",
            f"Are you sure you want to delete {len(rows_to_delete)} section(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        for sid in rows_to_delete:
            msg = self.admin_utils.admin_delete_section(sid)
            # تقدر تطبع msg لو حاب تتأكد:
            # print(msg)

        self.refresh_sections()

    # ------------------------ زر Add Section (حاليا مجرد رسالة) ------------------------

    def on_add_section_clicked(self):
        # تقدر لاحقاً تربطه بدايالوج إضافة سكشن جديد
        self.show_info("Add Section dialog is not implemented yet.")


# =============================== MAIN للتجربة ===============================

if __name__ == "__main__":
    app = QApplication(sys.argv)

    w = ManageSectionsWidget(admin)
    w.show()

    sys.exit(app.exec())
