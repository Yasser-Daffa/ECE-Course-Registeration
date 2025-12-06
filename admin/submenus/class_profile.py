# class_profile_widget.py

import os
import sys

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt

from app_ui.admin_ui.submenus_ui.ui_profile import Ui_Profile
from helper_files.shared_utilities import info, warning, error
from helper_files.validators import validate_email

from admin.class_admin_utilities import db


class ProfileWidget(QWidget):
    """
    Simple Profile Widget:
    - يحمّل Ui_Profile
    - يعرض بيانات الأدمن (name, email, department ثابت)
    - يسمح بتعديل الإيميل فقط (الاسم قراءة فقط)
    - يفعّل زر Save / Cancel فقط إذا تغيّر الإيميل
    - يحدّث الإيميل في الداتابيس عن طريق update_user()
    """

    def __init__(self, admin_user_data, parent=None):
        """
        admin_user_data → (user_id, name, email, program, state, account_status)
        """
        super().__init__(parent)

        # ----------------- Setup UI -----------------
        self.ui = Ui_Profile()
        self.ui.setupUi(self)

        # ----------------- Store DB and user info -----------------
        self.db = db
        self.admin_id = admin_user_data[0]
        self.name = admin_user_data[1]
        self.email = admin_user_data[2]
        self.program = admin_user_data[3]   # مو مستخدم حاليًا بس نخليه موجود

        # هنحفظ القيم الأصلية عشان نقارن
        self._original_name = self.name
        self._original_email = self.email

        # ----------------- Load data into UI -----------------
        self.load_initial_data()

        # نخلي الاسم قراءة فقط (ما يقدر يعدله)
        self.ui.lineEditName.setReadOnly(True)
        # لو تبغاه يبان معطّل بالكامل:
        # self.ui.lineEditName.setEnabled(False)

        # ----------------- Connect buttons -----------------
        self.ui.buttonEditEmail.clicked.connect(self.save_changes)

        # زر Edit ما نستخدمه الآن
        if hasattr(self.ui, "buttonEdit"):
            self.ui.buttonEdit.setEnabled(False)
            self.ui.buttonEdit.hide()

        # ----------------- Track changes on fields -----------------
        # نتابع الإيميل فقط، لأن الاسم ثابت
        self.ui.lineEditEmail.textChanged.connect(self.on_fields_changed)

        # في البداية ما في تغييرات → نعطّل Save / Cancel
        self.set_dirty(False)

    # ---------------------------------------------------------
    # INITIAL DATA
    # ---------------------------------------------------------
    def load_initial_data(self):
        """يحط بيانات الأدمن في الحقول."""
        self.ui.lineEditName.setText(self.name)
        self.ui.lineEditEmail.setText(self.email)

        # Department ثابت
        self.ui.lineEditDepartment.setText("Electrical and Computer Engineering")

    # ---------------------------------------------------------
    # DIRTY STATE (هل فيه تغييرات؟)
    # ---------------------------------------------------------
    def set_dirty(self, dirty: bool):
        """
        dirty = True  → فعّل Save + Cancel
        dirty = False → عطّل Save + Cancel
        """
        self.ui.buttonEditEmail.setEnabled(dirty)

    def on_fields_changed(self):
        """
        ينادي تلقائيًا لما يتغيّر الإيميل.
        إذا الإيميل الجديد يختلف عن الأصلي → نفعّل Save/Cancel.
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

        # نعدّل فقط لو الإيميل تغيّر فعلاً
        email_to_update = new_email if new_email != self._original_email else None

        if email_to_update is None:
            warning(self, "No Changes")
            return

        # نحدّث الإيميل فقط، الاسم ما نلمسه
        result = self.db.update_user(
            self.admin_id,
            email=email_to_update
        )

        if "successfully" in result.lower():
            info(self, "Profile updated successfully.")

            # تحديث القيم الداخلية
            self.email = email_to_update
            self._original_email = email_to_update

            self.set_dirty(False)
        else:
            error(self, "Error")

    # ---------------------------------------------------------
    # CANCEL EDIT
    # ---------------------------------------------------------
    def cancel_edit(self):
        """
        يرجّع الإيميل للقيمة الأصلية ويطفي Save/Cancel.
        الاسم أصلاً ثابت وما يتغيّر.
        """
        self.ui.lineEditEmail.setText(self._original_email)
        self.set_dirty(False)
