import sqlite3

con = sqlite3.connect("../university_database.db")
cur = con.cursor()



cur.execute("pragma foreign_keys = ON;")
# المواد
cur.execute("create table if not exists courses(name text not null,code text primary key,credits integer not null check(credits>=0))") #جدول لجميع المواد لكل الخطط

# هذا الجدول حق المواد المطلوبة
cur.execute("""
create table if not exists requires (
course_code  text not null,    --هنا قاعدين نحدد المادة وانه نوع الادخال يكون نص ومطلوب ادخاله ما ينفع يكون فاضي  

prereq_code  text not null , --هنا المادة المطلوبة للمقرر اللي فوق 
CHECK(course_code!=prereq_code),
primary key (course_code, prereq_code), --هنا وضيفة ال primary kye انه ما يخلي المادة والمطلوب يتكررون مره ثانية بحيث اذا الادمن دخل
                                        --"ee202" والمطلوب حقها "cpit110"  وجا مره ثانية دخل ذي المادة مع متطلبها ما رح يقبل

foreign key (course_code) references courses(code) ON DELETE CASCADE ON UPDATE CASCADE , --هنا بشكل عام قاعدين نقول ان المتغيرن بذا الجدول اللي هم المادة و مطلوبها شرط يكونون موجودبن ب جدول المواد واذا كانوا
                                                                       -- مو موجودين ما يقبل يدخل + اذا تم حذف المادة من الجدول الرئيسي تنحذف من هنا تلقائي

foreign key (prereq_code) references courses(code) ON DELETE CASCADE ON UPDATE CASCADE --- اضيف ابديت*****
);
""")

# جدول الشعب
cur.execute("""
create table if not exists sections(
section_id integer primary key AUTOINCREMENT, --الرقم التعريفي للشعبة كل مره يزيد بواجد
course_code text not null, -- رمز المادة
doctor_id integer, -- اسم الدكتور
days text, --ايام المحاظرات
time_start text,    --متى تبدا     
time_end text,   -- متى تنتهي
room text,  -- غرفة رقم كم
capacity integer not null check (capacity >= 0), --السعة
enrolled integer not null check (enrolled >= 0 and enrolled <= capacity), -- عدد الطلاب المسجلين بالشعبة
semester text not null,   --الترم 
state text not null check (state in ('open','closed')), -- حالة الشعبة لو مقفلة مفتوحة وزي كذا
unique (course_code,section_id , semester), --هنا قاعدين نقول انه لا يتكرر مره ثانيه بنفس رقم الشعبة بنفس الترم
unique (doctor_id, days, time_start,time_end), -- هنا نفس اللي فوق بس انه الدكتور ما يدرس شعبتين بنفس الوقت
foreign key (course_code) references courses(code) on delete cascade on update cascade  , --هنا نقول ان المادة شرط تكون بجدول المواد واذا انحذفت من هناك تنحذ من هنا
foreign key (doctor_id) references users(user_id) on delete cascade on update cascade
);
""")

# جدول اليوزرز سواء طلاب او الادمن
cur.execute("""create table if not exists users(
user_id integer primary key AUTOINCREMENT, --يتم انشاء رقم جامعي لك
name text not null, -- اسم الطالب او الاداري
email text not null, --الايميل
program text check(program in ('PWM','BIO','COMM','COMP')),               --
password_h text not null, --كلمة السر تنحفض بالهاش
state text not null check (state in ('admin','student','instructor')), -- اللي سجل طالب او ادمن ينحفظ هنا
account_status text not null default 'inactive' check(account_status in ('active','inactive')),
unique (email) --هنا اليونيك بمعنى انه ما يتكرر نفس الايميل 
);
""")

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


#جدول تسجيل الدخول الهدف الاساسي منه عشان نسجل اخر دخول للطالب او الاداري
cur.execute("""create table if not exists login(
user_id integer not null, -- رقم الطالب كمعرف 
last_login text, -- وقت تسجيل الدخول
foreign key (user_id) references users(user_id) on delete cascade  -- سوينا شرط ان رقم الطالب لازم يكون مرتبط برقم الطالب اللي باليوزر فوق
);""")

#هنا معلومات الطالب الاساسية في بعظ المعلومات مو موجودة زي الايميل لانه ببساطة نقدر نجيبها من الجداول اللي فوق
cur.execute("""
create table if not exists students(
student_id integer primary key,--رقم الطالب كمعرف مروط بالرقم اللي فوق                
level     integer check (level >= 1), -- الفل        
foreign key (student_id) references users(user_id) on delete cascade on update cascade --هنا زي ما ذكرت انه لازم يكون نفس الرقم بحيث لو انحذف فوق تنحذف هنا
);
""")
# تسجيل المواد او الجدول حق الطالب
cur.execute("""
create table if not exists registrations(
student_id integer not null, -- رقم الطالب              
section_id integer not null,  -- رقم الشعبة            
primary key (student_id, section_id),   -- ما يتكرر الطالب بنفس الشعبة    
foreign key (student_id) references students(student_id) on delete cascade on update cascade, --شروط انها تكون مربوطه زي ما ذكرت بالامثلة السابقة 
foreign key (section_id) references sections(section_id) on delete cascade on update cascade --نفس الشيء
);
""")
# سجل الطالب التاريخي في هكل المواد اللي خلصها مع الدرجات
cur.execute("""
create table if not exists transcripts(
student_id integer not null, -- رقم الطالب                  
course_code text not null,   -- رمز المادة                  
semester text not null,-- الترم
grade text,               -- الدرجة                   
primary key (student_id, course_code, semester),-- ما يتكرر نفس الرقم حق الطالب و الكورس و الترم
foreign key (student_id) references students(student_id) on delete cascade on update cascade, -- ارتباطات شرحناها فوق
foreign key (course_code) references courses(code) on update cascade     --ارتباطات شرحناها فوق 
);
""")

#الخطة الدراسية
cur.execute("""
create table if not exists program_plans(
program text not null, --اسم الخطة
level integer not null check (level >= 1), -- اللفل
course_code text not null,                  -- المادة 
primary key (program, level, course_code),    -- شروط سبق وان شرحناها
foreign key (course_code) references courses(code) on delete restrict on update cascade --ارتباطات سبق وان  شرحناها
);
""")



con.commit()
con.close()