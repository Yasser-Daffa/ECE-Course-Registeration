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
