import os
import sys

from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtCore import QTime

# عشان نشوف المجلد الرئيسي
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app_ui.admin_ui.submenus_ui.edit_section_dialog import Ui_EditSectionDialog
from helper_files.shared_utilities import BaseLoginForm


class EditSectionDialog(QDialog, BaseLoginForm):
    """
    Dialog لتعديل سكشن موجود:
    - يستقبل admin_utils + section_data (dict) من شاشة المانج.
    - يعبّي الحقول بالبيانات الحالية.
    - لما تضغط Save يستدعي admin.admin_update_section.
    """

    def __init__(self, admin_utils, section_data: dict, parent=None):
        QDialog.__init__(self, parent)
        BaseLoginForm.__init__(self, parent)

        self.ui = Ui_EditSectionDialog()
        self.ui.setupUi(self)

        self.admin_utils = admin_utils
        self.section_data = section_data
        self.section_id = section_data["section_id"]

        # نخزن days الأصلية عشان الآن ما نلعب فيها
        self.original_days = section_data.get("days") or ""

        # تجهيز الواجهة بالبيانات
        self.setup_initial_values()

        # ربط الأزرار
        self.ui.buttonSave.clicked.connect(self.handle_save)
        self.ui.buttonCancel.clicked.connect(self.reject)

    # ================= إعداد القيم الابتدائية =================

    def setup_initial_values(self):
        d = self.section_data

        # ----- الكورس (نعرضه بس، ما نغيّره من هنا) -----
        self.ui.comboBoxSelectCourse.clear()
        self.ui.comboBoxSelectCourse.addItem(str(d["course_code"]))
        self.ui.comboBoxSelectCourse.setEnabled(False)

        # ----- الدكتور (نخليه Editable رقم/اسم بسيط) -----
        self.ui.comboBoxSelectInstructor.clear()
        doctor_val = "" if d["doctor_id"] is None else str(d["doctor_id"])
        if doctor_val:
            self.ui.comboBoxSelectInstructor.addItem(doctor_val)
            self.ui.comboBoxSelectInstructor.setCurrentIndex(0)
        self.ui.comboBoxSelectInstructor.setEditable(True)

        # ----- الوقت -----
        def parse_time(value, default_h=8, default_m=0):
            if not value:
                return QTime(default_h, default_m)
            try:
                h, m = str(value).split(":")
                return QTime(int(h), int(m))
            except Exception:
                return QTime(default_h, default_m)

        self.ui.timeEditFrom.setTime(parse_time(d.get("time_start")))
        self.ui.timeEditTo.setTime(parse_time(d.get("time_end"), default_h=9))

        # ----- المبنى + الغرفة من حقل room -----
        room_val = (d.get("room") or "").strip()
        building = ""
        room = ""

        # نحاول نفصل بين المبنى/الغرفة إذا مكتوبة بصيغة B45-201
        if "-" in room_val:
            building, room = room_val.split("-", 1)
        elif " " in room_val:
            building, room = room_val.split(" ", 1)
        else:
            building = room_val

        self.ui.lineEditBuilding.setText(building)
        self.ui.lineEditRoom.setText(room)

        # ----- السعة -----
        cap = d.get("capacity") or 0
        try:
            cap = int(cap)
        except ValueError:
            cap = 0
        self.ui.spinBoxCapacity.setValue(cap)

        # ----- السمستر -----
        semester = (d.get("semester") or "").strip()
        if semester:
            idx = self.ui.comboBoxSelectTerm.findText(semester)
            if idx >= 0:
                self.ui.comboBoxSelectTerm.setCurrentIndex(idx)
            else:
                self.ui.comboBoxSelectTerm.addItem(semester)
                self.ui.comboBoxSelectTerm.setCurrentIndex(
                    self.ui.comboBoxSelectTerm.count() - 1
                )

        # ----- الحالة (open / closed) -----
        state = (d.get("state") or "").capitalize()
        if state:
            idx = self.ui.comboBoxSelectStatus.findText(state)
            if idx >= 0:
                self.ui.comboBoxSelectStatus.setCurrentIndex(idx)

        # ====== ملاحظة عن الأيام ======
        # عندنا days كنص (مثلاً: "UMW" أو "SU" حسب اللي استخدمتَه قبل).
        # حالياً ما نعدل الأيام من الدايلوج الجديد عشان ما نخرب منطق الـ check_time_conflict.
        # نخلي الأزرار شكلية الآن، لكن القيمة الفعلية من original_days.
        # لو حاب بعدين نخليها تشتغل 100% نضبط فورمات موحّد للأيام في كل المشروع.
        # (ما نغيّر على days في هذي النسخة)

    # ================= تجميع + حفظ =================

    def handle_save(self):
        """
        نجمع القيم من الواجهة ونسمي admin_update_section.
        ما نغيّر course_code ولا section_id من هنا.
        """
        # ---- السعة ----
        capacity = self.ui.spinBoxCapacity.value()
        if capacity <= 0:
            QMessageBox.warning(self, "Invalid Capacity", "Capacity must be greater than 0.")
            return

        # ---- الوقت ----
        time_start = self.ui.timeEditFrom.time().toString("HH:mm")
        time_end = self.ui.timeEditTo.time().toString("HH:mm")
        if time_start >= time_end:
            QMessageBox.warning(self, "Invalid Time", "Start time must be before end time.")
            return

        # ---- المبنى + الغرفة -> room ----
        building = self.ui.lineEditBuilding.text().strip()
        room_num = self.ui.lineEditRoom.text().strip()

        if building and room_num:
            room = f"{building}-{room_num}"
        else:
            room = building or room_num or None

        # ---- الدكتور ----
        instr_text = self.ui.comboBoxSelectInstructor.currentText().strip()
        doctor_id = None
        if instr_text:
            if instr_text.isdigit():
                doctor_id = int(instr_text)
            else:
                # لو حاب تخليها نصية في الداتابيس عدل نوع العمود
                doctor_id = instr_text  # حالياً ما نتشدد

        # ---- السمستر ----
        semester = self.ui.comboBoxSelectTerm.currentText().strip() or None

        # ---- الحالة ----
        state_text = self.ui.comboBoxSelectStatus.currentText().strip().lower() or None

        # ---- الأيام (نرجّع نفس النص القديم) ----
        days = self.original_days

        # ================= CALL ADMIN =================
        msg = self.admin_utils.admin_update_section(
            section_id=self.section_id,
            doctor_id=doctor_id,
            days=days,
            time_start=time_start,
            time_end=time_end,
            room=room,
            capacity=capacity,
            semester=semester,
            state=state_text,
        )

        QMessageBox.information(
            self,
            "Update Section",
            msg or "Section updated successfully."
        )
        self.accept()
