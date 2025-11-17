def get_user_info():
    while True:
        # -------- Student ID --------
        student_id = input("Enter your Student ID: ").strip()

        # لا يكون فاضي
        if not student_id:
            print("Error: Student ID is required.")
            continue

        # بدون مسافات
        if " " in student_id:
            print("Error: Student ID cannot contain spaces.")
            continue

        # لازم يكون أرقام فقط
        if not student_id.isdigit():
            print("Error: Student ID must contain numbers only.")
            continue

        # طول ID = 7 أرقام
        if len(student_id) != 7:
            print("Error: Student ID must be 7 digits.")
            continue

        # -------- Email --------
        email = input("Enter email: ").strip()

        if not email:
            print("Error: email is required.")
            continue

        if " " in email:
            print("Error: email cannot contain spaces.")
            continue

        if email.count("@") != 1:
            print("Error: invalid email format.")
            continue

        local, domain = email.split("@")

        if not local:
            print("Error: invalid email format.")
            continue

        if "." not in domain:
            print("Error: invalid email format.")
            continue

        if domain.startswith("."):
            print("Error: invalid email format.")
            continue

        if not domain[-1].isalnum():
            print("Error: invalid email format.")
            continue

        # قائمة الدومينات الخاطئة التي يتم رفضها
        wrong_domains = {
            "gamil.com", "gmial.com", "gmai.com", "gmal.com",
            "gmaiil.com", "gmail.co", "gmail.con", "gnail.com",
            "gmail.comm", "gmai.con",
            "hotmil.com", "hotmal.com", "hotmial.com",
            "hotmai.com", "hotnail.com", "homtail.com",
            "outlok.com", "outllok.com", "ootlook.com",
            "outloook.com", "outloo.com",
        }

        if domain.lower() in wrong_domains:
            print("Error: invalid email format.")
            continue

        email = f"{local}@{domain}".lower()

        print("\nSaved successfully!")
        print("Student ID:", student_id)
        print("Email:", email)
        return student_id, email


# Run
get_user_info()



##########################################################################################

def get_full_name():
    while True:
        # طلب إدخال الاسم الثلاثي من المستخدم
        full_name = input("Enter your full name (First - Middle - Last): ")

        # تنظيف المسافات الزائدة والمكررة
        cleaned = " ".join(full_name.split())

        # تحويل النص إلى حروف صغيرة
        lowered = cleaned.lower()

        # التحقق أن المدخل يحتوي على حروف ومسافات فقط
        if not lowered.replace(" ", "").isalpha():
            print("خطأ! الاسم يجب أن يحتوي على حروف فقط بدون أرقام أو رموز.\n")
            continue

        # تحويل أول حرف من كل كلمة إلى حرف كبير
        formatted = lowered.title()

        # تقسيم الاسم إلى ثلاثة أجزاء
        parts = formatted.split()

        # التحقق أن الاسم ثلاثي بالضبط
        if len(parts) != 3:
            print("خطأ! الرجاء إدخال اسم ثلاثي فقط.\n")
            continue

        first_name, middle_name, last_name = parts

        # التحقق أن كل كلمة مكونة من 3 أحرف أو أكثر
        if any(len(name) < 3 for name in parts):
            print("خطأ! كل اسم يجب أن يكون 3 أحرف أو أكثر.\n")
            continue

        # طباعة الاسم النهائي بعد التنسيق
        print("Full Name:", first_name, middle_name, last_name)

        return first_name, middle_name, last_name


# استدعاء الدالة وتشغيلها
get_full_name()

