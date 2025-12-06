import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from admin.class_admin_utilities import AdminUtilities, db
from helper_files.validators import hash_password

admin = AdminUtilities(db)

def create_instructor(name, email, password):
    hashed = hash_password(password)

    response = db.add_users(
        name=name,
        email=email,
        program=None,          # instructors have no program
        password=hashed,
        state="admin"      # this sets correct role and ID range
    )

    print(f"{email} -> {response}")


# -------------------------------
# ADD INSTRUCTORS HERE
# -------------------------------

create_instructor("salem", "aaa@aa.dd", "1234")
create_instructor("Dr. Ahmed Instructor", "inst32@uni.test", "password")
create_instructor("Ms. Nora Instructor", "inst43@uni.test", "abcd")
