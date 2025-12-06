import sys
import os

# Add project root to path (finalProject/)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "././")))

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QStackedWidget,
    QMessageBox,
)
from PyQt6.QtCore import QTimer

# -----------------------------
# UI Pages (نفس الصفحات اللي عندك)
# -----------------------------
from login_files.ui_files.class_create_account_widget import CreateAccountWidget
from login_files.ui_files.class_confirm_email_widget import ConfirmEmailWidget

# -----------------------------
# Shared base class and helpers
# -----------------------------
from helper_files.shared_utilities import (
    BaseLoginForm,
    EmailSender,
    CodeGenerator,
)
from helper_files.validators import (
    hash_password,
    validate_full_name,
    validate_email,
)

# -----------------------------
# Database utilities
# -----------------------------
from admin.class_admin_utilities import db


class SignupAndConfirmWindow(BaseLoginForm):
    """
    نافذة مستقلة مسؤولة عن:
    - عرض صفحة CreateAccountWidget
    - إرسال كود تفعيل على الإيميل
    - عرض صفحة ConfirmEmailWidget
    - التحقق من الكود
    - إنشاء المستخدم في قاعدة البيانات

    * بدون صفحة Login
    * بدون Reset Password
    * هنا ننشئ حسابات ADMIN فقط
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # DB و إيميل
        self.db = db
        self.email_sender = EmailSender()

        # نخزن بيانات المستخدم المؤقتة (قبل إنشاء الحساب فعليًا)
        self.new_user_data: dict = {}

        # مولّد الأكواد: email -> CodeGenerator
        self.code_generators: dict[str, CodeGenerator] = {}

        # -----------------------------
        # 1) إنشاء الـ pages
        # -----------------------------
        self.create_account_page = CreateAccountWidget()
        self.confirm_email_page = ConfirmEmailWidget()

        # نخفي حقل البرنامج لأنه غير مطلوب في إنشاء الأدمن
        try:
            # نضبط قيمة افتراضية صحيحة للداتا بيس (مثلاً COMP)
            self.create_account_page.comboBoxProgram.setCurrentIndex(1)
            # نخفي الـ comboBox من الواجهة
            self.create_account_page.comboBoxProgram.hide()
        except AttributeError:
            # احتياط لو الاسم تغيّر في المستقبل
            pass

        # -----------------------------
        # 2) إنشاء الـ stacked widget
        # -----------------------------
        self.stacked = QStackedWidget()
        self.stacked.addWidget(self.create_account_page)   # index 0
        self.stacked.addWidget(self.confirm_email_page)    # index 1
        self.stacked.setCurrentIndex(0)

        # -----------------------------
        # 3) layout للنافذة
        # -----------------------------
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stacked)

        # نبدأ بصفحة إنشاء الحساب
        self.go_to_create_account()

        # نفرغ رسالة الستاتس
        self.create_account_page.labelGeneralStatus.setText("")

        # -----------------------------
        # 4) توصيل الإشارات (Signals)
        # -----------------------------
        # زر إنشاء الحساب
        self.create_account_page.buttonCreateAccont.clicked.connect(
            self.handle_create_account_click
        )

        # زر "Login here" - هنا بس نقفل النافذة (أنت إذا حاب تربطها بشيء ثاني اربط الإشارة برا)
        self.create_account_page.buttonLoginHere.clicked.connect(self.close)

        # أزرار صفحة تأكيد الإيميل
        self.confirm_email_page.buttonBackToCreateAccount.clicked.connect(
            self.handle_back_to_create_account
        )
        self.confirm_email_page.buttonBackToSignIn.clicked.connect(
            self.handle_back_to_sign_in
        )
        self.confirm_email_page.buttonVerifyCode.clicked.connect(
            self.handle_email_confirmation
        )
        self.confirm_email_page.buttonReSendCode.clicked.connect(
            self.resend_code
        )

        # حجم مبدئي بسيط (تقدر تشيله لو تبغى يعتمد على الـ sizeHint)
        self.resize(900, 600)
        self.setWindowTitle("Admin Sign up & Email Verification")

    # =========================================================
    #                    NAVIGATION
    # =========================================================
    def go_to_create_account(self):
        """إظهار صفحة إنشاء الحساب."""
        self.stacked.setCurrentIndex(0)

    def go_to_confirm_email(self):
        """إظهار صفحة تأكيد الإيميل."""
        self.confirm_email_page.lineEditVerificationCode.clear()
        self.stacked.setCurrentIndex(1)

    # =========================================================
    #      ACCOUNT CREATION AND EMAIL VERIFICATION LOGIC
    # =========================================================
    def handle_create_account_click(self):
        """
        يُنفَّذ لما المستخدم يضغط زر Create Account.
        هذه النسخة مخصصة لإنشاء ADMIN فقط بدون اختيار برنامج.
        """

        # --- 1. قراءة المدخلات ---
        raw_full_name = self.create_account_page.fullName.text().strip()
        raw_email = self.create_account_page.email.text().strip()
        raw_password = self.create_account_page.password.text()

        labelStatus = self.create_account_page.labelGeneralStatus

        # --- 2. التحقق من الاسم الكامل ---
        full_name_parts, name_error = validate_full_name(raw_full_name)
        if name_error:
            labelStatus.setText(name_error)
            self.set_label_color(labelStatus, "red")
            return
        full_name = " ".join(full_name_parts)

        # --- 3. التحقق من الإيميل ---
        email_error = validate_email(raw_email)
        if email_error:
            labelStatus.setText(email_error)
            self.set_label_color(labelStatus, "red")
            return

        # --- 4. التأكد أن الإيميل غير موجود مسبقًا في الـ DB ---
        if self.db.check_email_exists(raw_email):
            self.create_account_page.highlight_invalid_lineedit(
                self.create_account_page.email,
                "Email already exists.",
            )
            labelStatus.setText("Email already registered.")
            self.set_label_color(labelStatus, "red")
            return

        # --- 5. كل شيء سليم -> نخزن البيانات مؤقتًا ---
        # نستخدم برنامج افتراضي صالح للداتا بيس (غيّره لو عندك كود خاص بالأدمن)
        default_program = "COMP"

        self.new_user_data = {
            "name": full_name,
            "email": raw_email,
            "password": raw_password,
            "program": None,
            "state": "admin",             # بدل student -> admin
        }

        # --- 6. إظهار رسالة نجاح مبدئية ---
        labelStatus.setText("All good! Please confirm your email...")
        self.set_label_color(labelStatus, "green")

        # --- 7. إنشاء CodeGenerator لو ما كان موجود لهذا الإيميل ---
        if raw_email not in self.code_generators:
            self.code_generators[raw_email] = CodeGenerator(validity_minutes=5)

        # --- 8. إرسال الكود على الإيميل ---
        sent = self.send_verification_code(self.new_user_data["email"])

        if sent:
            print(f"Verification code sent: {self.code_generators[raw_email].code}")

        # --- 9. الانتقال لصفحة تأكيد الإيميل بعد ثانيتين تقريبًا ---
        QTimer.singleShot(1500, self.go_to_confirm_email)

    def send_verification_code(self, to_email: str) -> bool:
        """
        توليد كود جديد (أو إعادة استخدام generator موجود)
        ثم إرساله إلى الإيميل.
        """
        if to_email not in self.code_generators:
            self.code_generators[to_email] = CodeGenerator(validity_minutes=5)

        generator = self.code_generators[to_email]
        code = generator.generate_verification_code()  # يحدّث الوقت

        subject = "Your Verification Code"
        body = (
            f"Your verification code is: {code}\n"
            f"Expires in {generator.validity_minutes} minutes."
        )

        sent = self.email_sender.send_email(to_email, subject, body)

        if sent:
            QMessageBox.information(self, "Code Sent", "A verification code was sent to your email.")
            self.confirm_email_page.start_cooldown_timer()
        else:
            QMessageBox.critical(self, "Error", "Failed to send verification email.")

        return sent

    # ----------------------------------------------------------
    #           EMAIL CONFIRMATION LOGIC
    # ----------------------------------------------------------
    def check_is_code_valid(self, entered_code: str, email: str) -> tuple[bool, str]:
        if not entered_code:
            return False, "Code cannot be empty."

        generator = self.code_generators.get(email)
        if not generator:
            return False, "No code generated for this email."

        if entered_code != generator.code:
            return False, "Incorrect verification code."

        if generator.is_code_expired():
            return False, "The code has expired. Please request a new one."

        return True, ""

    def handle_email_confirmation(self):
        """
        يُنفَّذ لما المستخدم يضغط زر Verify Code.
        لو الكود صحيح -> ينشئ الحساب في قاعدة البيانات.
        """
        if not self.new_user_data:
            QMessageBox.warning(self, "Error", "No registration data found.")
            return

        entered_code = self.confirm_email_page.lineEditVerificationCode.text().strip()
        email = self.new_user_data["email"]

        is_valid, reason = self.check_is_code_valid(entered_code, email)

        if not is_valid:
            self.shake_widget(self.confirm_email_page.lineEditVerificationCode)
            self.highlight_invalid_lineedit(
                self.confirm_email_page.lineEditVerificationCode,
                reason,
            )
            self.confirm_email_page.lineEditVerificationCode.setFocus()
            if reason != "Code cannot be empty.":
                QMessageBox.warning(self, "Invalid Code", reason)
            return

        # --- الكود صحيح -> إنشاء الحساب ---
        QMessageBox.information(self, "Code Verified", "Email verified successfully!")

        password_hashed = hash_password(self.new_user_data["password"])
        result = self.db.add_users(
            self.new_user_data["name"],
            self.new_user_data["email"],
            password_hashed,
            self.new_user_data["program"],  # قيمة افتراضية
            self.new_user_data["state"],    # admin
        )

        if "successfully" in result:
            QMessageBox.information(
                self,
                "Email Confirmed",
                "Admin account created! Please wait for admin approval (if applicable).",
            )
            # هنا بدل ما نرجع للّوجن، نقفل النافذة
            QTimer.singleShot(1000, self.close)
        else:
            QMessageBox.critical(self, "Error", f"An error occurred: {result}")

    # --- resend code logic ---
    def resend_code(self):
        if not self.new_user_data:
            QMessageBox.warning(self, "Error", "No registration data found.")
            return

        email = self.new_user_data["email"]
        sent = self.send_verification_code(email)
        if sent:
            QMessageBox.information(self, "Code Sent", "Verification code resent successfully.")

    # =========================================================
    #               BACK NAVIGATION
    # =========================================================
    def handle_back_to_create_account(self):
        response = self.show_confirmation(
            "Are you sure?",
            "Going back might cancel the registration process.",
        )
        if response == QMessageBox.StandardButton.Yes:
            self.go_to_create_account()

    def handle_back_to_sign_in(self):
        """
        هنا مافي صفحة Login، فـ "Back to Sign In" بس يقفل النافذة.
        (لو حاب تربطها بنافذة لوجن ثانية، غيّر هذا الميثود في مشروعك)
        """
        response = self.show_confirmation(
            "Are you sure?",
            "Going back will close the registration window.",
        )
        if response == QMessageBox.StandardButton.Yes:
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SignupAndConfirmWindow()
    window.show()
    sys.exit(app.exec())
