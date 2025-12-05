from PyQt6.QtWidgets import QWidget
from app_ui.student_ui.submenus_ui.ui_register_courses_stackedwidget import Ui_RegisterCoursesStackedWidget

from student.submenus.class_register_courses import RegisterCoursesWidget
from student.submenus.class_view_sections import ViewSectionsWidget


class RegisterCoursesStackedWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Load UI
        self.ui = Ui_RegisterCoursesStackedWidget()
        self.ui.setupUi(self)

        # Create pages
        self.page_courses = RegisterCoursesWidget(parent=self)
        self.page_sections = ViewSectionsWidget(parent=self)

        # Put pages inside the stack
        self.ui.stackedWidget.addWidget(self.page_courses)     # index 2
        self.ui.stackedWidget.addWidget(self.page_sections)    # index 3

        # Remove empty auto-generated pages
        self.ui.stackedWidget.removeWidget(self.ui.page)
        self.ui.stackedWidget.removeWidget(self.ui.page_2)

        # Show courses page first
        self.show_courses_page()

    # ------------------------------------
    # Navigation API
    # ------------------------------------
    def show_courses_page(self):
        self.ui.stackedWidget.setCurrentWidget(self.page_courses)

    def show_sections_page(self, course_data: dict):
        """Called by RegisterCoursesWidget when user selects a course."""
        self.page_sections.load_sections(course_data)
        self.ui.stackedWidget.setCurrentWidget(self.page_sections)
