import sqlite3

con = sqlite3.connect("university.db")
cur = con.cursor()


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



    #*********************************************************************************
    def ListRequires(self, course_code):
        self.cur.execute(
            "slect prereq_code from requires where course_code = ? order by prereq_code",(course_code,))
        return self.cur.fetchall()

    def AddPrerequisite(self, course_code, prereq_code):

        try:
            self.cur.execute("INSERT INTO requires(course_code, prereq_code) VALUES(?, ?)",(course_code, prereq_code))
            self.commit()
            return "Prerequisite added successfully"

        except sqlite3.IntegrityError:
            return "Error: prerequisite already exists"


    def UpdateRequires(self):







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

    #***************************************************************************************************
    def AdminAddPrerequisite(self):
        courses = self.db.ListCourses()
        for code, name, credits in courses:
            print(code, name, credits)

        originalcourse = input("enter course code: ")
        tims = input("enter how many requires course for this course:")
        for i in range(int(tims)):
            requires = input("enter requires course code: ")
            m= self.db.AddPrerequisite(originalcourse, requires)
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




