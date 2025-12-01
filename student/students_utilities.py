class Student:
    def __init__(self, db, student_id):
        # نخزن كائن قاعدة البيانات
        self.db = db
        # نخزن رقم الطالب (تم استقباله عند تسجيل الدخول)
        self.student_id = student_id

    # ================== دوال مساعدة للطالب ==================

    def is_registration_open(self, semester):
        # هذه الدالة تتحقق إذا التسجيل مفتوح في هذا الترم
        self.db.cur.execute("""
            SELECT 1 FROM sections
            WHERE semester = ? AND state = 'open'
            LIMIT 1
        """, (semester,))
        return self.db.cur.fetchone() is not None

    def get_student_program(self):
        # هذه الدالة تجيب برنامج الطالب من جدول users باستخدام الآيدي المخزن
        self.db.cur.execute("""
            SELECT program FROM users WHERE user_id = ?
        """, (self.student_id,))
        row = self.db.cur.fetchone()
        return row[0] if row else None

    def get_program_plan_courses(self, program):
        # هذه الدالة تجيب كل مواد الخطة الدراسية لبرنامج معيّن
        # يفترض وجود جدول program_plans(program, course_code)
        self.db.cur.execute("""
            SELECT course_code
            FROM program_plans
            WHERE program = ?
            ORDER BY course_code
        """, (program,))
        return [row[0] for row in self.db.cur.fetchall()]

    def get_completed_courses(self):
        # هذه الدالة تجيب المواد التي أنهى الطالب دراستها (لها grade)
        self.db.cur.execute("""
            SELECT course_code
            FROM transcripts
            WHERE student_id = ? AND grade IS NOT NULL
        """, (self.student_id,))
        return [row[0] for row in self.db.cur.fetchall()]

    def show_my_transcript(self):
        # (جديد) هذه الدالة تعرض السجل الأكاديمي للطالب نفسه
        self.db.cur.execute("""
            SELECT course_code, semester, grade
            FROM transcripts
            WHERE student_id = ?
            ORDER BY semester, course_code
        """, (self.student_id,))

        rows = self.db.cur.fetchall()
        if not rows:
            print("No transcript records found.")
            return

        print(f"\nTranscript for Student ID: {self.student_id}")
        print("Semester | Course  | Grade")
        print("---------------------------")
        for course_code, semester, grade in rows:
            print(f"{semester}   | {course_code} | {grade}")

    def get_registered_courses(self, semester=None):
        # هذه الدالة تجيب المواد التي الطالب مسجلها حالياً
        query = """
            SELECT DISTINCT s.course_code
            FROM registrations r
            JOIN sections s ON r.section_id = s.section_id
            WHERE r.student_id = ?
        """
        params = [self.student_id]

        # لو حددنا ترم نفلتر عليه
        if semester is not None:
            query += " AND s.semester = ?"
            params.append(semester)

        self.db.cur.execute(query, params)
        return [row[0] for row in self.db.cur.fetchall()]

    def get_available_courses(self, semester):
        # هذه الدالة تحسب المواد اللي يقدر الطالب يسجلها في هذا الترم
        # (حسب الخطة + المتطلبات + المواد اللي خلصها/مسجلها)

        program = self.get_student_program()
        if not program:
            print("✗ No program found for this student.")
            return []

        # مواد الخطة الدراسية للبرنامج
        plan_courses = self.get_program_plan_courses(program)

        # المواد المنتهية
        completed = set(self.get_completed_courses())
        # المواد المسجلة حالياً (أي ترم)
        registered = set(self.get_registered_courses())

        available = []

        for course_code in plan_courses:
            # نتخطى المواد اللي الطالب خلصها أو مسجلها أصلاً
            if course_code in completed or course_code in registered:
                continue

            # نجيب اسم المادة وعدد ساعاتها
            self.db.cur.execute("""
                SELECT name, credits FROM courses WHERE code = ?
            """, (course_code,))
            row = self.db.cur.fetchone()
            if not row:
                continue

            course_name, credits = row

            # نجيب متطلبات المادة من جدول requires
            # يفترض جدول requires(course_code, prereq_code)
            self.db.cur.execute("""
                SELECT prereq_code
                FROM requires
                WHERE course_code = ?
            """, (course_code,))
            prereqs = [r[0] for r in self.db.cur.fetchall()]

            # المتطلبات الناقصة (اللي الطالب ما خلصها)
            missing = [p for p in prereqs if p not in completed]

            can_register = (len(missing) == 0)

            available.append({
                "course_code": course_code,
                "course_name": course_name,
                "credits": credits,
                "prereqs": prereqs,
                "missing_prereqs": missing,
                "can_register": can_register
            })

        return available

    def show_available_courses(self, semester):
        # هذه الدالة تعرض المواد اللي يقدر الطالب يسجلها واللي ما يقدر بسبب المتطلبات

        courses = self.get_available_courses(semester)
        if not courses:
            print("\nNo available courses.")
            return []

        can = [c for c in courses if c["can_register"]]
        cannot = [c for c in courses if not c["can_register"]]

        print("\n" + "=" * 70)
        print(f"Available courses for semester {semester}")
        print("=" * 70)

        if can:
            print("\n✓ You can register these courses:")
            for c in can:
                print(f"  {c['course_code']} - {c['course_name']} ({c['credits']} credits)")

        if cannot:
            print("\n✗ You CANNOT register these courses (missing prerequisites):")
            for c in cannot:
                missing_str = ", ".join(c["missing_prereqs"])
                print(f"  {c['course_code']} - {c['course_name']}")
                print(f"    Missing: {missing_str}")

        print("=" * 70 + "\n")
        return can  # نرجع فقط المواد اللي فعلاً يقدر يسجلها

    # ================== اختيار المواد والشعب ==================

    def select_courses(self, semester):
        # هذه الدالة تخلي الطالب يختار المواد اللي يبغاها
        available = self.show_available_courses(semester)
        if not available:
            return []

        available_codes = [c["course_code"] for c in available]
        selected = []

        print("Enter course codes to register (type 'done' to finish):")

        while True:
            code = input("Course code: ").strip().upper()
            if code == "DONE":
                break

            if code not in available_codes:
                print("✗ This course is not in the available list.")
                continue

            if code in selected:
                print("✗ You already selected this course.")
                continue

            selected.append(code)
            print(f"✓ {code} added.")

        if not selected:
            print("\nNo courses selected.")
        else:
            print("\nSelected:", ", ".join(selected))

        return selected

    def get_sections_for_courses(self, course_codes, semester):
        # هذه الدالة تجيب الشعب المتاحة (المفتوحة + فيها مقاعد) لكل مادة

        sections_by_course = {}

        for code in course_codes:
            self.db.cur.execute("""
                SELECT section_id, course_code, doctor_id, days,
                       time_start, time_end, room, capacity, enrolled,
                       semester, state
                FROM sections
                WHERE course_code = ? AND semester = ?
            """, (code, semester))

            rows = self.db.cur.fetchall()
            sections = []

            for row in rows:
                (section_id, course_code, doctor_id, days,
                 time_start, time_end, room, capacity, enrolled,
                 sem, state) = row

                # نضيف فقط الشعب المفتوحة واللي فيها مقاعد فاضية
                if state == "open" and enrolled < capacity:
                    sections.append({
                        "section_id": section_id,
                        "course_code": course_code,
                        "doctor_id": doctor_id,
                        "days": days,
                        "time_start": time_start,
                        "time_end": time_end,
                        "room": room,
                        "capacity": capacity,
                        "enrolled": enrolled,
                        "semester": sem,
                        "state": state,
                        "available_seats": capacity - enrolled
                    })

            sections_by_course[code] = sections

        return sections_by_course

    def check_time_conflict(self, sec1, sec2):
        # هذه الدالة تتحقق من تعارض الأوقات بين شعبتين
        # تفترض أن الأيام كنص مثل "MTW" والأوقات بصيغة 24 ساعة "HH:MM"

        days1 = set(sec1["days"].upper().replace(" ", ""))
        days2 = set(sec2["days"].upper().replace(" ", ""))

        # لو ما فيه أيام مشتركة ما فيه تعارض
        if not days1.intersection(days2):
            return False

        start1 = sec1["time_start"]  # مثال "08:00"
        end1 = sec1["time_end"]  # مثال "09:30"
        start2 = sec2["time_start"]
        end2 = sec2["time_end"]

        # بما أن الوقت بصيغة "HH:MM" في نظام 24 ساعة
        # تقدر تقارن كنص وتشوف التداخل
        if start1 < end2 and start2 < end1:
            return True

        return False

    def show_sections_and_select(self, course_codes, semester):
        # هذه الدالة تعرض الشعب لكل مادة وتخلي الطالب يختار شعبة واحدة لكل مادة

        sections_data = self.get_sections_for_courses(course_codes, semester)
        selected_sections = {}

        for code in course_codes:
            sections = sections_data.get(code, [])

            if not sections:
                print(f"\n⚠ No sections available for course {code}")
                continue

            print("\n" + "=" * 70)
            print(f"Sections for course {code}")
            print("=" * 70)

            for i, sec in enumerate(sections, start=1):
                print(f"{i}. Section ID: {sec['section_id']}")
                print(f"   Days : {sec['days']}")
                print(f"   Time : {sec['time_start']} - {sec['time_end']}")
                print(f"   Room : {sec['room']}")
                print(f"   Seats: {sec['available_seats']}/{sec['capacity']}")
                print("-" * 70)

            while True:
                choice = input(f"Choose section number for {code} (or 'skip'): ").strip()
                if choice.lower() == "skip":
                    print(f"{code} skipped.")
                    break

                try:
                    idx = int(choice) - 1
                except ValueError:
                    print("✗ Please enter a valid number.")
                    continue

                if 0 <= idx < len(sections):
                    selected_sections[code] = sections[idx]
                    print(f"✓ Section {sections[idx]['section_id']} selected for {code}")
                    break
                else:
                    print("✗ Invalid section number.")

        return selected_sections

    # ================== التسجيل الفعلي + الحذف + الجدول ==================

    def register_selected_sections(self, selected_sections, semester):
        # هذه الدالة تسجل فعلياً الشعب اللي اختارها الطالب
        # تتحقق من:
        # - التسجيل مفتوح
        # - ما فيه تعارض بين الشعب الجديدة مع بعض
        # - ما فيه تعارض بين الشعب الجديدة والمواد المسجلة سابقاً
        # - فيه مقاعد فاضية
        # - زيادة enrolled +1 لكل شعبة ناجحة

        # أولاً: التأكد أن التسجيل مفتوح في هذا الترم
        if not self.is_registration_open(semester):
            print(f"✗ Registration is closed for semester {semester}.")
            return

        # لو ما فيه شعب مختارة
        if not selected_sections:
            print("✗ No sections selected.")
            return

        # نحول الشعب المختارة لقائمة (قيم القاموس) لسهولة التعامل
        new_sections = list(selected_sections.values())

        # ====== 1) نجيب جدول الطالب الحالي من قاعدة البيانات ======
        # نجيب كل الشعب اللي الطالب مسجلها فعلياً في هذا الترم
        self.db.cur.execute("""
            SELECT s.section_id, s.course_code, s.days, s.time_start, s.time_end
            FROM registrations r
            JOIN sections s ON r.section_id = s.section_id
            WHERE r.student_id = ? AND s.semester = ?
        """, (self.student_id, semester))

        existing_rows = self.db.cur.fetchall()

        # نحول الجدول الحالي لقائمة قواميس بنفس شكل بيانات الشعب الجديدة
        existing_sections = []
        for row in existing_rows:
            section_id, course_code, days, time_start, time_end = row
            existing_sections.append({
                "section_id": section_id,
                "course_code": course_code,
                "days": days,
                "time_start": time_start,
                "time_end": time_end
            })

        # قائمة لتخزين الشعب اللي تم تسجيلها في نفس هذه العملية
        # عشان نتحقق من التعارض بينها بعد النجاح
        registered_this_call = []

        registered = []  # مواد تم تسجيلها بنجاح
        failed = []  # مواد فشلت مع السبب

        # ====== 2) نمر على كل شعبة جديدة ونطبق الشروط ======
        for sec in new_sections:
            course_code = sec["course_code"]

            # ---- 2.1 التحقق من التعارض مع الجدول القديم ----
            conflict_with_old = False
            for old in existing_sections:
                if self.check_time_conflict(sec, old):
                    # لو فيه تعارض مع مادة قديمة مسجلة
                    reason = f"Time conflict with already registered course {old['course_code']}"
                    failed.append((course_code, reason))
                    print(f"✗ {course_code} not registered: {reason}")
                    conflict_with_old = True
                    break

            if conflict_with_old:
                # ننتقل للمادة التالية
                continue

            # ---- 2.2 التحقق من التعارض مع الشعب الجديدة المقبولة في نفس العملية ----
            conflict_with_new = False
            for ok_sec in registered_this_call:
                if self.check_time_conflict(sec, ok_sec):
                    reason = f"Time conflict with newly registered course {ok_sec['course_code']}"
                    failed.append((course_code, reason))
                    print(f"✗ {course_code} not registered: {reason}")
                    conflict_with_new = True
                    break

            if conflict_with_new:
                continue

            # ---- 2.3 إعادة التحقق من حالة الشعبة من قاعدة البيانات (مقاعد / حالة) ----
            self.db.cur.execute("""
                SELECT capacity, enrolled, state
                FROM sections
                WHERE section_id = ?
            """, (sec["section_id"],))
            row = self.db.cur.fetchone()

            if not row:
                # لو الشعبة اختفت من قاعدة البيانات
                failed.append((course_code, "Section not found in database"))
                print(f"✗ {course_code} not registered: section not found.")
                continue

            capacity, enrolled, state = row

            # الشعبة مقفلة
            if state != "open":
                failed.append((course_code, "Section is closed"))
                print(f"✗ {course_code} not registered: section is closed.")
                continue

            # الشعبة ممتلئة
            if enrolled >= capacity:
                failed.append((course_code, "Section is full"))
                print(f"✗ {course_code} not registered: section is full.")
                continue

            # ---- 2.4 لو كل شيء تمام، نسجل الطالب في الشعبة ----
            try:
                # إضافة سجل في جدول registrations
                self.db.cur.execute("""
                    INSERT INTO registrations(student_id, section_id)
                    VALUES (?, ?)
                """, (self.student_id, sec["section_id"]))

                # زيادة عدد المسجلين في جدول sections
                self.db.cur.execute("""
                    UPDATE sections
                    SET enrolled = enrolled + 1
                    WHERE section_id = ?
                """, (sec["section_id"],))

                # حفظ في قاعدة البيانات
                self.db.commit()

                # نضيف المقرر لقائمة الناجحين
                registered.append(course_code)
                # نضيف هذه الشعبة لقائمة الشعب المسجلة في هذه العملية
                registered_this_call.append(sec)

                print(f"✓ {course_code} registered successfully.")

            except Exception as e:
                # لو صار خطأ في قاعدة البيانات
                failed.append((course_code, f"Database error: {e}"))
                print(f"✗ {course_code} not registered: database error.")

        # ====== 3) عرض النتائج النهائية ======
        print("\n" + "=" * 70)
        print("Registration result")
        print("=" * 70)

        if registered:
            print("\n✓ Registered courses:")
            for c in registered:
                print(f"  - {c}")
        else:
            print("\nNo courses registered successfully.")

        if failed:
            print("\n✗ Failed courses:")
            for c, reason in failed:
                print(f"  - {c} | Reason: {reason}")

        print("=" * 70 + "\n")

    def drop_course(self, course_code, semester):
        # هذه الدالة تحذف مادة من جدول الطالب
        # تتأكد أن:
        # - المادة مسجلة
        # - التسجيل مفتوح
        # - تنقص enrolled -1 من الشعبة

        # نجيب الشعبة اللي الطالب مسجل فيها هذا المقرر في هذا الترم
        self.db.cur.execute("""
            SELECT r.section_id
            FROM registrations r
            JOIN sections s ON r.section_id = s.section_id
            WHERE r.student_id = ? AND s.course_code = ? AND s.semester = ?
        """, (self.student_id, course_code, semester))
        row = self.db.cur.fetchone()

        if not row:
            print(f"✗ Course {course_code} is not registered in semester {semester}.")
            return

        section_id = row[0]

        # نتأكد أن التسجيل مفتوح
        if not self.is_registration_open(semester):
            print(f"✗ Cannot drop course {course_code}: registration is closed.")
            return

        try:
            # نحذف من جدول registrations
            self.db.cur.execute("""
                DELETE FROM registrations
                WHERE student_id = ? AND section_id = ?
            """, (self.student_id, section_id))

            # ننقص عدد المسجلين في جدول sections
            self.db.cur.execute("""
                UPDATE sections
                SET enrolled = enrolled - 1
                WHERE section_id = ?
            """, (section_id,))

            self.db.commit()
            print(f"✓ Course {course_code} dropped from semester {semester}.")

        except Exception as e:
            print("✗ Failed to drop course:", e)

    def show_schedule(self, semester):
        # هذه الدالة تعرض جدول الطالب في الترم المحدد

        self.db.cur.execute("""
            SELECT s.section_id, s.course_code, c.name,
                   s.days, s.time_start, s.time_end, s.room,
                   c.credits
            FROM registrations r
            JOIN sections s ON r.section_id = s.section_id
            JOIN courses c ON s.course_code = c.code
            WHERE r.student_id = ? AND s.semester = ?
            ORDER BY s.days, s.time_start
        """, (self.student_id, semester))

        rows = self.db.cur.fetchall()

        if not rows:
            print(f"\nNo courses registered in semester {semester}.")
            return

        print("\n" + "=" * 70)
        print(f"Schedule for semester {semester}")
        print("=" * 70)

        total_credits = 0

        for row in rows:
            section_id, code, name, days, start, end, room, credits = row
            print(f"\n{code} - {name} ({credits} credits)")
            print(f"  Section : {section_id}")
            print(f"  Days    : {days}")
            print(f"  Time    : {start} - {end}")
            print(f"  Room    : {room}")
            total_credits += credits

        print("\nTotal credits:", total_credits)
        print("=" * 70 + "\n")


# ==============================================================================
# كلاس إدارة التسجيل (يستخدمه الأدمن لفتح/غلق التسجيل وإدارة شعب الطلاب)
# تمت إضافته هنا ليتمكن ملف الأدمن من استيراده
# ==============================================================================

class AdminRegistration:
    def __init__(self, db):
        # نخزن كائن قاعدة البيانات
        self.db = db

    def open_registration(self, semester):
        # هذه الدالة تفتح التسجيل:
        # تخلي كل الشعب في هذا الترم state = 'open'
        self.db.cur.execute("""
            UPDATE sections
            SET state = 'open'
            WHERE semester = ? AND state = 'closed'
        """, (semester,))
        self.db.commit()
        print(f"✓ Registration opened for semester {semester}.")

    def close_registration(self, semester):
        # هذه الدالة تقفل التسجيل:
        # تخلي كل الشعب في هذا الترم state = 'closed'
        self.db.cur.execute("""
            UPDATE sections
            SET state = 'closed'
            WHERE semester = ? AND state = 'open'
        """, (semester,))
        self.db.commit()
        print(f"✓ Registration closed for semester {semester}.")

    def add_section_for_student(self, student_id, section_id):
        # هذه الدالة تخلي الأدمن يضيف شعبة لطالب
        # تتحقق من:
        # - وجود الشعبة
        # - عدم تكرار تسجيل نفس المادة في نفس الترم
        # - وجود مقاعد فاضية
        # - زيادة enrolled +1

        # نجيب بيانات الشعبة
        self.db.cur.execute("""
            SELECT section_id, course_code, capacity, enrolled, semester, state
            FROM sections
            WHERE section_id = ?
        """, (section_id,))
        row = self.db.cur.fetchone()

        if not row:
            print("✗ Section not found.")
            return

        sec_id, course_code, capacity, enrolled, semester, state = row

        # نتأكد أن الطالب مو مسجل نفس المادة في نفس الترم
        self.db.cur.execute("""
            SELECT 1
            FROM registrations r
            JOIN sections s ON r.section_id = s.section_id
            WHERE r.student_id = ? AND s.course_code = ? AND s.semester = ?
            LIMIT 1
        """, (student_id, course_code, semester))
        if self.db.cur.fetchone():
            print("✗ Student already registered in this course in this semester.")
            return

        # نتأكد فيه مقاعد فاضية
        if enrolled >= capacity:
            print("✗ Section is full.")
            return

        try:
            # نضيف تسجيل للطالب
            self.db.cur.execute("""
                INSERT INTO registrations(student_id, section_id)
                VALUES (?, ?)
            """, (student_id, sec_id))

            # نزيد عدد المسجلين
            self.db.cur.execute("""
                UPDATE sections
                SET enrolled = enrolled + 1
                WHERE section_id = ?
            """, (sec_id,))

            self.db.commit()
            print(f"✓ Student {student_id} added to course {course_code} (section {sec_id}).")

        except Exception as e:
            print("✗ Failed to add section for student:", e)

    def drop_section_for_student(self, student_id, section_id):
        # هذه الدالة تحذف شعبة عن طالب
        # لا ترتبط بحالة التسجيل (الأدمن يقدر حتى لو التسجيل مقفول)
        # وتقلل enrolled -1

        # نتأكد أن الطالب مسجل في هذه الشعبة
        self.db.cur.execute("""
            SELECT 1
            FROM registrations
            WHERE student_id = ? AND section_id = ?
        """, (student_id, section_id))
        if not self.db.cur.fetchone():
            print("✗ Student is not registered in this section.")
            return

        try:
            # حذف التسجيل
            self.db.cur.execute("""
                DELETE FROM registrations
                WHERE student_id = ? AND section_id = ?
            """, (student_id, section_id))

            # تقليل عدد المسجلين
            self.db.cur.execute("""
                UPDATE sections
                SET enrolled = enrolled - 1
                WHERE section_id = ?
            """, (section_id,))

            self.db.commit()
            print(f"✓ Section {section_id} dropped for student {student_id}.")

        except Exception as e:
            print("✗ Failed to drop section for student:", e)

    def show_student_schedule(self, student_id, semester):
        # هذه الدالة تعرض جدول طالب معيّن للأدمن

        # نجيب اسم الطالب وبرنامجه
        self.db.cur.execute("""
            SELECT name, program
            FROM users
            WHERE user_id = ?
        """, (student_id,))
        row = self.db.cur.fetchone()

        if not row:
            print("✗ Student not found.")
            return

        name, program = row

        print("\n" + "=" * 70)
        print(f"Schedule for {name} (ID: {student_id}) - Program: {program}")
        print("=" * 70)

        # نعرض جدول الطالب
        self.db.cur.execute("""
            SELECT s.section_id, s.course_code, c.name,
                   s.days, s.time_start, s.time_end, s.room,
                   c.credits
            FROM registrations r
            JOIN sections s ON r.section_id = s.section_id
            JOIN courses c ON s.course_code = c.code
            WHERE r.student_id = ? AND s.semester = ?
            ORDER BY s.days, s.time_start
        """, (student_id, semester))

        rows = self.db.cur.fetchall()

        if not rows:
            print(f"No courses registered in semester {semester}.")
            print("=" * 70 + "\n")
            return

        total_credits = 0
        for row in rows:
            section_id, code, cname, days, start, end, room, credits = row
            print(f"\n{code} - {cname} ({credits} credits)")
            print(f"  Section : {section_id}")
            print(f"  Days    : {days}")
            print(f"  Time    : {start} - {end}")
            print(f"  Room    : {room}")
            total_credits += credits

        print("\nTotal credits:", total_credits)
        print("=" * 70 + "\n")