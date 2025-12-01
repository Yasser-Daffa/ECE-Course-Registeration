
from StudentClass import AdminRegistration

db = Database(con, cur)


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
    def admin_add_section(self):
        # نستعرض المواد
        courses = self.db.list_courses()
        for code, name, credits in courses:
            print(code, name)
        # نحدد المادة اللي نبغا نسوي لها سكاشن
        course_code = input("Enter course code for the sections: ")
        # عدد السكاشن اللي ابغا اسويها
        count = int(input("How many sections do you want to add for this course? "))

        # نسوي لوب بحيث لو دخل انه يبغا 3 شعب اللوب يصير ثلاث دورات عشان بكل دوره ندخل معلومات الشعبه
        for i in range(count):

            doctor_id = input(
                "Enter doctor user_id (or press Enter for none): ").strip()  # رح نحذفه وقت ما نسوي ال gui
            if doctor_id:
                doctor_id = int(doctor_id)

            else:
                doctor_id = None

            days = input("Enter lecture days ").strip()  # رح نحذفه وقت ما نسوي ال gui
            time_start = input("Enter start time  ").strip()  # رح نحذفه وقت ما نسوي ال gui
            time_end = input("Enter end time  ").strip()  # رح نحذفه وقت ما نسوي ال gui
            room = input("Enter room  ").strip()  # رح نحذفه وقت ما نسوي ال gui
            capacity = int(input("Enter capacity: ").strip())  # رح نحذفه وقت ما نسوي ال gui
            semester = input("Enter semester  ").strip()  # رح نحذفه وقت ما نسوي ال gui
            msg = self.db.add_section(
                course_code=course_code,
                doctor_id=doctor_id,
                days=days,
                time_start=time_start,
                time_end=time_end,
                room=room,
                capacity=capacity,
                semester=semester,
                state="open")
            print(msg)

    def admin_list_sections(self):
        # اذا يبغا يشوف شعب مادة معينه يكتبها واذا يبغا يشوف شعب كل المواد يسيبه فاضي
        course_code = input(
            "Filter by course code (or press Enter for all): ").strip()  # رح نحذفه وقت ما نسوي ال gui
        # اذا يبغا يشوف شعب ترم معين يكتبه واذا يبغا يشوف شعب كل الاترام يسيبه فاضي
        semester = input("Filter by semester (or press Enter for all): ").strip()  # رح نحذفه وقت ما نسوي ال gui

        # هنا اذا خلاه فاضي رح يروح للجداول ويشيل معاه اني حطيته فاضي وفاضي ذا بالفعل يعتبر عدد او اوبجكت فا لازم نرجع نخليه none
        if course_code:

            course_code = course_code
        else:
            course_code = None
        if semester:

            semester = semester
        else:
            semester = None

        # هنا نروح ل فنكشن اللي تظهر شعب المواد
        rows = self.db.list_sections(course_code=course_code, semester=semester)
        # هنا نشوف اذا كان في شعب بالمادة اللي حددناها ولا مافي
        if not rows:
            print("No sections found.")
            return

        for (section_id, course_code, doctor_id, days, time_start, time_end, room, capacity, enrolled, semester,
             state) in rows:
            print(
                f"ID:{section_id} | "
                f"{course_code} | "
                f"Doc:{doctor_id} | "
                f"{days} {time_start}-{time_end} | "
                f"Room:{room} | "
                f"{enrolled}/{capacity} | "
                f"Sem:{semester} | "
                f"State:{state}")

    def admin_update_section(self):

        # نجيب كل الشعب بدون فلترة
        rows = self.db.list_sections()

        if not rows:
            print("No sections found.")
            return

        for (section_id, course_code, doctor_id, days, time_start, time_end, room, capacity, enrolled, semester,
             state) in rows:
            print(
                f"ID:{section_id} | "
                f"{course_code} | "
                f"Doc:{doctor_id} | "
                f"{days} {time_start}-{time_end} | "
                f"Room:{room} | "
                f"{enrolled}/{capacity} | "
                f"Sem:{semester} | "
                f"State:{state}"
            )

        # نطلب من الأدمن يختار رقم الشعبة
        section_id = input("Enter section ID to update: ").strip()  # رح نحذفه وقت ما نسوي ال gui
        section_id = int(section_id)

        # نسأل وش الأشياء اللي يبغى يغيّرها
        change_doc = input("Change doctor? (yes/no): ").strip().lower() == 'yes'  # رح نحذفه وقت ما نسوي ال gui
        change_days = input("Change days? (yes/no): ").strip().lower() == 'yes'
        change_start = input(
            "Change start time? (yes/no): ").strip().lower() == 'yes'  # رح نحذفه وقت ما نسوي ال gui
        change_end = input("Change end time? (yes/no): ").strip().lower() == 'yes'  # رح نحذفه وقت ما نسوي ال gui
        change_room = input("Change room? (yes/no): ").strip().lower() == 'yes'  # رح نحذفه وقت ما نسوي ال gui
        change_cap = input("Change capacity? (yes/no): ").strip().lower() == 'yes'  # رح نحذفه وقت ما نسوي ال gui
        change_sem = input("Change semester? (yes/no): ").strip().lower() == 'yes'  # رح نحذفه وقت ما نسوي ال gui
        change_state = input(
            "Change state (open/closed)? (yes/no): ").strip().lower() == 'yes'  # رح نحذفه وقت ما نسوي ال gui

        # القيم الجديدة (None = ما نغيّره)
        new_doctor_id = None
        new_days = None
        new_start = None
        new_end = None
        new_room = None
        new_capacity = None
        new_semester = None
        new_state = None

        if change_doc:
            doc_input = input(
                "New doctor user_id (or press Enter for none): ").strip()  # رح نحذفه وقت ما نسوي ال gui
            if doc_input:
                new_doctor_id = int(doc_input)
            else:
                new_doctor_id = None

        if change_days:
            new_days = input("New days ").strip()  # رح نحذفه وقت ما نسوي ال gui

        if change_start:
            new_start = input("New start time ").strip()  # رح نحذفه وقت ما نسوي ال gui

        if change_end:
            new_end = input("New end time ").strip()  # رح نحذفه وقت ما نسوي ال gui

        if change_room:
            new_room = input("New room ").strip()  # رح نحذفه وقت ما نسوي ال gui

        if change_cap:
            new_capacity = int(input("New capacity: ").strip())  # رح نحذفه وقت ما نسوي ال gui

        if change_sem:
            new_semester = input("New semester ").strip()  # رح نحذفه وقت ما نسوي ال gui

        if change_state:
            new_state = input("New state ").strip()  # رح نحذفه وقت ما نسوي ال gui

        # نستدعي دالة الداتا بيس
        msg = self.db.update_section(
            section_id=section_id,
            doctor_id=new_doctor_id,
            days=new_days,
            time_start=new_start,
            time_end=new_end,
            room=new_room,
            capacity=new_capacity,
            semester=new_semester,
            state=new_state)

        print(msg)



    def admin_delete_section(self):
        rows = self.db.list_sections()

        if not rows:
            print("No sections found.")
            return

        for (section_id, course_code, doctor_id, days, time_start,
             time_end, room, capacity, enrolled, semester, state) in rows:
            print(
                f"ID:{section_id} | "
                f"{course_code} | "
                f"Doc:{doctor_id} | "
                f"{days} {time_start}-{time_end} | "
                f"Room:{room} | "
                f"{enrolled}/{capacity} | "
                f"Sem:{semester} | "
                f"State:{state}")

        section_id = input("\nEnter section ID to delete: ").strip()
        if not section_id:
            print("No section ID entered.")
            return

        section_id = int(section_id)

        msg = self.db.delete_section(section_id)
        print(msg)

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


admin = Admin(db)
