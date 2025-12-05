import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from student.class_student_utilities import StudentUtilities, db

student_id = 7500003
stu = StudentUtilities(db, student_id)

# Directly fetch registered sections/courses
registrations = db.list_student_registrations(student_id)

print(f"Student {student_id} registered courses/sections:")
for reg in registrations:
    # Assuming reg dict has section_id and course_code
    section_id = reg['section_id']
    course_code = reg['course_code']
    
    # Get section info
    sec_info = db.get_section_by_id(section_id)
    if sec_info:
        print(
            f"{course_code} | Section {section_id} | Days: {sec_info['days']} | "
            f"Time: {sec_info['time_start']}-{sec_info['time_end']} | Room: {sec_info['room']} | "
            f"Instructor: {sec_info['instructor']}"
        )
