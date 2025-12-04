import sqlite3
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "university_database.db"))
con = sqlite3.connect(DB_PATH)
cur = con.cursor()

try:
    cur.execute("INSERT INTO students (student_id, level) VALUES (?, ?)", (1, 1))
    print("Inserted test student with ID 1")
except sqlite3.IntegrityError as e:
    print("Error inserting student:", e)

con.commit()
con.close()
