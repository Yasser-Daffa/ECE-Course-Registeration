import os
import sys

from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QMessageBox,
)

# نحط مسار المشروع الكامل
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# واجهة إضافة السكشن (من Qt Designer)
from app_ui.admin_ui.submenus_ui.ui_add_sections_dialog import Ui_AddSectionDialog

# كلاس الأدوات المشتركة (الهز + تلوين الحقول + الفاليديشن)
from helper_files.shared_utilities import BaseLoginForm

# كائن الأدمن الجاهز
from admin.class_admin_utilities import admin


class AddSectionDialog(QDialog, BaseLoginForm):
    """
    Dialog مسؤول عن:
    - قراءة الحقول من واجهة Add Section
    - التحقق من المدخلات الأساسية
    - استدعاء دالة add_section في الداتا بيس
    """

    def __init__(self, admin_utils, parent=None):
        QDialog.__init__(self, parent)
        BaseLoginForm.__init__(self, parent)

        self.ui = Ui_AddSectionDialog()
        self.ui.setupUi(self)

        self.admin_utils = admin_utils     # هذا هو كائن admin الجاهز

        # نجهز الكومبو بوكس حق المواد من جدول courses
        self.populate_courses_combo()

        # مبدئياً: زر الإضافة يكون مقفول
        self.ui.buttonAdd.setEnabled(False)

        # ربط الأزرار
        self.ui.buttonAdd.clicked.connect(self.on_add_clicked)
        self.ui.buttonCancel.clicked.connect(self.reject)

        # فاليديشن للحقول النصية المهمة
        self.attach_non_empty_validator(self.ui.lineEditBuilding, "Building")
        self.attach_non_empty_validator(self.ui.lineEditRoom, "Room")

        # كل ما تغيّر شيء من دول نعيد فحص تفعيل الزر
        self.ui.comboBoxSelectCourse.currentIndexChanged.connect(self.check_all_fields_filled)
        self.ui.comboBoxSelectTerm.currentIndexChanged.connect(self.check_all_fields_filled)
        self.ui.comboBoxSelectStatus.currentIndexChanged.connect(self.check_all_fields_filled)
        self.ui.lineEditBuilding.textChanged.connect(self.check_all_fields_filled)
        self.ui.lineEditRoom.textChanged.connect(self.check_all_fields_filled)
        self.ui.spinBoxCapacity.valueChanged.connect(self.check_all_fields_filled)

        # تشيك أولي
        self.check_all_fields_filled()

    # ------------------------ تعبئة كومبو المواد ------------------------

    def populate_courses_combo(self):
        """
        يجيب المواد من جدول courses (ListCourses)
        ويحطها في comboBoxSelectCourse
        """
        self.ui.comboBoxSelectCourse.clear()
        self.ui.comboBoxSelectCourse.addItem("Select a course.", None)

        # نستخدم الداتا بيس من داخل الأدمن
        rows = self.admin_utils.db.ListCourses()  # (code, name, credits)

        for code, name, credits in rows:
            display = f"{code} - {name}"
            self.ui.comboBoxSelectCourse.addItem(display, code)

    # ------------------------ تفعيل/تعطيل زر الإضافة ------------------------

    def check_all_fields_filled(self):
        """
        يفعّل/يعطّل زر Add بناء على الحقول الأساسية:
        - Course مختار
        - Term مختار
        - Status مختار
        - Building / Room
        - Capacity > 0
        """
        course_ok = self.ui.comboBoxSelectCourse.currentIndex() > 0
        term_ok = self.ui.comboBoxSelectTerm.currentIndex() > 0
        status_ok = self.ui.comboBoxSelectStatus.currentIndex() > 0

        building = self.ui.lineEditBuilding.text().strip()
        room = self.ui.lineEditRoom.text().strip()
        capacity_ok = self.ui.spinBoxCapacity.value() > 0

        if course_ok and term_ok and status_ok and building and room and capacity_ok:
            self.ui.buttonAdd.setEnabled(True)
        else:
            self.ui.buttonAdd.setEnabled(False)

    # ------------------------ رسائل منبثقة بخط أسود ------------------------

    def show_error(self, message: str):
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Critical)
        box.setWindowTitle("Error")
        box.setText(message)
        box.setStandardButtons(QMessageBox.StandardButton.Ok)
        box.setStyleSheet(
            """
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
            """
        )
        box.exec()

    def show_info(self, message: str):
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Information)
        box.setWindowTitle("Success")
        box.setText(message)
        box.setStandardButtons(QMessageBox.StandardButton.Ok)
        box.setStyleSheet(
            """
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
            """
        )
        box.exec()

    # ------------------------ أداة مساعدة: أيام الاسبوع ------------------------

    def get_selected_days(self) -> str:
        """
        يرجّع الأيام المختارة كـ string مثل: 'SUN,MON,WED'
        """
        days = []
        buttons = [
            self.ui.pushButtonDaySun,
            self.ui.pushButtonDayMon,
            self.ui.pushButtonDayTue,
            self.ui.pushButtonDayWed,
            self.ui.pushButtonDayThu,
        ]
        for btn in buttons:
            if btn.isChecked():
                days.append(btn.text().strip())

        return ",".join(days)

    # ------------------------ حدث زر الإضافة ------------------------

    def on_add_clicked(self):
        """
        يقرأ كل الحقول ويستدعي db.add_section عن طريق admin_utils.db
        """
        # ---- الكورس ----
        course_index = self.ui.comboBoxSelectCourse.currentIndex()
        course_code = self.ui.comboBoxSelectCourse.currentData()

        if course_index <= 0 or not course_code:
            self.show_error("Please select a course.")
            return

        # ---- الترم (السمستر) ----
        term_index = self.ui.comboBoxSelectTerm.currentIndex()
        if term_index <= 0:
            self.show_error("Please select a semester.")
            return
        semester = self.ui.comboBoxSelectTerm.currentText().strip()

        # ---- الحالة (state) ----
        status_index = self.ui.comboBoxSelectStatus.currentIndex()
        if status_index <= 0:
            self.show_error("Please select section status.")
            return
        state = self.ui.comboBoxSelectStatus.currentText().strip().lower()

        # ---- المبنى والغرفة ----
        building = self.ui.lineEditBuilding.text().strip().upper()
        room = self.ui.lineEditRoom.text().strip().upper()

        # نرجّع البوردر للوضع الطبيعي
        self.reset_lineedit_border(self.ui.lineEditBuilding)
        self.reset_lineedit_border(self.ui.lineEditRoom)

        if not building:
            self.highlight_invalid_lineedit(self.ui.lineEditBuilding, "Building is required.")
            self.shake_widget(self.ui.lineEditBuilding)
            self.show_error("Please enter building.")
            return

        if not room:
            self.highlight_invalid_lineedit(self.ui.lineEditRoom, "Room is required.")
            self.shake_widget(self.ui.lineEditRoom)
            self.show_error("Please enter room.")
            return

        # ممكن نخزنهم بهذا الشكل مثلاً: B40-A170 أو بس B40A170
        full_room = f"{building}{room}"

        # ---- السعة ----
        capacity = self.ui.spinBoxCapacity.value()
        if capacity <= 0:
            self.show_error("Capacity must be greater than 0.")
            return

        # ---- الأيام ----
        days = self.get_selected_days()
        if not days:
            self.show_error("Please select at least one day.")
            return

        # ---- الوقت ----
        start_qtime = self.ui.timeEditFrom.time()
        end_qtime = self.ui.timeEditTo.time()

        time_start = start_qtime.toString("HH:mm")
        time_end = end_qtime.toString("HH:mm")

        if end_qtime <= start_qtime:
            self.show_error("End time must be after start time.")
            return

        # ---- الدكتور (اختياري) ----
        doctor_id = None
        if self.ui.comboBoxSelectInstructor.currentIndex() > 0:
            data = self.ui.comboBoxSelectInstructor.currentData()
            if data is not None:
                try:
                    doctor_id = int(data)
                except (TypeError, ValueError):
                    doctor_id = None

        # ===== استدعاء دالة إضافة السكشن في الداتا بيس =====
        try:
            msg = self.admin_utils.db.add_section(
                course_code=course_code,
                doctor_id=doctor_id,
                days=days,
                time_start=time_start,
                time_end=time_end,
                room=full_room,
                capacity=capacity,
                semester=semester,
                state=state,
            )
        except Exception as e:
            self.show_error(f"Error while adding section:\n{e}")
            return

        self.show_info(msg)
        self.accept()


# =============================== MAIN (تشغيل مباشر) ===============================

if __name__ == "__main__":
    app = QApplication(sys.argv)

    dialog = AddSectionDialog(admin)
    dialog.show()

    sys.exit(app.exec())