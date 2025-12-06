# class_profile_widget.py

import os
import sys

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt

# واجهة بروفايل الطالب
from app_ui.student_ui.submenus_ui.ui_profile import Ui_Profile

# رسائل + فحص الإيميل
from helper_files.shared_utilities import info, warning, error
from helper_files.validators import validate_email

# كائن قاعدة بيانات الطالب
from student.class_student_utilities import db


class ProfileWidget(QWidget):
    """
    Student Profile Widget:
    - يحمّل Ui_Profile الخاصة بالطالب
    - يعرض بيانات الطالب (name, email, program, department ثابت)
    - يسمح بتعديل الإيميل فقط (الاسم قراءة فقط)
    - يفعّل زر Edit Email فقط إذا تغيّر الإيميل
    - يحدّث الإيميل في الداتابيس عن طريق update_user()
    """

    def __init__(self, student_user_data, parent=None):
        """
        student_user_data → (user_id, name, email, program, state, account_status)
        """
        super().__init__(parent)

        # ----------------- Setup UI -----------------
        self.ui = Ui_Profile()
        self.ui.setupUi(self)

        # ----------------- Store DB and user info -----------------
        self.db = db
        self.student_id = student_user_data[0]
        self.name = student_user_data[1] or ""
        self.email = student_user_data[2] or ""
        self.program = student_user_data[3] or ""   # COMP, PWM, ...

        # نخزن القيمة الأصلية للإيميل عشان نعرف إذا صار تغيير
        self._original_email = self.email

        # ----------------- Load data into UI -----------------
        self.load_initial_data()

        # الاسم/البرنامج/القسم قراءة فقط
        self.ui.lineEditName.setReadOnly(True)
        # لو عندك في الـ UI:
        # self.ui.lineEditProgram.setReadOnly(True)
        # self.ui.lineEditDepartment.setReadOnly(True)

        # ----------------- Connect buttons -----------------
        # زر تعديل الإيميل = زر الحفظ
        self.ui.buttonEditEmail.clicked.connect(self.save_changes)

        # لو موجود زر cancel في الواجهة، نربطه بدالة الإلغاء
        if hasattr(self.ui, "buttonCancel"):
            self.ui.buttonCancel.clicked.connect(self.cancel_edit)

        # لو عندك زر Edit ثاني ما تستخدمه:
        if hasattr(self.ui, "buttonEdit"):
            self.ui.buttonEdit.setEnabled(False)
            self.ui.buttonEdit.hide()

        # ----------------- Track changes on fields -----------------
        # نتابع الإيميل فقط، لأن الاسم ثابت
        self.ui.lineEditEmail.textChanged.connect(self.on_fields_changed)

        # في البداية ما في تغييرات → نعطّل زر Edit Email
        self.set_dirty(False)

    # ---------------------------------------------------------
    # INITIAL DATA
    # ---------------------------------------------------------
    def load_initial_data(self):
        """يحط بيانات الطالب في الحقول."""
        self.ui.lineEditName.setText(self.name)
        self.ui.lineEditEmail.setText(self.email)

        # لو في حقول إضافية في UI الطالب (مثلاً program / department) عدّلها هنا:
        if hasattr(self.ui, "lineEditProgram"):
            self.ui.lineEditProgram.setText(self.program or "N/A")

        if hasattr(self.ui, "lineEditDepartment"):
            self.ui.lineEditDepartment.setText("Electrical and Computer Engineering")

    # ---------------------------------------------------------
    # DIRTY STATE (هل فيه تغييرات؟)
    # ---------------------------------------------------------
    def set_dirty(self, dirty: bool):
        """
        dirty = True  → فعّل زر Edit Email
        dirty = False → عطّله
        """
        self.ui.buttonEditEmail.setEnabled(dirty)

    def on_fields_changed(self):
        """
        ينادي تلقائيًا لما يتغيّر الإيميل.
        إذا الإيميل الجديد يختلف عن الأصلي → نفعّل الزر.
        """
        current_email = self.ui.lineEditEmail.text().strip()
        dirty = (current_email != self._original_email)
        self.set_dirty(dirty)

    # ---------------------------------------------------------
    # SAVE CHANGES (email only)
    # ---------------------------------------------------------
    def save_changes(self):
        new_email = self.ui.lineEditEmail.text().strip()

        # التحقق من أن الإيميل مو فاضي
        if not new_email:
            warning(self, "Email cannot be empty.")
            return

        # Validate email format
        email_error = validate_email(new_email)
        if email_error:
            warning(self, "Invalid Email")
            return

        # لو ما تغيّر شيء فعليًا
        if new_email == self._original_email:
            warning(self, "No Changes")
            self.set_dirty(False)
            return

        # نحدّث الإيميل فقط، الاسم ما نلمسه
        result = self.db.update_user(
            self.student_id,
            email=new_email
        )

        if "successfully" in result.lower():
            info(self, "Profile updated successfully.")

            # تحديث القيم الداخلية
            self.email = new_email
            self._original_email = new_email

            self.set_dirty(False)
        else:
            error(self, "Error")

    # ---------------------------------------------------------
    # CANCEL EDIT
    # ---------------------------------------------------------
    def cancel_edit(self):
        """
        يرجّع الإيميل للقيمة الأصلية ويطفي الزر.
        الاسم أصلاً ثابت وما يتغيّر.
        """
        self.ui.lineEditEmail.setText(self._original_email)
        self.set_dirty(False)
