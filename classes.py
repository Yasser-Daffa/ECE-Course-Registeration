
import sqlite3

con = sqlite3.connect("university.db")
cur = con.cursor()
class Database:

    def __init__(self,con,cur):
        self.con=sqlite3.connect("university.db")
        self.cur = con.cursor()





    def AddCourse(self, code, name, credits):
        """
        تضيف مادة جديدة إلى قاعدة البيانات.

        المعاملات:
        - code: رمز المادة (مثال: 'EE101')
        - name: اسم المادة (مثال: 'الدوائر الكهربائية 1')
        - credits: عدد الساعات المعتمدة (مثال: 3)
        """
            # إدخال المادة الجديدة في جدول المواد

        self.cur.execute("INSERT INTO courses(code, name, credits) VALUES(?, ?, ?)",(code, name, credits) )
        self.commit()
        return "Course added successfully"

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
        sets,vals=[],[]

        
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

        self.cur.execute(f"UPDATE courses SET {', '.join(sets)} WHERE code=?",vals)
        self.commit()

    def ListCourses(self):
        """ترجع قائمة بجميع المواد (الكود، الاسم، الساعات)."""
        # نسترجع كل المواد من جدول , نرتبها تصاعدياً من الاقل الى الاعلى courses حسب الكود
        self.cur.execute("SELECT code, name, credits FROM courses ORDER BY code")
        return self.cur.fetchall()  #  (list)نرجع النتايج كقائمة من الصفوف او تقدر تقول ترجع النتائج ك


    def DeleteCourse(self, code):
        """تحذف مادة باستخدام كودها."""
        self.cur.execute("DELETE FROM courses WHERE code=?", (code,))
        self.commit()  # نحفظ التغييرات في قاعدة البيانات



class Admin(Database,User):

    def __init__(self):
        
    def AdminUpdateCourse():
        current = input("Enter the course code to update: ").strip()

        change_code    = input("Do you want to change the code? (yes/no): ").strip().lower() == 'yes'
        change_name    = input("Do you want to change the name? (yes/no): ").strip().lower() == 'yes'
        change_credits = input("Do you want to change the credits? (yes/no): ").strip().lower() == 'yes'

        new_code    = input("New code: ").strip() if change_code else None
        new_name    = input("New name: ").strip() if change_name else None
        new_credits = int(input("New credits: ").strip()) if change_credits else None

        msg = UpdateCourse(
            current_code=current,
            new_code=new_code,
            new_name=new_name,
            new_credits=new_credits)
        print(msg)


    def AdminAddCourse():
        """
        دالة خاصة بالمدير (الأدمن) لإضافة مادة جديدة.
        تطلب من الأدمن إدخال معلومات المادة، ثم تستدعي الدالة الخاصة بقاعدة البيانات.
        """
        # طلب بيانات المادة من الأدمن
        code = input("Enter course code: ").strip()
        name = input("Enter course name: ").strip()
        credits = int(input("Enter course credits: ").strip())
        # استدعاء الدالة الخاصة بقاعدة البيانات لإضافة المادة

        msg =AddCourse(code, name, credits)
        # طباعة النتيجة للمستخدم

        print(msg)

    def AdminDeleteCourses():
        '''يحذف المادة من القائمة'''
        print(ListCourses)     #يعرض القائمة 
        msg=DeleteCourse(code) #يحذف القائمة 
