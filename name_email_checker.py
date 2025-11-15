def get_user_info():
    # خريطة لأخطاء الدومينات وتصحيحها تلقائياً
    typo_domains = {
        # Gmail
        "gamil.com": "gmail.com",
        "gmial.com": "gmail.com",
        "gmai.com": "gmail.com",
        "gmal.com": "gmail.com",
        "gmaiil.com": "gmail.com",
        "gmail.co": "gmail.com",
        "gmail.con": "gmail.com",
        "gnail.com": "gmail.com",
        "gmail.comm": "gmail.com",

        # Hotmail
        "hotmil.com": "hotmail.com",
        "hotmal.com": "hotmail.com",
        "hotmial.com": "hotmail.com",
        "hotmai.com": "hotmail.com",
        "hotnail.com": "hotmail.com",
        "homtail.com": "hotmail.com",

        # Outlook
        "outlok.com": "outlook.com",
        "outllok.com": "outlook.com",
        "ootlook.com": "outlook.com",
        "outloook.com": "outlook.com",
        "outloo.com": "outlook.com",
    }

    while True:
        # -------- Username --------
        username = input("Enter username: ").strip()

        if not username:
            print("Error: username is required.")
            continue

        if " " in username:
            print("Error: username cannot contain spaces.")
            continue

        if len(username) < 3:
            print("Error: username must be at least 3 characters.")
            continue
        if len(username) > 20:
            print("Error: username is too long (max 20 characters).")
            continue

        if username[0].isdigit():
            print("Error: username cannot start with a number.")
            continue

        allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
        if any(ch not in allowed for ch in username):
            print("Error: username can only contain letters, numbers, and _")
            continue

        username = username.lower()

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

        #  تصحيح تلقائي بدون إعلام المستخدم
        domain_lower = domain.lower()
        if domain_lower in typo_domains:
            domain = typo_domains[domain_lower]

        # إعادة تركيب الإيميل
        email = f"{local}@{domain}".lower()

        print("\nSaved successfully!")
        print("Username:", username)
        print("Email:", email)
        return username, email


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

