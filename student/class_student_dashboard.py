import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))


from PyQt6 import QtWidgets
from student.class_student_utilities import StudentUtilities, db

# Subpage UI & Controller imports
from app_ui.student_ui.ui_student_dashboard import Ui_StudentDashboard

# # not finished yet
# from app_ui.student_ui.submenus_ui.ui_profile import Ui_Profile

from app_ui.student_ui.submenus_ui.ui_current_schedule import Ui_CurrentSchedule
from student.submenus.class_current_schedule import CurrentScheduleWidget

from app_ui.student_ui.submenus_ui.ui_register_courses import Ui_RegisterCourses
from student.submenus.class_register_courses import RegisterCoursesWidget

from app_ui.student_ui.submenus_ui.ui_transcript import Ui_Transcript
from student.submenus.class_transcript import TranscriptWidget

# CANT TEST THIS CLASS IN HERE UNLESS WE HAVE THE REQUIRED INFORMATION FROM USERS

class StudentDashboard(QtWidgets.QMainWindow):
    """
    Main admin dashboard window.
    Handles page switching via a QStackedWidget and initializes all sub-pages.
    """
    
    def __init__(self, db, user: tuple):
        super().__init__()

        # -------------------------------
        # Main UI setup
        # -------------------------------
        self.ui = Ui_StudentDashboard()
        self.ui.setupUi(self)
        self.db = db
        self.user_id, self.name, self.email, self.program, self.state, self.account_status, self.hashed_pw = user
        self.student = StudentUtilities(self.db, self.user_id)

        self.ui.labelStudentName.setText(self.name)
        # ------------------------
        # 1. Initialize all pages
        # ------------------------
        self.init_sub_pages()

        # ------------------------
        # 2. Add pages to stacked widget
        # ------------------------
        # self.ui.stackedWidget.addWidget(self.profile_page)
        self.ui.stackedWidget.addWidget(self.current_schedule_page)
        self.ui.stackedWidget.addWidget(self.register_courses_page)
        self.ui.stackedWidget.addWidget(self.transcript_page)

        # Add other pages similarly...


        # -------------------------------
        # 3- Map buttons to their corresponding pages
        # -------------------------------

        # Key: QPushButton object
        # Value: Tuple of (page name string, QWidget page)
        # Using a string here avoids printing emojis/unicode directly from button.text()
        self.page_mapping = {
            self.ui.buttonProfile: ("Profile", self.current_schedule_page),
            self.ui.buttonCurrentSchedule: ("Current Schedule", self.current_schedule_page),
            self.ui.buttonRegisterCourses: ("Manage Courses", self.register_courses_page),
            self.ui.buttonTranscript: ("Transcript", self.transcript_page),
        }

        # Connect buttons to page-switching logic
        for button in self.page_mapping.keys():
            button.clicked.connect(lambda checked, b=button: self.switch_to_page(b))

        # Show default page (should be profile first)
        self.switch_to_page(self.ui.buttonProfile)
        # Disable manage faculty button do to it not being implemented yet

    # -------------------------------
    # Initialize all sub-pages
    # -------------------------------
    def init_sub_pages(self):
        """
        Create QWidget pages, set up their UI, and attach controllers.
        Controllers must be initialized AFTER widget + UI exist.
        """
        # # -------------------------------
        # # Profile page
        # # -------------------------------
        # self.profile_page = QtWidgets.QWidget()
        # self.profile_page_ui = Ui_Profile()
        # self.profile_page_ui.setupUi(self.profile_page)

        # -------------------------------
        # Current Sched page
        # -------------------------------
        # this page sets up its own ui internally.
        self.current_schedule_page = CurrentScheduleWidget(self.user_id)
        self.ui.stackedWidget.addWidget(self.current_schedule_page)

        # -------------------------------
        # Register Courses page
        # -------------------------------
        # this page sets up its own ui internally.

        self.register_courses_page = RegisterCoursesWidget(self.user_id, semester=None)
        self.ui.stackedWidget.addWidget(self.register_courses_page)

        # # -------------------------------
        # # Transcript courses
        # # -------------------------------
        # this page sets up its own ui internally.
        self.transcript_page = TranscriptWidget(self.user_id)
        self.ui.stackedWidget.addWidget(self.transcript_page)


    # -------------------------------
    # Switch the stacked widget to the page associated with the clicked button
    # -------------------------------
    def switch_to_page(self, button):
        # Retrieve the mapping info for the clicked button
        info = self.page_mapping.get(button)
        if info:
            # Unpack the tuple into a readable name and the actual QWidget page
            name, page = info
            
            # Set the stacked widget to display the selected page
            self.ui.stackedWidget.setCurrentWidget(page)
            
            # Optional debug: safely print the human-readable name of the page
            print(f"Switched to page: {name}")

# # ------------------------------- MAIN APP -------------------------------
# if __name__ == "__main__":
#     app = QtWidgets.QApplication(sys.argv)

#     student_id = 7500003
#     window = StudentDashboard(db, user_id)
#     window.show()
#     sys.exit(app.exec())
