# HELPER-FUNCTIONS
# ----------------
# This file contains reusable helper functions and a base form class
# that provide:
# 1. Password toggle functionality
# 2. Border highlighting for invalid inputs
# 3. Attatchement Methods for field validators
# 4. Adds Shadow and animation methods for widgets
# ----------------------

from PyQt6.QtCore import Qt, QEvent, QPropertyAnimation, QEasingCurve, QPoint, QTimer
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import (
    QApplication, QWidget, QGraphicsDropShadowEffect, QFrame,
    QHBoxLayout, QPushButton, QComboBox, QLineEdit
)

import login_resources_rc

# -----------------------------
# SIMPLE FIELD VALIDATORS
# -----------------------------
def all_fields_filled(fields) -> bool:
    """
    Checks if all fields in the given list are non-empty.
    
    'fields' should be a list of (field_name, field_value) tuples.
    
    Returns True if all values are non-empty, False otherwise.
    
    Example usage:
        username = "user123"
        email = "user@example.com"
        password = ""
        fields = [(username), (email), (password)]
        
        if all_fields_filled(fields):
            print("All fields are filled!")
        else:
            print("Some fields are missing!")
        # Output: Some fields are missing!
    """
    return all(str(field_value).strip() != "" for field_value in fields)


def passwords_match(password: str, password_confirm: str) -> bool:
    """
    Checks if the password and its confirmation match.
    """
    return password == password_confirm and password != ""


# -----------------------------
# BASE FORM CLASS
# -----------------------------
class BaseLoginForm(QWidget):
    """Base class with shared methods for forms like CreateAccountWidget."""
    from PyQt6.QtWidgets import QLineEdit
    def __init__(self, parent=None):
        super().__init__(parent)

        
        # Stores each toggle button, keyed by its QLineEdit.
        # Example: toggle_buttons[line_edit] = toggle_btn
        self.toggle_buttons = {}

        # Stores whether each password field is currently visible (True) or hidden (False).
        # We track this ourselves because QLineEdit/QPushButton don't hold this state.
        self.show_password_states = {}

        # These dictionaries let the same toggle logic work for any number of password fields.
        # If future forms have more password boxes, the same code will handle them automatically.
        # This allows the BaseLoginForm to support unlimited password fields without writing new code.
    

    # -------------------------------
    # 1. PASSWORD TOGGLE BUTTONS
    # -------------------------------

    def create_pwrd_toggle_button(self, line_edit: QLineEdit):
        """
        Creates an eye-icon toggle button inside a QLineEdit to show/hide password.
        The button automatically toggles the line_edit's echo mode when clicked.
        """
        btn = QPushButton(line_edit)
        btn.setIcon(QIcon(":/qrc_images/assets/images/open_eye_icon24.png"))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setCheckable(True)
        btn.setFixedSize(24, 24)
        btn.setStyleSheet("border: none; background: transparent;")
        btn.clicked.connect(lambda: self.toggle_password(line_edit))

        # KEEP track of states
        self.toggle_buttons[line_edit] = btn
        self.show_password_states[line_edit] = False

        # initial position
        self.update_toggle_button_position(line_edit)

        # schedule the update after the layout is applied.
        # otherwise it will result in a missplacement on initial launch of the window
        # try commenmting these line and seeing for yourself
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(0, lambda: self.update_toggle_button_position(line_edit))
        #-----------------
        
        return btn

    def toggle_password(self, line_edit: QLineEdit):
        """
        Toggles the visibility of the password for a given QLineEdit.
        Updates the icon accordingly.
        """
        state = self.show_password_states[line_edit]
        if state:
            # Hide password
            line_edit.setEchoMode(self.QLineEdit.EchoMode.Password)
            self.toggle_buttons[line_edit].setIcon(QIcon(":/qrc_images/assets/images/open_eye_icon24.png"))
        else:
            # Show password
            line_edit.setEchoMode(self.QLineEdit.EchoMode.Normal)
            self.toggle_buttons[line_edit].setIcon(QIcon(":/qrc_images/assets/images/close_eye_icon24.png"))
        # Toggle the state
        self.show_password_states[line_edit] = not state


    def update_toggle_button_position(self, line_edit: QLineEdit):
        """ The calculations required to Move toggle button 
        to the correct position inside the line edit."""
        btn = self.toggle_buttons[line_edit]

        x = line_edit.width() - btn.width() - 4
        y = (line_edit.height() - btn.height()) // 2

        btn.move(x, y)


    def resizeEvent(self, event):
        """Reposition ALL toggle buttons when window resizes."""
        super().resizeEvent(event)
        for line_edit in self.toggle_buttons:
            self.update_toggle_button_position(line_edit)


    # -----------------------------
    # 2. BORDER HIGHLIGHTING METHODS
    # -----------------------------
    # We should use these if we only want validations


    ## NOTE:
    # - Each QLineEdit may already have a custom style applied (colors, borders, fonts).
    #   If we just set a red border directly, it would overwrite any existing styles.

    # - To prevent that, we store the original style in a custom attribute on the widget itself:
    #       _original_style = line_edit.styleSheet()

    # - Before applying the red border, we check if this attribute exists using hasattr(line_edit, "_original_style").
    #   - If it exists, we reuse it so we don't overwrite previous styles.
    #   - If it doesn't exist, we save the current style first.
    # - This allows us to easily reset the field back to its original appearance later.

    def highlight_invalid_lineedit(self, line_edit: QLineEdit, message: str):
        """
        Set a red border and tooltip for any invalid QLineEdit.

        Parameters:
        - line_edit: The QLineEdit widget to highlight.
        - message: The tooltip message to show when invalid.
        
        Notes:
        - We store the original stylesheet on the widget itself using a custom
        attribute '_original_style'. This prevents overwriting existing styles.
        - hasattr(line_edit, "_original_style") checks if we have already stored it.
        """
        if not hasattr(line_edit, "_original_style"):
            # Save the original style to restore later
            line_edit._original_style = line_edit.styleSheet()

        # Append a red border style while keeping the original styles
        line_edit.setStyleSheet(
            line_edit._original_style +
            "QLineEdit { border: 2px solid red; } QLineEdit:focus { border: 2px solid red; }"
        )
        # Set tooltip for user guidance
        line_edit.setToolTip(message)


    def reset_lineedit_border(self, line_edit: QLineEdit):
        """
        Reset a QLineEdit's border to its original style.

        - Only resets if we have stored the original style previously.
        - Clears any tooltip message.
        """
        if hasattr(line_edit, "_original_style"):
            line_edit.setStyleSheet(line_edit._original_style)
            line_edit.setToolTip("")


    def validate_confirm_password(self, password_line: QLineEdit, confirm_line: QLineEdit):
        """
        Highlights the confirm password field in red if it doesn't match the main password.

        Parameters:
        - password_line: The main password QLineEdit.
        - confirm_line: The confirmation password QLineEdit.

        Uses:
        - passwords_match() from helper functions to compare values.
        - Calls highlight_invalid_lineedit / reset_lineedit_border accordingly.
        """
        from login_helper_functions import passwords_match

        password = password_line.text()
        confirm = confirm_line.text()

        if passwords_match(password, confirm):
            self.reset_lineedit_border(confirm_line)
        else:
            self.highlight_invalid_lineedit(confirm_line, "Passwords do not match.")


    def validate_non_empty(self, line_edit: QLineEdit, field_name: str = "This field"):
        """
        Highlights a QLineEdit in red if it is empty.

        Parameters:
        - line_edit: The QLineEdit to validate.
        - field_name: Optional friendly name for tooltip message.
        
        Usage:
        - Called on text change to give dynamic feedback.
        """
        if line_edit.text().strip() == "":
            self.highlight_invalid_lineedit(line_edit, f"{field_name} cannot be empty.")
        else:
            self.reset_lineedit_border(line_edit)


    def validate_combobox_selection(self, combo: QComboBox, message: str = "Please select a valid option."):
        """
        Highlights a QComboBox in red if no valid selection is made.

        - A valid selection is considered any index > 0 (common practice where index 0 = placeholder).
        - Uses a custom attribute '_original_style' to store original style for later restoration.

        Returns:
        - True if selection is valid.
        - False if invalid (and highlights the combo box in red).
        """
        if combo.currentIndex() <= 0:
            # Save original style if not already stored
            if not hasattr(combo, "_original_style"):
                combo._original_style = combo.styleSheet()

            combo.setStyleSheet(combo._original_style + "\nQComboBox { border: 2px solid red; }")
            combo.setToolTip(message)
            return False
        else:
            # Restore original style
            if hasattr(combo, "_original_style"):
                combo.setStyleSheet(combo._original_style)
                combo.setToolTip("")
            return True
        

        ## Example usage on how to use these methods
        ## inside some slot or validation function

# self.validate_non_empty(self.ui.lineEditUsername, "Username")
# self.validate_confirm_password(self.ui.lineEditPassword, self.ui.lineEditPasswordConfirm)
# self.validate_combobox_selection(self.ui.comboBoxRole)

    # -----------------------------
    # 3. DYNAMIC VALIDATION HOOKS
    # -----------------------------
    # These are the ones we should be using to check non empty fields
    # Or add a validator in general if we want live feedback 

    def attach_non_empty_validator(self, line_edit: QLineEdit, field_name: str = "This field"):
        """
        Attach dynamic validation to a QLineEdit that checks if it is non-empty.
        Updates the border in real-time as user types.
        """
        line_edit.textChanged.connect(lambda: self.validate_non_empty(line_edit, field_name))

    def attach_confirm_password_validator(self, password_line: QLineEdit, confirm_line: QLineEdit):
        """
        Attach dynamic validation between password and confirm password fields.
        Updates border in real-time while typing.
        """
        password_line.textChanged.connect(lambda: self.validate_confirm_password(password_line, confirm_line))
        confirm_line.textChanged.connect(lambda: self.validate_confirm_password(password_line, confirm_line))

    def attach_combobox_validator(self, combo: QComboBox, message: str = "Please select a valid option."):
        """
        Attach dynamic validation to a QComboBox that checks selection.
        Updates the border immediately on selection change.
        """
        combo.currentIndexChanged.connect(lambda _: self.validate_combobox_selection(combo, message))


    def attach_password_strength_checker(
        self,
        password_line: QLineEdit,
        progress_bar,
        strength_label,
        rules_label
    ):
        """
        Attaches a dynamic password strength checker to a QLineEdit.

        Parameters:
        - password_line: QLineEdit for the password input
        - progress_bar: QProgressBar to display strength
        - strength_label: QLabel to show 'Weak/Moderate/Strong'
        - rules_label: QLabel to show password requirements, updates dynamically

        Behavior:
        - Updates strength label
        - Updates progress bar chunk color (preserving existing stylesheet)
        - Updates requirements label with * prefix and green/red color
        - Highlights password line edit red if requirements not met
        - Preserves original tooltips
        """
        from password_validator import validate_password, password_strength

        # Store original stylesheet to preserve it
        if not hasattr(progress_bar, "_original_style"):
            progress_bar._original_style = progress_bar.styleSheet() or ""

        def update_strength():
            password = password_line.text()
            valid, errors = validate_password(password)
            strength = password_strength(password)

            # --- Update strength label ---
            strength_label.setText(strength)

            # --- Update progress bar value and color only ---
            strength_map = {"Weak": 25, "Moderate": 50, "Strong": 100}
            color_map = {"Weak": "#e74c3c", "Moderate": "#f39c12", "Strong": "#2ecc71"}
            progress_bar.setValue(strength_map[strength])

            # Only append color change to existing style
            progress_bar.setStyleSheet(
                progress_bar._original_style +
                f"""
                QProgressBar::chunk {{
                    background-color: {color_map[strength]};
                }}
                """
            )

            # --- Update requirements label dynamically ---
            requirements = [
                "Password must be at least 8 characters long.",
                "Password must contain at least one uppercase letter.",
                "Password must contain at least one lowercase letter.",
                "Password must contain at least one digit.",
                "Password must contain at least one special character."
            ]

            label_lines = []
            tooltip_lines = []

            for req in requirements:
                color = "green" if req not in errors else "red"
                label_lines.append(f'<span style="color:{color};">* {req}</span>')
                tooltip_lines.append(f'* {req}')

            rules_label.setText("<br>".join(label_lines))
            rules_label.setToolTip("\n".join(tooltip_lines))

            # --- Highlight password line edit if invalid ---
            if not valid:
                self.highlight_invalid_lineedit(password_line, "Password does not meet all requirements.")
            else:
                self.reset_lineedit_border(password_line)

        # Connect signal to update on text change
        password_line.textChanged.connect(update_strength)

        # Call once to initialize display
        update_strength()

        
# -------- EXAMPLE USAGE ---------
# self.attach_non_empty_validator(self.ui.lineEditUsername, "Username")
# self.attach_non_empty_validator(self.ui.lineEditEmail, "Email")
# self.attach_confirm_password_validator(self.ui.lineEditPassword, self.ui.lineEditPasswordConfirm)
# self.attach_combobox_validator(self.ui.comboBoxRole)

#-- EXAMPLE FOR THE "attach_password_stenghth_checker" method

# self.attach_password_strength_checker(
#     self.lineEditPassword,
#     self.progressBarPwrdStrength,
#     self.labelPwrdStrengthStatus,
#     self.labelPasswordRules
# )



    # -------------------------------
    # 4. SHADOW & ANIMATION HELPERS
    # -------------------------------

    def add_shadow(self, widget, blur=15, xOffset=0, yOffset=5, color=(0, 0, 0, 160)):
        """Adds a drop shadow effect to any QWidget"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur)
        shadow.setXOffset(xOffset)
        shadow.setYOffset(yOffset)
        shadow.setColor(QColor(*color))
        widget.setGraphicsEffect(shadow)

    def shake_widget(self, widget):
        """Simple shake animation for widgets (e.g., invalid input)"""
        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(150)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        original_pos = widget.pos()
        offset = 6

        anim.setKeyValueAt(0, original_pos)
        anim.setKeyValueAt(0.25, original_pos + QPoint(-offset, 0))
        anim.setKeyValueAt(0.5, original_pos + QPoint(offset, 0))
        anim.setKeyValueAt(0.75, original_pos + QPoint(-offset, 0))
        anim.setKeyValueAt(1, original_pos)

        anim.start()
        self._shake_animation = anim  # Keep a reference to prevent garbage collection