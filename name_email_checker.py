def get_user_info():
    while True:
        username = input("Enter username: ").strip()
        if not username:
            print("Error: username is required.")
            continue
        if " " in username:
            print("Error: username cannot contain spaces.")
            continue

        email = input("Enter email: ").strip()
        if not email or "@" not in email or "." not in email.split("@")[-1]:
            print("Error: invalid email. Example: user@example.com")
            continue
        if " " in email:
            print("Error: email cannot contain spaces.")
            continue

        print("\nSaved successfully!")
        print("Username:", username)
        print("Email:", email)
        return username, email

get_user_info()


####################################################################################

while True:
    username = input("Enter username: ").strip()
    if not username:
        print("Error: username is required.")
        continue
    if " " in username:
        print("Error: username cannot contain spaces.")
        continue

    email = input("Enter email: ").strip()
    if not email:
        print("Error: email is required.")
        continue
    if "@" not in email or "." not in email.split("@")[-1]:
        print("Error: invalid email. Example: user@example.com")
        continue
    if " " in email:
        print("Error: email cannot contain spaces.")
        continue

    print("\nSaved successfully!")
    print("Username:", username)
    print("Email:", email)
    break
