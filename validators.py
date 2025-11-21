# ------------------------------------------------------
#  Simple Validation Functions for GUI (PyQt Compatible)
# ------------------------------------------------------

def validate_student_id(student_id: str):
    """
    Validate student ID.
    Returns:
        None if valid,
        or an error message string.
    """
    if not student_id:
        return "Student ID is required."
    if " " in student_id:
        return "Student ID cannot contain spaces."
    if not student_id.isdigit():
        return "Student ID must contain numbers only."
    if len(student_id) != 7:
        return "Student ID must be 7 digits."
    return None


def validate_email(email: str):
    """
    Validate email format.
    Returns:
        None if valid,
        or an error message string.
    """
    if not email:
        return "Email is required."
    if " " in email:
        return "Email cannot contain spaces."
    if email.count("@") != 1:
        return "Invalid email format."

    local, domain = email.split("@")

    if not local:
        return "Invalid email format."
    if "." not in domain:
        return "Invalid email format."
    if domain.startswith("."):
        return "Invalid email format."
    if not domain[-1].isalnum():
        return "Invalid email format."

    wrong_domains = {
        "gamil.com", "gmial.com", "gmai.com", "gmal.com",
        "gmaiil.com", "gmail.co", "gmail.con", "gnail.com",
        "gmail.comm", "gmai.con",
        "hotmil.com", "hotmal.com", "hotmial.com",
        "hotmai.com", "hotnail.com", "homtail.com",
        "outlok.com", "outllok.com", "ootlook.com",
        "outloook.com", "outloo.com",
    }

    if domain.lower() in wrong_domains:
        return "Invalid email format."

    return None



def validate_full_name(full_name: str):
    """
    Validate a full name (First Middle Last).
    Returns:
        (parts, None) if valid, where parts is [first, middle, last]
        (None, error_message) if invalid.
    """
    cleaned = " ".join(full_name.split())
    lowered = cleaned.lower()

    if not lowered.replace(" ", "").isalpha():
        return None, "الاسم يجب أن يحتوي على حروف فقط بدون أرقام أو رموز."

    parts = lowered.title().split()

    if len(parts) != 3:
        return None, "الرجاء إدخال اسم ثلاثي فقط."

    if any(len(p) < 3 for p in parts):
        return None, "كل اسم يجب أن يكون 3 أحرف أو أكثر."

    return parts, None
