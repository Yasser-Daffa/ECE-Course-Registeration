# HELPER-FUNCTIONS



# form_helpers.py

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


from PyQt6.QtCore import Qt, QEvent, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QColor, QIcon, QPalette

from PyQt6.QtWidgets import QApplication, QWidget, QGraphicsDropShadowEffect, QFrame, QHBoxLayout, QPushButton

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
    

    def add_shadow(self, widget, blur=15, xOffset=0, yOffset=5, color=(0, 0, 0, 160)):
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur)
        shadow.setXOffset(xOffset)
        shadow.setYOffset(yOffset)
        shadow.setColor(QColor(*color))
        widget.setGraphicsEffect(shadow)

    def resizeEvent(self, event):
        """Reposition ALL toggle buttons when window resizes."""
        super().resizeEvent(event)
        for line_edit in self.toggle_buttons:
            self.update_toggle_button_position(line_edit)


    def update_toggle_button_position(self, line_edit: QLineEdit):
        """ The calculations required to Move toggle button 
        to the correct position inside the line edit."""
        btn = self.toggle_buttons[line_edit]

        x = line_edit.width() - btn.width() - 4
        y = (line_edit.height() - btn.height()) // 2

        btn.move(x, y)


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

        # Store references
        self.toggle_buttons[line_edit] = btn
        self.show_password_states[line_edit] = False
        
        # position correctly
        self.update_toggle_button_position(line_edit)
        
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

    def validate_combobox(self, combo):
        """
        Checks if the current QComboBox selection is valid (index > 0).
        Highlights the combo box in red and shows a tooltip if invalid.
        
        Returns:
        - True if valid selection
        - False if invalid
        """
        # Store the original style to restore later
        if not hasattr(combo, "_original_style"):
            combo._original_style = combo.styleSheet()

        valid = combo.currentIndex() > 0
        if not valid:
            combo.setStyleSheet(combo._original_style + "\nQComboBox { border: 2px solid red; }")
            combo.setToolTip("Please select a valid option.")
        else:
            combo.setStyleSheet(combo._original_style)
            combo.setToolTip("")
        return valid
    
            #---------- ANIMATION ATTEMPT ()-------------#
    def shake_widget(self, widget):
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
        self._shake_animation = anim  # keep reference