# class_profile_widget.py

import os
import sys

from PyQt6.QtWidgets import QWidget
from app_ui.admin_ui.submenus_ui.ui_profile import Ui_Profile

from helper_files.shared_utilities import info, warning, error
from helper_files.validators import validate_email, hash_password

from admin.class_admin_utilities import db


class ProfileWidget(QWidget):
    """
    نسخة مبسّطة من صفحة البروفايل:

    - تعرض بيانات الأدمن (الاسم + الإيميل).
    - زر Edit:
        يفتح حقل الإيميل للتعديل فقط.
    - زر Save:
        يتحقق من الإيميل ثم يحفظه في قاعدة البيانات.
    - زر Cancel:
        يرجّع القيم القديمة ويقفل التعديل.
    - زر Change Password: (نخليه مثل ما هو مستقبلاً لو حبيت تربطه)
    """

    def __init__(self, admin_user_data, parent=None):
        """
        admin_user_data → (user_id, name, email, program, state, account_status)
        """
        super().__init__(parent)

        # ---------- UI ----------
        self.ui = Ui_Profile()
        self.ui.setupUi(self)

        # ---------- بيانات المستخدم ----------
        self.db = db
        self.admin_id = admin_user_data[0]
        self.name = admin_user_data[1]
        self.email = admin_user_data[2]
        self.program = admin_user_data[3]  # مو مهمة للأدمن حاليًا

        # نخزن نسخة أصلية عشان الـ Cancel
        self.original_name = self.name
        self.original_email = self.email

        # حمل البيانات في الحقول
        self.load_initial_data()

        # ربط الأزرار
        self.ui.buttonEdit.clicked.connect(self.start_edit_email_mode)
        self.ui.buttonSave.clicked.connect(self.save_changes)
        self.ui.buttonCancel.clicked.connect(self.cancel_edit)

        # زر تغيير الباسورد نخليه مقفول مؤقتاً أو تبرمجه لاحقاً
        self.ui.buttonChangePassword.setEnabled(False)

        # في البداية: ممنوع التعديل
        self.disable_edit_mode()

    # ---------------------------------------------------------
    # INITIAL DATA
    # ---------------------------------------------------------
    def load_initial_data(self):
        self.ui.lineEditName.setText(self.name)
        self.ui.lineEditEmail.setText(self.email)

        # قسم/كلية ثابتة
        self.ui.lineEditDepartment.setText("Electrical and Computer Engineering")

        # كلمة المرور مجرد شكل
        self.ui.lineEditPassword.setText("••••••••")

    # ---------------------------------------------------------
    # ENABLE/DISABLE EDIT MODE
    # ---------------------------------------------------------
    def start_edit_email_mode(self):
        """
        لما تضغط زر Edit:
        - نخلي حقل الإيميل فقط قابل للتعديل.
        - نفعل Save + Cancel.
        - نعطل Edit.
        """
        # نخلي الإيميل بس هو اللي يقدر يكتب فيه
        self.ui.lineEditEmail.setReadOnly(False)

        # نخلي باقي الحقول مقفولة (الاسم، القسم، الباسورد)
        self.ui.lineEditName.setReadOnly(True)
        self.ui.lineEditDepartment.setReadOnly(True)
        self.ui.lineEditPassword.setReadOnly(True)

        # تفعيل الأزرار المناسبة
        self.ui.buttonSave.setEnabled(True)
        self.ui.buttonCancel.setEnabled(True)
        self.ui.buttonEdit.setEnabled(False)

    def disable_edit_mode(self):
        """
        نقفل كل الحقول ونرجّع حالة الأزرار:
        - Edit مفعّل
        - Save / Cancel مقفولين
        """
        self.ui.lineEditName.setReadOnly(True)
        self.ui.lineEditEmail.setReadOnly(True)
        self.ui.lineEditDepartment.setReadOnly(True)
        self.ui.lineEditPassword.setReadOnly(True)

        self.ui.buttonSave.setEnabled(False)
        self.ui.buttonCancel.setEnabled(False)
        self.ui.buttonEdit.setEnabled(True)

    # ---------------------------------------------------------
    # SAVE CHANGES (EMAIL ONLY)
    # ---------------------------------------------------------
    def save_changes(self):
        """
        يحفظ التغيير في الإيميل فقط.
        """
        new_email = self.ui.lineEditEmail.text().strip()

        if not new_email:
            warning("Missing Info", "Email cannot be empty.")
            return

        # التحقق من صيغة الإيميل
        email_error = validate_email(new_email)
        if email_error:
            warning("Invalid Email", email_error)
            return

        # لو الإيميل ما تغيّر، ما في داعي نحدّث
        if new_email == self.email:
            info("No Changes", "No changes to save.")
            self.disable_edit_mode()
            return

        # تحديث في الداتا بيس
        result = self.db.update_user(
            self.admin_id,
            email=new_email
        )

        if "successfully" in result.lower():
            info("Success", "Email updated successfully.")

            # نحدّث القيم المخزّنة
            self.email = new_email
            self.original_email = new_email

            # نقفل التعديل مرة ثانية
            self.disable_edit_mode()
        else:
            error("Error", result)

    # ---------------------------------------------------------
    # CANCEL EDIT
    # ---------------------------------------------------------
    def cancel_edit(self):
        """
        يرجع الإيميل للقيمة الأصلية ويقفل التعديل.
        """
        self.ui.lineEditEmail.setText(self.original_email)
        self.disable_edit_mode()
