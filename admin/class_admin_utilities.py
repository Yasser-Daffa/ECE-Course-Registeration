
from helper_files.shared_utilities import EmailSender

from database_files.initialize_database import initialize_database
from database_files.class_database_uitlities import DatabaseUtilities

con, cur = initialize_database("university_database.db")
db = DatabaseUtilities(con, cur)


class AdminUtilities:
    def __init__(self, db):
        self.db = db
        self.email_sender = EmailSender()

    # ========================= ADD COURSE =========================
    def add_course(self, code: str, name: str, credits: int) -> str:
        """
        Adds a new course to the database.
        Returns: message string from DB layer.
        """
        msg = self.db.AddCourse(code, name, credits)
        return msg

    # ========================= UPDATE COURSE =========================
    def update_course(
        self,
        current_code: str,
        new_code: str | None = None,
        new_name: str | None = None,
        new_credits: int | None = None
    ) -> str:
        """
        Updates an existing course based on provided new fields.
        Returns: message from DB layer.
        """
        msg = self.db.UpdateCourse(
            current_code=current_code,
            new_code=new_code,
            new_name=new_name,
            new_credits=new_credits
        )
        return msg

    # ========================= DELETE COURSE =========================
    def delete_course(self, code: str) -> str:
        """
        Deletes a course by code.
        Returns: message from DB layer.
        """
        msg = self.db.DeleteCourse(code)
        return msg

    # ========================= LIST COURSES =========================
    def list_courses(self):
        """
        Returns a list of courses: (code, name, credits)
        """
        return self.db.ListCourses()
    # ***************************************************************************************************


admin = AdminUtilities(db)