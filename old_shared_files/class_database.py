import sqlite3

con = sqlite3.connect("university.db")
cur = con.cursor()
cur.execute("PRAGMA foreign_keys = ON;")

class Database:

    def __init__(self, con, cur):
        self.con = con
        self.cur = cur

    def commit(self):
        """حفظ التغييرات في قاعدة البيانات."""
        self.con.commit()

    def AddCourse(self, code, name, credits):
        """
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
    def ListRequires(self, course_code):
        self.cur.execute(
            "select prereq_code from requires where course_code = ? order by prereq_code", (course_code,))
        return self.cur.fetchall()

    def AddPrerequisite(self, course_code, prereq_code):

        try:
            self.cur.execute("INSERT INTO requires(course_code, prereq_code) VALUES(?, ?)", (course_code, prereq_code))
            self.commit()
            return "Prerequisite added successfully"

        except sqlite3.IntegrityError:
            return "Error: prerequisite already exists"

    # 9/14

    def UpdateRequires(self, course_code, old_prereq, new_prereq):
        """ يعدّل شرطًا مسبقًا (Prerequisite) لمادة معينة.
             المعاملات:
             - course_code : كود المادة الأساسية (مثال: 'EE201')
             - old_prereq  : المادة المسبق القديم الذي نريد تغييره
             - new_prereq  : المادة المسبق الجديد الذي نريد وضعه بدلاً من القديم """

        # نغيّر الـ prereq_code من old_prereq → new_prereq
        # بشرط أن يكون السطر تابعًا لنفس course_code
        self.cur.execute("UPDATE requires SET prereq_code=? WHERE course_code=? AND prereq_code=?",
                         (new_prereq, course_code, old_prereq))
        self.commit()
        return "Prerequisite updated successfully"

    def DeleteRequires(self, course_code, prereq_code):
        """ يحذف شرطًا مسبقًا (Prerequisite) محدد لمادة معينة.
        المعاملات:
        - course_code: كود المادة الأساسية (مثال: EE201)
        - prereq_code: كود المادة المطلوبة كشرط مسبق (مثال: EE101)
        """
        # تنفيذ أمر الحذف باستخدام الشرطين:
        # 1) course_code  → المادة نفسها
        # 2) prereq_code  → المادة المطلوبة كـ prerequisite

        self.cur.execute("DELETE FROM requires WHERE course_code=? AND prereq_code=?", (course_code, prereq_code))
        self.commit()
        return "Prerequisite deleted successfully"
    #********************************************************************************************************************

    def AddSection(self, course_code, doctor_id, days, time_start, time_end, room, capacity, semester, state="open"):

        self.cur.execute("""
            INSERT INTO sections(course_code,doctor_id,days,time_start,time_end,room,capacity,enrolled,semester,state)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?)""",
                (course_code,doctor_id,days,time_start,time_end,room,capacity,semester,state))
        self.commit()
        return "Section added successfully"


    def ListSections(self, course_code=None, semester=None):

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

    def UpdateSection(self,section_id,doctor_id=None,days=None,time_start=None,
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

        # لو ما فيه أي شيء نعدّله
        if not sets:
            return "Nothing to update"

        # نضيف section_id لآخر القيم عشان شرط الـ WHERE
        vals.append(section_id)

        sql = f"UPDATE sections SET {', '.join(sets)} WHERE section_id=?"
        self.cur.execute(sql, vals)
        self.commit()

        # rowcount = كم صف تأثّر (0 يعني ما لقينا الشعبة)
        return "Section updated successfully" if self.cur.rowcount else "Section not found"

    def DeleteSection(self, section_id):


        self.cur.execute("DELETE FROM sections WHERE section_id=?", (section_id,))
        self.commit()

        return "Section deleted successfully" if self.cur.rowcount else "Section not found"

db = Database(con, cur)

class Admin:
    def __init__(self, db):
        self.db = db

    def AdminUpdateCourse(self):
        current = input("Enter the course code to update: ").strip()

        change_code = input("Do you want to change the code? (yes/no): ").strip().lower() == 'yes'
        change_name = input("Do you want to change the name? (yes/no): ").strip().lower() == 'yes'
        change_credits = input("Do you want to change the credits? (yes/no): ").strip().lower() == 'yes'

        new_code = input("New code: ").strip() if change_code else None
        new_name = input("New name: ").strip() if change_name else None
        new_credits = int(input("New credits: ").strip()) if change_credits else None

        # نستدعي الدالة من كائن الداتا بيس عن طريق self.db
        msg = self.db.UpdateCourse(
            current_code=current,
            new_code=new_code,
            new_name=new_name,
            new_credits=new_credits
        )
        print(msg)

    def AdminAddCourse(self):
        """
        دالة خاصة بالمدير (الأدمن) لإضافة مادة جديدة.
        تطلب من الأدمن إدخال معلومات المادة، ثم تستدعي الدالة الخاصة بقاعدة البيانات.
        """
        # طلب بيانات المادة من الأدمن
        code = input("Enter course code: ").strip()
        name = input("Enter course name: ").strip()
        credits = int(input("Enter course credits: ").strip())
        # استدعاء الدالة الخاصة بقاعدة البيانات لإضافة المادة

        msg = self.db.AddCourse(code, name, credits)
        # طباعة النتيجة للمستخدم

        print(msg)

    def AdminDeleteCourses(self):
        '''يحذف المادة من القائمة'''
        # يعرض القائمة
        courses = self.db.ListCourses()
        print(courses)

        code = input("Enter course code to delete: ").strip()
        msg = self.db.DeleteCourse(code)  # يحذف المادة
        print(msg)

    # ***************************************************************************************************
    def AdminAddPrerequisite(self):
        courses = self.db.ListCourses()
        for code, name, credits in courses:
            print(code, name, credits)

        originalcourse = input("enter course code: ")
        tims = input("enter how many requires course for this course:")
        for i in range(int(tims)):
            requires = input("enter requires course code: ")
            m = self.db.AddPrerequisite(originalcourse, requires)
            print(m)

    def AdminListRequires(self):
        courses = self.db.ListCourses()
        for code, name, credits in courses:
            print(code, name, credits)

        course_code = input("Enter course code to show its prerequisites: ").strip()

        rows = self.db.ListRequires(course_code)

        if not rows:
            print("This course has no prerequisites.")
        else:
            print(f"Prerequisites for {course_code}:")
            for (prereq_code,) in rows:
                print("-", prereq_code)

    def AdminUpdateRequires(self):
        # نعرض كل المواد الموجودة عشان المستخدم يعرف الكود اللي يبغى يعدّل شروطه
        courses = self.db.ListCourses()
        for code, name, credits in courses:
            print(code, name, credits)

        # نطلب من المستخدم كود المادة اللي بيعدّل شروطها
        course_code = input("Enter course code: ").strip()

        # نعرض الشروط المسبقة الحالية للمادة
        print("\nCurrent prerequisites:")
        rows = self.db.ListRequires(course_code)
        for (r,) in rows:
            print("-", r)

        # نطلب من المستخدم الشرط القديم اللي يبغى يغيّره
        old = input("Enter old prerequisite to change: ").strip()

        # نطلب الشرط الجديد اللي بنحطّه بدل القديم
        new = input("Enter new prerequisite: ").strip()

        # نستخدم دالة قاعدة البيانات لتحديث الشرط
        msg = self.db.UpdateRequires(course_code, old, new)

        # نعرض النتيجة النهائية (نجحت/فشلت)
        print(msg)

    def AdminDeleteRequires(self):
        # أول شي: نعرض كل المواد عشان المستخدم يعرف الكود اللي يبغى يحذف منه
        courses = self.db.ListCourses()
        for code, name, credits in courses:
            print(code, name, credits)

        # نطلب من المستخدم كود المادة اللي نبي نحذف من شروطها المسبقة
        course_code = input("Enter course code: ").strip()

        # نجيب كل الـ prerequisites للمادة
        rows = self.db.ListRequires(course_code)

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
        msg = self.db.DeleteRequires(course_code, prereq)

        # نعرض النتيجة
        print(msg)

    # *****************************************************************************************************************
    def AdminAddSection(self):
        # نستعرض المواد
        courses = self.db.ListCourses()
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
            msg = self.db.AddSection(
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

    def AdminListSections(self):
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
        rows = self.db.ListSections(course_code=course_code, semester=semester)
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

    def AdminUpdateSection(self):

        # نجيب كل الشعب بدون فلترة
        rows = self.db.ListSections()

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
        msg = self.db.UpdateSection(
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

    def AdminDeleteSection(self):
        rows = self.db.ListSections()

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

        msg = self.db.DeleteSection(section_id)
        print(msg)















