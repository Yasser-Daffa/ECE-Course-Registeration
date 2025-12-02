import os

from student.students_utilities import AdminRegistration

from database_files.initialize_database import initialize_database
from database_files.class_database_uitlities import DatabaseUtilities

# Make DB path absolute
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "../university_database.db"))

# Initialize database connection
con, cur = initialize_database(DB_PATH)
db = DatabaseUtilities(con, cur)



class AdminUtilities:

    def __init__(self, db):
        self.db = db


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
    def admin_add_prerequisite(self):
        courses = self.db.list_courses()
        for code, name, credits in courses:
            print(code, name, credits)

        originalcourse = input("enter course code: ")
        tims = input("enter how many requires course for this course:")
        for i in range(int(tims)):
            requires = input("enter requires course code: ")
            m = self.db.add_prerequisite(originalcourse, requires)
            print(m)

    def admin_list_requires(self):
        courses = self.db.list_courses()
        for code, name, credits in courses:
            print(code, name, credits)

        course_code = input("Enter course code to show its prerequisites: ").strip()

        rows = self.db.list_requires(course_code)

        if not rows:
            print("This course has no prerequisites.")
        else:
            print(f"Prerequisites for {course_code}:")
            for (prereq_code,) in rows:
                print("-", prereq_code)

    def admin_update_requires(self):
        # نعرض كل المواد الموجودة عشان المستخدم يعرف الكود اللي يبغى يعدّل شروطه
        courses = self.db.list_courses()
        for code, name, credits in courses:
            print(code, name, credits)

        # نطلب من المستخدم كود المادة اللي بيعدّل شروطها
        course_code = input("Enter course code: ").strip()

        # نعرض الشروط المسبقة الحالية للمادة
        print("\nCurrent prerequisites:")
        rows = self.db.list_requires(course_code)
        for (r,) in rows:
            print("-", r)

        # نطلب من المستخدم الشرط القديم اللي يبغى يغيّره
        old = input("Enter old prerequisite to change: ").strip()

        # نطلب الشرط الجديد اللي بنحطّه بدل القديم
        new = input("Enter new prerequisite: ").strip()

        # نستخدم دالة قاعدة البيانات لتحديث الشرط
        msg = self.db.update_requires(course_code, old, new)

        # نعرض النتيجة النهائية (نجحت/فشلت)
        print(msg)

    def admin_delete_requires(self):
        # أول شي: نعرض كل المواد عشان المستخدم يعرف الكود اللي يبغى يحذف منه
        courses = self.db.list_courses()
        for code, name, credits in courses:
            print(code, name, credits)

        # نطلب من المستخدم كود المادة اللي نبي نحذف من شروطها المسبقة
        course_code = input("Enter course code: ").strip()

        # نجيب كل الـ prerequisites للمادة
        rows = self.db.list_requires(course_code)

        # لو ما عندها أي شرط مسبق → نطلع رسالة ونوقف
        if not rows:
            print("This course has no prerequisites.")
            return

        # نعرض كل الشروط المسبقة حق المادة
        print("\nPrerequisites:")
        for (r,) in rows:
            print("-", r)

        # نطلب من المستخدم أي شرط مسبق يبغى يحذفه
        prereq = input("Enter prerequisite to delete: ").strip()

        # نحذف الشرط باستخدام دالة قاعدة البيانات
        msg = self.db.delete_requires(course_code, prereq)

        # نعرض النتيجة
        print(msg)

    # *****************************************************************************************************************
    def admin_add_section(self,
                          course_code,
                          count,
                          doctor_ids,
                          days_list,
                          start_times,
                          end_times,
                          rooms,
                          capacities,
                          semesters,
                          states):
        """
        نفس كودك الأصلي بالضبط لكن يستقبل
        قوائم (lists) بدل input لكل سكشن.

        مثال من الـ GUI:
        admin.admin_add_section(
            course_code="EE201",
            count=3,
            doctor_ids=[1, 2, None],
            days_list=["MW", "TR", "F"],
            start_times=["08:00", "10:00", "12:00"],
            end_times=["09:30", "11:30", "13:30"],
            rooms=["B12", "C33", "A20"],
            capacities=[40, 50, 35],
            semesters=["241", "241", "241"],
            states=["open", "open", "closed"]
        )
        """

        results = []

        for i in range(count):
            msg = self.db.add_section(
                course_code=course_code,
                doctor_id=doctor_ids[i],
                days=days_list[i],
                time_start=start_times[i],
                time_end=end_times[i],
                room=rooms[i],
                capacity=capacities[i],
                semester=semesters[i],
                state=states[i]
            )
            results.append(msg)

        return results

    def admin_list_sections(self, course_code=None, semester=None):
        rows = self.db.list_sections(course_code=course_code, semester=semester)

        if not rows:
            return "No sections found."

        return rows

    def admin_update_section(self,
                             section_id,
                             doctor_id=None,
                             days=None,
                             time_start=None,
                             time_end=None,
                             room=None,
                             capacity=None,
                             semester=None,
                             state=None):
        rows = self.db.list_sections()

        if not rows:
            return "No sections found."

        msg = self.db.update_section(
            section_id=section_id,
            doctor_id=doctor_id,
            days=days,
            time_start=time_start,
            time_end=time_end,
            room=room,
            capacity=capacity,
            semester=semester,
            state=state
        )

        return msg

    def admin_delete_section(self, section_id):
        rows = self.db.list_sections()

        if not rows:
            return "No sections found."

        msg = self.db.delete_section(section_id)
        return msg

    # ***************************************************************************************************************

    def admin_add_transcript(self):

        student_id = int(input("Enter student ID: ").strip())
        course_code = input("Enter course code: ").strip()
        semester = input("Enter semester ").strip()
        grade = input("Enter grade (or press Enter if not graded yet): ").strip()

        if grade == "":
            grade = None

        msg = self.db.add_transcript(student_id, course_code, semester, grade)
        print(msg)

    def admin_show_transcript(self):

        student_id = int(input("Enter student ID to show transcript: ").strip())

        rows = self.db.list_transcript(student_id)
        if not rows:
            print("No transcript records for this student.")  # هذا بيكون بكلاس الطالب
            return

        print(f"Transcript for student {student_id}:")
        for course_code, semester, grade in rows:
            print(f"{semester} | {course_code} | Grade: {grade}")

    def admin_update_transcript_grade(self):

        student_id = int(input("Enter student ID: ").strip())
        course_code = input("Enter course code: ").strip()
        semester = input("Enter semester (e.g. 2024-1): ").strip()
        new_grade = input("Enter new grade: ").strip()

        msg = self.db.update_transcript_grade(student_id, course_code, semester, new_grade)
        print(msg)

    def admin_add_course_to_plan(self):
        # نعرض كل المواد المتاحة
        courses = self.db.list_courses()
        print("Available courses:")
        for code, name, credits in courses:
            print(f"{code} - {name} ({credits} credits)")

        course_code = input("Enter course code to add to a plan: ").strip()

        # نفس البرامج المستخدمة في جدول users.program
        print("\nAvailable programs:")
        print("PWM  - Power & Machines Engineering")
        print("BIO  - Biomedical Engineering")
        print("COMM - Communications Engineering")
        print("COMP - Computer Engineering")

        program = input("Enter program code ('PWM','BIO','COMM','COMP'): ").strip().upper()
        level = int(input("Enter level number: ").strip())

        msg = self.db.add_course_to_plan(program, course_code, level)
        print(msg)

    def admin_delete_course_from_plan(self):
        program = input("Enter program code ('PWM','BIO','COMM','COMP'): ").strip().upper()
        rows = self.db.list_plan_courses(program)

        if not rows:
            print("This plan has no courses or does not exist.")
            return

        print(f"\nCourses in plan '{program}':")
        for prog, code, name, credits, level in rows:
            print(f"Level {level}: {code} - {name} ({credits} credits)")

        course_code = input("Enter course code to remove from this plan: ").strip()
        msg = self.db.delete_course_from_plan(program, course_code)
        print(msg)





    def admin_show_plans(self):
        """
        يعرض كل الخطط وكل المواد داخل كل خطة.
        """
        rows = self.db.list_plan_courses()  # نعرض كل الخطط

        if not rows:
            print("No plans found.")
            return

        current_program = None

        # كل صف يحتوي:
        # (program, course_code, course_name, credits, level)
        for program, code, name, credits, level in rows:

            # إذا تغيّر التخصص نبدأ عنوان جديد
            if program != current_program:
                current_program = program
                print(f"\n===== Plan: {program} =====")

            # نعرض المادة والمستوى
            print(f"Level {level}: {code} - {name} ({credits} credits)")



    # إدارة التسجيل
    def manage_registration_period(self):
        print("1. Open Registration")
        print("2. Close Registration")
        ch = input("Choose: ")
        sem = input("Enter Semester: ")
        if ch == '1':
            self.reg_manager.open_registration(sem)
        elif ch == '2':
            self.reg_manager.close_registration(sem)


admin = AdminUtilities(db)
def add_test_sections():
    # انتبه: لازم يكون في كورسات بهذي الأكواد في جدول courses
    sections_data = [
        {
            "course_code": "MATH101",
            "doctor_id": None,          # أو رقم دكتور موجود فعليًا
            "days": "MW",
            "time_start": "09:00",
            "time_end": "09:50",
            "room": "B15",
            "capacity": 40,
            "semester": "241",
            "state": "open",
        },
        {
            "course_code": "MATH101",
            "doctor_id": None,
            "days": "TTh",
            "time_start": "11:00",
            "time_end": "12:15",
            "room": "B16",
            "capacity": 45,
            "semester": "241",
            "state": "open",
        },
        {
            "course_code": "MATH1231",
            "doctor_id": None,
            "days": "MWF",
            "time_start": "13:00",
            "time_end": "13:50",
            "room": "C201",
            "capacity": 35,
            "semester": "241",
            "state": "closed",
        },
    ]

    for sec in sections_data:
        msg = db.add_section(
            sec["course_code"],
            sec["doctor_id"],
            sec["days"],
            sec["time_start"],
            sec["time_end"],
            sec["room"],
            sec["capacity"],
            sec["semester"],
            sec["state"],
        )
        print(sec["course_code"], "=>", msg)


if __name__ == "__main__":
    add_test_sections()
    print("✅ Done seeding test sections.")