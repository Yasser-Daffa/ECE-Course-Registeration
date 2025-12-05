import sqlite3

con = sqlite3.connect("../../university_database.db")
cur = con.cursor()
cur.execute("PRAGMA foreign_keys = ON;")

class DatabaseUtilities:

    def __init__(self, con, cur):
        self.con = con
        self.cur = cur

    def commit(self):
        """حفظ التغييرات في قاعدة البيانات."""
        self.con.commit()
    
    # Query execution & fetching
    def fetchone(self, query, params=()):
        self.cur.execute(query, params)
        return self.cur.fetchone()

    def fetchall(self, query, params=()):
        self.cur.execute(query, params)
        return self.cur.fetchall()

    # Insert/Update/Delete with commit
    def execute(self, query, params=()):
        self.cur.execute(query, params)
        self.con.commit()


    def AddCourse(self, code, name, credits):
        """             #math 110   #dddd    -3
        تضيف مادة جديدة إلى قاعدة البيانات.

        المعاملات:
        - code: رمز المادة (مثال: 'EE101')
        - name: اسم المادة (مثال: 'الدوائر الكهربائية 1')
        - credits: عدد الساعات المعتمدة (مثال: 3)
        """
        # إدخال المادة الجديدة في جدول المواد
        try:
            self.cur.execute(
                "INSERT INTO courses(code, name, credits) VALUES(?, ?, ?)",
                (code, name, credits))
            self.commit()
            return "Course added successfully"
        except sqlite3.IntegrityError:
            return "course already added"

    def UpdateCourse(self, current_code, new_code=None, new_name=None, new_credits=None):
        """
    يا الشيخ، أول شي: **راح ندور على المادة باستخدام كودها الحالي**.
    هذا عشان لو كان الكود غلط ولا قديم، نقدر نلقاها ونعدّل الكود حقها ونزبطه.

    بعد ما نلقاها، حطّ القيمة الجديدة اللي تبي تغيّرها، واستخدم المتغيرات هذي:

    * **new_code:** لو تبي تغيّر **رمز** المادة (الكود).
    * **new_name:** لو تبي تغيّر **اسم** المادة.
    * **new_credits:** لو تبي تغيّر **عدد الساعات** المعتمدة.

    **واللي ما تبي تلمسه أو تعدّله، خليه فاضي وحط بداله `None`.**
    (عشان لا نخرب شي ما نبيه يتغيّر!)
    """
        if new_code is None and new_name is None and new_credits is None:
            return "Nothing to update"

        sets, vals = [], []

        if new_code is not None:
            sets.append("code=?")
            vals.append(new_code)

        if new_name is not None:
            sets.append("name=?")
            vals.append(new_name)

        if new_credits is not None:
            sets.append("credits=?")
            vals.append(new_credits)

        vals.append(current_code)

        self.cur.execute(f"UPDATE courses SET {', '.join(sets)} WHERE code=?", vals)
        self.commit()

        return "Course updated successfully"

    def ListCourses(self):
        """ترجع قائمة بجميع المواد (الكود، الاسم، الساعات)."""
        # نسترجع كل المواد من جدول , نرتبها تصاعدياً من الاقل الى الاعلى courses حسب الكود
        self.cur.execute("SELECT code, name, credits FROM courses ORDER BY code")
        return self.cur.fetchall()  # (list)نرجع النتايج كقائمة من الصفوف او تقدر تقول ترجع النتائج ك

    def DeleteCourse(self, code):
        """تحذف مادة باستخدام كودها."""
        self.cur.execute("DELETE FROM courses WHERE code=?", (code,))
        self.commit()  # نحفظ التغييرات في قاعدة البيانات

        return "Course deleted successfully"

    # *********************************************************************************
    def list_prerequisites(self, course_code):
        """Return a list of prerequisite codes for a given course."""
        self.cur.execute(
            "SELECT prereq_code FROM requires WHERE course_code=? ORDER BY prereq_code",
            (course_code,)
        )
        return [t[0] for t in self.cur.fetchall()]  # flatten tuples

    def add_prerequisite(self, course_code, prereq_code):

        try:
            self.cur.execute("INSERT INTO requires(course_code, prereq_code) VALUES(?, ?)", (course_code, prereq_code))
            self.commit()
            return "Prerequisite added successfully"

        except sqlite3.IntegrityError:
            return "Error: prerequisite already exists"

    # 9/14


    def update_prerequisite(self, course_code, old_prereq, new_prereq):
        """Update a prerequisite code for a course."""
        self.cur.execute(
            "UPDATE requires SET prereq_code=? WHERE course_code=? AND prereq_code=?",
            (new_prereq, course_code, old_prereq)
        )
        self.commit()
        return "Prerequisite updated successfully"

    def delete_prerequisite(self, course_code, prereq_code):
        """Delete a specific prerequisite from a course."""
        self.cur.execute(
            "DELETE FROM requires WHERE course_code=? AND prereq_code=?",
            (course_code, prereq_code)
        )
        self.commit()
        return "Prerequisite deleted successfully"
    #********************************************************************************************************************

    def add_section(self, course_code, doctor_id, days, time_start, time_end, room, capacity, semester, state="open"):

        self.cur.execute("""
            INSERT INTO sections(course_code,doctor_id,days,time_start,time_end,room,capacity,enrolled,semester,state)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?)""",
                (course_code,doctor_id,days,time_start,time_end,room,capacity,semester,state))
        self.commit()
        return "Section added successfully"


    def list_sections(self, course_code=None, semester=None):

        sql = """
        SELECT section_id,course_code,doctor_id,days,time_start,time_end,room,capacity,enrolled,semester,state
        FROM sections
        """

        # وش فايدتها ذي بالضبط؟ نحنا ما نعرف هل المستخدم دخل انه يبغا يشوف شعب سمستر او لا فا تكون فاضيه حاليا
        params = []

        # نفس فوق بس الفرق هنا اسم المتغير نفسه لانه ديفول معرف ب none ا لو الادمن عرف المتغير رح نضيفه هنا
        conds = []

        # لو المستخدم حدد مادة معينة
        if course_code is not None:
            conds.append("course_code = ?")
            params.append(course_code)

        # لو المستخدم حدد ترم معين
        if semester is not None:
            conds.append("semester = ?")
            params.append(semester)

        # هنا يقلك انه اذا كان الكوندشنز مو فارغ رح نظيف where معه لان ذي الكلمه هي جزء من سينتاكس ال sql اللي تسوي الشروط
        if conds:
            sql += " where " + " and ".join(conds)

        # ترتيب الناتج
        sql += " ORDER BY course_code, section_id"
        # شكل النتائج بيطلع كذا اذا تحقق الشروط اللي فوق SELECT * FROM sections WHERE course_code = ? AND semester = ? ORDER BY course_code, section_id
        # تنفيذ الاستعلام
        self.cur.execute(sql, params)

        # إعادة النتائج
        return self.cur.fetchall()

    def update_section(self,section_id,doctor_id=None,days=None,time_start=None,
                      time_end=None,room=None,capacity=None,semester=None,state=None):
        sets = [] #نفس فكرة اللي فوق نحنا حاليا ما نعرف المستخدم وش بيعدل بالضبط فا بنعبي ذا المتغير حسب هو وش اختار يعدل
        vals = [] # نفسه بس هنا نحفظ الارقام

        if doctor_id is not None:
            sets.append("doctor_id=?")
            vals.append(doctor_id)

        if days is not None:
            sets.append("days=?")
            vals.append(days)

        if time_start is not None:
            sets.append("time_start=?")
            vals.append(time_start)

        if time_end is not None:
            sets.append("time_end=?")
            vals.append(time_end)

        if room is not None:
            sets.append("room=?")
            vals.append(room)

        if capacity is not None:
            sets.append("capacity=?")
            vals.append(capacity)

        if semester is not None:
            sets.append("semester=?")
            vals.append(semester)

        if state is not None:
            sets.append("state=?")
            vals.append(state)

        # لو ما فيه أي شيء نعدله
        if not sets:
            return "Nothing to update"

        # نضيف section_id لآخر القيم عشان شرط الـ WHERE
        vals.append(section_id)

        sql = f"UPDATE sections SET {', '.join(sets)} WHERE section_id=?"
        self.cur.execute(sql, vals)
        self.commit()

        return "Section updated successfully" if self.cur.rowcount else "Section not found"

    def delete_section(self, section_id):


        self.cur.execute("DELETE FROM sections WHERE section_id=?", (section_id,))
        self.commit()

        return "Section deleted successfully" if self.cur.rowcount else "Section not found"

    # *********************************************************************************************************
    def add_users(self, name, email, password, program, state):
        try:
            self.cur.execute("""
                INSERT INTO users(name, email, password_h, program, state, account_status)
                VALUES(?,?,?,?,?, 'inactive')""", (name, email, password, program, state))
            self.commit()
            return "User added successfully, please wait for final acceptance"
        except sqlite3.IntegrityError:
            return "email already exists"

    def list_users(self):
        self.cur.execute("""SELECT user_id, name, email, program, state, account_status FROM users""")
        return self.cur.fetchall()

    def update_user(self, user_id, name=None, email=None,
                    program=None, password=None, account_status=None):

        sets = []
        vals = []

        if name is not None:
            sets.append("name=?")
            vals.append(name)

        if email is not None:
            sets.append("email=?")
            vals.append(email)

        if program is not None:
            sets.append("program=?")
            vals.append(program)

        if password is not None:
            sets.append("password_h=?")
            vals.append(password)

        if account_status is not None:
            sets.append("account_status=?")
            vals.append(account_status)

        if not sets:
            return "Nothing to update"

        vals.append(user_id)

        sql = f"UPDATE users SET {', '.join(sets)} WHERE user_id=?"
        self.cur.execute(sql, vals)
        self.commit()

        return "User updated successfully"

    def user_login(self, user_id, password_h):
        self.cur.execute("""
            SELECT user_id, name, email, program, state, account_status
            FROM users
            WHERE user_id=? AND password_h=?
        """, (user_id, password_h))

        return self.cur.fetchone()

    def get_user_by_id(self, user_id):

        self.cur.execute("""
            SELECT user_id, name, email, program, state, account_status
            FROM users
            WHERE user_id=?
        """, (user_id,))
        return self.cur.fetchone()

    def reset_password_with_email(self, user_id, email, new_password):

        self.cur.execute("""
            UPDATE users SET password_h=? WHERE user_id=? AND email=?
        """, (new_password, user_id, email))

        if self.cur.rowcount == 0:
            return "Error: ID or email is incorrect"

        self.commit()
        return "Password reset successfully"
    
    def get_user_by_login(self, login_input):
        self.cur.execute("""
            SELECT user_id, name, email, program, state, account_status, password_h
            FROM users
            WHERE email=? OR user_id=?
        """, (login_input, login_input))
        return self.cur.fetchone()
    
    def check_email_exists(self, email: str) -> bool:
        """Check if an email already exists in the users table."""

        self.cur.execute("SELECT 1 FROM users WHERE LOWER(email) = LOWER(?) LIMIT 1", (email,))
        return self.cur.fetchone() is not None

    #*********************************************************************************************************

    def add_transcript(self, student_id, course_code, semester, grade=None):
        try:
            self.cur.execute("""INSERT INTO transcripts(student_id, course_code, semester, grade) VALUES (?, ?, ?, ?)
            """, (student_id, course_code, semester, grade))
            self.commit()
            return "transcript record added successfully"
        except sqlite3.IntegrityError:
            return " this course/semester is already in transcript for this student"

    def list_transcript(self, student_id):

        self.cur.execute("""
            SELECT course_code, semester, grade
            FROM transcripts
            WHERE student_id = ?
            ORDER BY semester, course_code
        """, (student_id,))
        return self.cur.fetchall()

    def update_transcript_grade(self, student_id, course_code, semester, new_grade):
        """
        تعدل الدرجة فقط لمادة معيّنة في سمستر معين
        """
        self.cur.execute("""
            UPDATE transcripts
            SET grade = ?
            WHERE student_id = ? AND course_code = ? AND semester = ?
        """, (new_grade, student_id, course_code, semester))

        if self.cur.rowcount == 0:
            self.commit()
            return "Transcript record not found"
        self.commit()
        return "Grade updated successfully"


    def add_course_to_plan(self, program, course_code, level):
        try:
            self.cur.execute("""
                INSERT INTO program_plans(program, course_code, level)
                VALUES (?, ?, ?)
            """, (program, course_code, level))
            self.commit()
            return "Course added to plan successfully"
        except sqlite3.IntegrityError:
            return "This course is already in this plan"

    def delete_course_from_plan(self, program, course_code):
        self.cur.execute("""
            DELETE FROM program_plans
            WHERE program=? AND course_code=?
        """, (program, course_code))

        self.commit()

        if self.cur.rowcount > 0:
            return " Course removed from plan successfully"
        return " Course not found in this plan"

    def update_course_in_plan(self,
                              old_program,
                              old_course_code,
                              old_level,
                              new_program,
                              new_course_code,
                              new_level):
        """
        تعدّل سطر واحد في program_plans:
        من (old_program, old_course_code, old_level)
        إلى (new_program, new_course_code, new_level)
        NOTE:
        نستخدم البرنامج والكود فقط في WHERE عشان نضمن انه يلقاه
        """

        # نطبعهم بصيغة موحّدة عشان ما نتعلق في مسافات / كابتل / سمول
        old_program = (old_program or "").strip().upper()
        old_course_code = (old_course_code or "").strip().upper()
        new_program = (new_program or "").strip().upper()
        new_course_code = (new_course_code or "").strip().upper()

        try:
            # نحدّث الصف بناءً على (program, course_code) فقط
            self.cur.execute("""
                UPDATE program_plans
                SET program = ?, course_code = ?, level = ?
                WHERE UPPER(program) = ? AND UPPER(course_code) = ?
            """, (
                new_program,
                new_course_code,
                new_level,
                old_program,
                old_course_code,
            ))

            if self.cur.rowcount == 0:
                # يعني ما لقى ولا صف بهذي التركيبة
                self.commit()
                return "✗ Course not found in this plan"

            self.commit()
            return "✓ Course in plan updated successfully"

        except sqlite3.IntegrityError:
            # محاولة تكرار نفس الكورس بنفس الليفل مرتين في نفس الخطة
            return "This course (with this level) is already in this plan"

    def list_plan_courses(self, program=None):
        if program is None:
            self.cur.execute("""
                SELECT p.program, c.code, c.name, c.credits, p.level
                FROM program_plans p
                JOIN courses c ON p.course_code = c.code
                ORDER BY p.program, p.level, c.code
            """)
        else:
            self.cur.execute("""
                SELECT p.program, c.code, c.name, c.credits, p.level
                FROM program_plans p
                JOIN courses c ON p.course_code = c.code
                WHERE p.program=?
                ORDER BY p.level, c.code
            """, (program,))

        return self.cur.fetchall()
    
    # student dealings

    def list_student_registrations(self, student_id, semester=None):
        """
        Return list of sections the student is registered in.
        Each item: section_id, course_code, semester, ...
        """
        sections = self.list_sections(semester=semester)  # get all sections or filtered by semester
        registrations = []
        for sec in sections:
            sec_id = sec[0]  # section_id
            # Check if student is registered in this section
            self.cur.execute("SELECT 1 FROM registrations WHERE student_id=? AND section_id=?", (student_id, sec_id))
            if self.cur.fetchone():
                registrations.append(sec)
        return registrations
    
    def is_student_registered(self, student_id, section_id, semester):
        """
        يتأكد هل الطالب مسجل في هذا السكشن في هذا السمستر.
        نستخدم section_id + semester عشان لو نفس السكشن تكرر مستقبلاً بسمستر ثاني
        يكون كل واحد له رقم مختلف أصلاً.
        """
        self.cur.execute(
            """
            SELECT 1 FROM registrations
            WHERE student_id = ? AND section_id = ? AND semester = ?
            """,
            (student_id, section_id, semester)
        )
        return self.cur.fetchone() is not None

    

    def register_student_to_section(self, student_id: int, section_id: int,
                                    course_code: str, semester: str) -> bool:
        """
        تسجيل طالب في سكشن معيّن في سمستر معيّن.

        - يمنع التسجيل المكرر لنفس (student_id, course_code, semester)
          بسبب الـ PRIMARY KEY في جدول registrations.
        """
        try:
            cur = self.con.cursor()

            # نتأكد أولاً إنه مو مسجل نفس الكورس في نفس السمستر
            cur.execute(
                """
                SELECT 1 FROM registrations
                WHERE student_id = ? AND course_code = ? AND semester = ?
                """,
                (student_id, course_code, semester)
            )
            if cur.fetchone():
                # مسجل مسبقاً في نفس الكورس ونفس السمستر
                return False

            # ندخل الصف الجديد
            cur.execute(
                """
                INSERT INTO registrations (student_id, section_id, course_code, semester)
                VALUES (?, ?, ?, ?)
                """,
                (student_id, section_id, course_code, semester)
            )
            self.con.commit()
            return True

        except Exception as e:
            print(f"DB Error in register_student_to_section: {e}")
            return False

        
    # ------------------- Remove student registration -------------------
    def remove_student_registration(self, student_id: int, course_code: str) -> bool:
        """
        Deletes a student's registration for a specific course.
        Returns True if a row was deleted, False otherwise.
        """
        try:
            # Get all section_ids for this course that the student is registered in
            self.cur.execute(
                "SELECT section_id FROM registrations "
                "WHERE student_id = ? AND course_code = ?",
                (student_id, course_code)
            )
            rows = self.cur.fetchall()
            if not rows:
                return False  # student not registered for this course

            # Delete all registrations for this course (usually only one per course)
            section_ids = [r[0] for r in rows]
            self.cur.execute(
                f"DELETE FROM registrations WHERE student_id = ? AND section_id IN ({','.join(['?']*len(section_ids))})",
                [student_id, *section_ids]
            )
            self.con.commit()
            return True
        except Exception as e:
            print(f"[ERROR] remove_student_registration failed: {e}")
            return False



