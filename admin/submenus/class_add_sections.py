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

        # فاليديشن للحقول النصية المهمة (الهز + تغيير البوردر لو حبيت تستخدمها)
        self.attach_non_empty_validator(self.ui.lineEditBuilding, "Building")
        self.attach_non_empty_validator(self.ui.lineEditRoom, "Room")

        # كل ما تغيّر شيء من دول نعيد فحص تفعيل الزر
        self.ui.comboBoxSelectCourse.currentIndexChanged.connect(self.check_all_fields_filled)
        self.ui.comboBoxSelectTerm.currentIndexChanged.connect(self.check_all_fields_filled)
        self.ui.comboBoxSelectStatus.currentIndexChanged.connect(self.check_all_fields_filled)
        self.ui.lineEditBuilding.textChanged.connect(self.check_all_fields_filled)
        self.ui.lineEditRoom.textChanged.connect(self.check_all_fields_filled)
        self.ui.spinBoxCapacity.valueChanged.connect(self.check_all_fields_filled)

        # أزرار الأيام برضه تؤثر على تفعيل الزر
        self.ui.pushButtonDaySun.toggled.connect(self.check_all_fields_filled)
        self.ui.pushButtonDayMon.toggled.connect(self.check_all_fields_filled)
        self.ui.pushButtonDayTue.toggled.connect(self.check_all_fields_filled)
        self.ui.pushButtonDayWed.toggled.connect(self.check_all_fields_filled)
        self.ui.pushButtonDayThu.toggled.connect(self.check_all_fields_filled)

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
        rows = self.admin_utils.db.ListCourses()  # [(code, name, credits), ...]

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
        - على الأقل يوم واحد مختار
        """
        course_ok = self.ui.comboBoxSelectCourse.currentIndex() > 0
        term_ok = self.ui.comboBoxSelectTerm.currentIndex() > 0
        status_ok = self.ui.comboBoxSelectStatus.currentIndex() > 0

        building = self.ui.lineEditBuilding.text().strip()
        room = self.ui.lineEditRoom.text().strip()
        capacity_ok = self.ui.spinBoxCapacity.value() > 0

        days_ok = any([
            self.ui.pushButtonDaySun.isChecked(),
            self.ui.pushButtonDayMon.isChecked(),
            self.ui.pushButtonDayTue.isChecked(),
            self.ui.pushButtonDayWed.isChecked(),
            self.ui.pushButtonDayThu.isChecked(),
        ])

        if course_ok and term_ok and status_ok and building and room and capacity_ok and days_ok:
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
        ملاحظة: نفترض أن check_all_fields_filled ضمنّت أن الحقول الأساسية صحيحة.
        """

        # ---- الكورس ----
        course_code = self.ui.comboBoxSelectCourse.currentData()

        # ---- الترم (السمستر) ----
        semester = self.ui.comboBoxSelectTerm.currentText().strip()

        # ---- الحالة (state) ----
        state = self.ui.comboBoxSelectStatus.currentText().strip().lower()

        # ---- المبنى والغرفة ----
        building = self.ui.lineEditBuilding.text().strip().upper()
        room = self.ui.lineEditRoom.text().strip().upper()
        full_room = f"{building}{room}"

        # ---- السعة ----
        capacity = self.ui.spinBoxCapacity.value()

        # ---- الأيام ----
        days = self.get_selected_days()

        # ---- الوقت ----
        start_qtime = self.ui.timeEditFrom.time()
        end_qtime = self.ui.timeEditTo.time()

        time_start = start_qtime.toString("HH:mm")
        time_end = end_qtime.toString("HH:mm")

        # الشرط المنطقي المهم: وقت النهاية بعد وقت البداية
        if end_qtime <= start_qtime:
            self.show_error("End time must be after start time.")
            return

        # ---- الدكتور (اختياري) ----
        doctor_id = None
        if self.ui.comboBoxSelectInstructor.currentIndex() > 0:
            data = self.ui.comboBoxSelectInstructor.currentData()
            try:
                doctor_id = int(data) if data is not None else None
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


# =============================== MAIN (تشغيل مباشر) ===============================

if __name__ == "__main__":
    app = QApplication(sys.argv)

    dialog = AddSectionDialog(admin)
    dialog.show()

    sys.exit(app.exec())
