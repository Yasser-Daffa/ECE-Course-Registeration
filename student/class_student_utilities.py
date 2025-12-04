import os

# from student.class_students_utilities import AdminRegistration

from database_files.initialize_database import initialize_database
from database_files.class_database_uitlities import DatabaseUtilities

# Make DB path absolute
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "../university_database.db"))

# Initialize database connection
con, cur = initialize_database(DB_PATH)
db = DatabaseUtilities(con, cur)


class StudentUtilities:
    def __init__(self, db_util: DatabaseUtilities, student_id):
        self.db = db_util
        self.student_id = student_id

    # ================== Student info ==================
    def get_student_program(self):
        user = self.db.get_user_by_id(self.student_id)
        return user[3] if user else None  # index 3 is 'program'

    def get_completed_courses(self):
        transcripts = self.db.ListTranscript(self.student_id)
        return [course for course, _, grade in transcripts if grade is not None]

    def get_registered_courses(self, semester=None):
        sections = self.db.list_sections()
        registered = []
        for sec in sections:
            sec_id, course_code, *_ = sec
            if self.db.is_student_registered(self.student_id, sec_id) and (semester is None or sec[9] == semester):
                registered.append(course_code)
        return registered

    # ================== Available courses ==================
    def get_available_courses(self, semester):
        program = self.get_student_program()
        if not program:
            return []

        plan_courses = [code for code, in self.db.list_plan_courses(program)]
        completed = set(self.get_completed_courses())
        registered = set(self.get_registered_courses(semester))

        available = []
        course_info_list = self.db.ListCourses()
        for code in plan_courses:
            if code in completed or code in registered:
                continue

            course_info = next((c for c in course_info_list if c[0] == code), None)
            if not course_info:
                continue
            _, name, credits = course_info

            prereqs = self.db.list_prerequisites(code)
            missing_prereqs = [p for p in prereqs if p not in completed]
            can_register = len(missing_prereqs) == 0

            available.append({
                "course_code": code,
                "course_name": name,
                "credits": credits,
                "prereqs": prereqs,
                "missing_prereqs": missing_prereqs,
                "can_register": can_register
            })

        return available

    def show_available_courses(self, semester):
        courses = self.get_available_courses(semester)
        can = [c for c in courses if c["can_register"]]
        cannot = [c for c in courses if not c["can_register"]]

        print("\nAvailable courses for semester", semester)
        if can:
            print("\n✓ You can register these courses:")
            for c in can:
                print(f"  {c['course_code']} - {c['course_name']} ({c['credits']} credits)")

        if cannot:
            print("\n✗ You CANNOT register these courses (missing prerequisites):")
            for c in cannot:
                print(f"  {c['course_code']} - {c['course_name']}")
                print(f"    Missing: {', '.join(c['missing_prereqs'])}")

        return can

    # ================== Sections ==================
    # inside class StudentUtilities
    def get_all_sections(self):
        """
        Return all sections in a standardized dict format for the table.
        Safely parses enrolled/capacity and computes status.
        """
        sections = self.db.list_sections()  # fetch all sections from DB
        result = []

        for sec in sections:
            try:
                section_id = sec[0]
                course_code = sec[1]
                course_name = sec[2]
                instructor_name = sec[3]
                days = sec[4]
                start_time = sec[5]
                end_time = sec[6]
                room = sec[7]

                # enrolled and capacity might be invalid strings; cast safely
                try:
                    enrolled = int(sec[8])
                except (ValueError, TypeError):
                    enrolled = 0
                try:
                    capacity = int(sec[9])
                except (ValueError, TypeError, IndexError):
                    capacity = 0  # treat as unlimited if missing/invalid

                # status determination
                status_db = sec[10] if len(sec) > 10 else "Open"
                if status_db.lower() == "closed":
                    status = "Closed"
                elif capacity > 0 and enrolled >= capacity:
                    status = "Full"
                else:
                    status = "Open"

                schedule = f"{days or ''} {start_time or ''}-{end_time or ''} | {room or ''}".strip()

                result.append({
                    "id": section_id,
                    "course_code": course_code,
                    "name": course_name,
                    "instructor": instructor_name,
                    "schedule": schedule,
                    "enrolled": enrolled,
                    "capacity": capacity,
                    "status": status
                })
            except Exception as e:
                # Skip broken rows but log them
                print(f"Skipping invalid section row: {sec} -> {e}")
                continue

        return result



    def register_section(self, section_id: int) -> bool:
        return self.db.register_student_to_section(self.student_id, section_id)


    def get_sections_for_course(self, course_code, semester):
        return self.db.list_sections(course_code=course_code, semester=semester)

    def check_time_conflict(self, sec1, sec2):
        days1 = set(sec1["days"].upper().replace(" ", ""))
        days2 = set(sec2["days"].upper().replace(" ", ""))
        if not days1.intersection(days2):
            return False
        return sec1["time_start"] < sec2["time_end"] and sec2["time_start"] < sec1["time_end"]

    # ================== Transcript ==================
    def show_transcript(self):
        transcript = self.db.ListTranscript(self.student_id)
        print(f"\nTranscript for student {self.student_id}:")
        for course_code, semester, grade in transcript:
            print(f"  {semester} | {course_code} | {grade}")

