# import sqlite3
# from random import choice, randint

# # Connect to your database
# con = sqlite3.connect("university_database.db")
# cur = con.cursor()

# # List of mock names and programs
# names = ["Alice Smith", "Bob Johnson", "Charlie Lee", "Diana Brown", "Ethan White"]
# programs = ["PWM", "BIO", "COMM", "COMP"]

# # Number of mock students to add
# num_students = 10

# for i in range(num_students):
#     name = choice(names) + f" {randint(1, 100)}"  # Ensure uniqueness
#     email = name.replace(" ", ".").lower() + "@example.com"
#     program = choice(programs)
#     password_h = "hashed_password"  # placeholder, replace with real hash if needed
#     state = "student"
#     account_status = "inactive"
    
#     try:
#         cur.execute("""
#         INSERT INTO users (name, email, program, password_h, state, account_status)
#         VALUES (?, ?, ?, ?, ?, ?)
#         """, (name, email, program, password_h, state, account_status))
#     except sqlite3.IntegrityError:
#         # Skip duplicates
#         continue

# # Commit changes and close
# con.commit()
# con.close()

# print(f"Inserted {num_students} mock students (duplicates skipped).")




#-------------
# from student.class_student_utilities import db

# cur = db.cur

# cur.execute("SELECT * FROM students WHERE student_id=?", (2500001,))
# print(cur.fetchone())

# cur.execute("SELECT program FROM students WHERE student_id=?", (2500001,))
# print("PROGRAM:", cur.fetchone())



#-----------


