import sqlite3

def initialize_database(db_path="../university_database.db"):
    """Initializes all database tables, triggers, and constraints."""

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    cur.execute("pragma foreign_keys = ON;")

    # Courses table for all courses across all programs
    cur.execute("""
    create table if not exists courses(
        name text not null,
        code text primary key,
        credits integer not null check(credits >= 0)
    )
    """)

    # Prerequisite table (course → required prerequisite)
    cur.execute("""
    create table if not exists requires (
        course_code  text not null,   -- The course that requires a prerequisite (text, required)
        prereq_code  text not null,   -- The prerequisite course
        CHECK(course_code != prereq_code),
        primary key (course_code, prereq_code),  -- Prevents duplicates (same course + prereq pair)

        foreign key (course_code)  references courses(code) ON DELETE CASCADE ON UPDATE CASCADE,
        foreign key (prereq_code) references courses(code) ON DELETE CASCADE ON UPDATE CASCADE
    );
    """)

    # Sections table (class sections)
    cur.execute("""
    create table if not exists sections(
        section_id integer primary key AUTOINCREMENT, -- Auto-incremented unique section ID
        course_code text not null,  -- Course code
        doctor_id integer,          -- Instructor ID
        days text,                  -- Lecture days
        time_start text,            -- Start time
        time_end text,              -- End time
        room text,                  -- Room number
        capacity integer not null check (capacity >= 0), -- Section capacity
        enrolled integer not null check (enrolled >= 0 and enrolled <= capacity), -- Enrolled students
        semester text not null,     -- Semester
        state text not null check (state in ('open','closed')), -- Section state (open/closed)

        unique (course_code, section_id, semester),   -- Prevent same section repeating in same semester
        unique (doctor_id, days, time_start, time_end), -- Prevent instructor from teaching 2 sections at the same time

        foreign key (course_code) references courses(code) on delete cascade on update cascade,
        foreign key (doctor_id) references users(user_id) on delete cascade on update cascade
    );
    """)

    # Users table (students, admins, instructors)
    cur.execute("""
    create table if not exists users(
        user_id integer primary key AUTOINCREMENT,  -- Auto-generated ID
        name text not null,                         -- User name
        email text not null,                        -- Email
        program text check(program in ('PWM','BIO','COMM','COMP')), -- Program
        password_h text not null,                   -- Password hash
        state text not null check (state in ('admin','student','instructor')), -- Role
        account_status text not null default 'inactive' check(account_status in ('active','inactive')),
        unique (email) -- Ensure email is not duplicated
    );
    """)

    # Trigger: Add ID prefix based on user type
    cur.execute("""
    CREATE TRIGGER IF NOT EXISTS trg_users_prefix_id
    AFTER INSERT ON users
    FOR EACH ROW
    BEGIN
        UPDATE users
        SET user_id =
            CASE NEW.state
                WHEN 'student'    THEN user_id + 2500000
                WHEN 'admin'      THEN user_id + 1100000
                WHEN 'instructor' THEN user_id + 3300000
                ELSE user_id
            END
        WHERE rowid = NEW.rowid;
    END;
    """)

    # Login history (store last login time)
    cur.execute("""
    create table if not exists login(
        user_id integer not null,  -- User ID
        last_login text,           -- Last login timestamp
        foreign key (user_id) references users(user_id) on delete cascade
    );
    """)

    # Student basic information
    cur.execute("""
    create table if not exists students(
        student_id integer primary key,   -- Same as user_id (linked)
        level integer check (level >= 1), -- Current academic level
        foreign key (student_id) references users(user_id) on delete cascade on update cascade
    );
    """)

    # Student registrations (current enrolled sections)
    cur.execute("""
    create table if not exists registrations(
        student_id integer not null,
        section_id integer not null,
        course_code text not null,
        primary key (student_id, course_code), -- Prevent duplicate registration
        foreign key (student_id) references users(user_id) on delete cascade on update cascade,
        foreign key (section_id) references sections(section_id) on delete cascade on update cascade,
        foreign key (course_code) references courses(code) on delete cascade on update cascade
    );
    """)

    # Student transcript (completed courses + grades)
    cur.execute("""
    create table if not exists transcripts(
        student_id integer not null,
        course_code text not null,
        semester text not null,
        grade text,
        primary key (student_id, course_code, semester), -- Prevent duplicates for same semester
        foreign key (student_id) references users(user_id) on delete cascade on update cascade,
        foreign key (course_code) references courses(code) on update cascade
    );
    """)

    # Program plan (study plan per program/level)
    cur.execute("""
    create table if not exists program_plans(
        program text not null,      -- Program name
        level integer not null check (level >= 1),
        course_code text not null,  -- Course in this level
        primary key (program, course_code),
        foreign key (course_code) references courses(code) on delete restrict on update cascade
    );
    """)

    con.commit()
    return con, cur