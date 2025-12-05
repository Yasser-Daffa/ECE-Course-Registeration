import os
import sys

# عشان نضمن الوصول للمجلد الرئيسي للمشروع
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from student.class_student_utilities import StudentUtilities, db


def add_or_update_yaser_grade():
    print("=== إضافة / تعديل درجة مادة YASER لطالب ===\n")

    # 1) ناخذ رقم الطالب
    while True:
        s = input("ادخل رقم الطالب (student_id): ").strip()
        if not s.isdigit():
            print("❌ لازم رقم صحيح")
            continue
        student_id = int(s)
        break

    # 2) نثبّت كود المادة YASER
    course_code = "YASER"
    print(f"\nالمادة المستهدفة: {course_code}")

    # 3) ناخذ السمستر
    semester = input("ادخل السمستر (مثال: First أو 2025-1): ").strip()
    if not semester:
        print("❌ ما ينفع سمستر فاضي")
        return

    # 4) ناخذ الدرجة
    grade = input("ادخل الدرجة (مثال: A, B+, C, F): ").strip().upper()
    if not grade:
        print("❌ ما ينفع درجة فاضية")
        return

    # 5) نجيب الترانسكربت الحالي للطالب
    stu = StudentUtilities(db, student_id)
    transcript_rows = db.list_transcript(student_id)  # (course_code, semester, grade)

    # نشوف هل فيه سجل لنفس المادة ونفس السمستر
    exists = any((c == course_code and sem == semester) for (c, sem, g) in transcript_rows)

    if exists:
        print("\n🔁 يوجد سجل سابق لهذه المادة وهذا السمستر، سيتم تحديث الدرجة...")
        msg = db.UpdateTranscriptGrade(student_id, course_code, semester, grade)
    else:
        print("\n➕ لا يوجد سجل سابق، سيتم إضافة سجل جديد في transcripts...")
        msg = db.add_transcript(student_id, course_code, semester, grade)

    print(f"\nنتيجة العملية: {msg}")

    # 6) نعرض الترانسكربت الكامل بعد التحديث
    print("\n=== Transcript بعد التحديث ===")
    stu.show_transcript()


if __name__ == "__main__":
    # تقدر تشغّل الملف من PyCharm أو من الترمينال:
    # python console_add_yaser_grade.py
    while True:
        add_or_update_yaser_grade()
        again = input("\nتبغى تعدل / تضيف لطالب آخر؟ (y/n): ").strip().lower()
        if again != "y":
            print("Bye 👋")
            break
