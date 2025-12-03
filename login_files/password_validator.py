import re
import bcrypt

# ----------------------------------------
# 1) PASSWORD VALIDATION (NO LOOPS, NO I/O)
# ----------------------------------------

def validate_password(password: str) -> tuple[bool, list]:
    """
    Validates a password against a set of common security rules.
    
    Paramaters:
    - password (str): The password string to validate.
    
    returns:
    - tuple[bool, list]: 
        - First element: True if password passes all rules, False otherwise.
        - Second element: A list of error messages for rules that failed.

    Rules checked:
    1. Minimum length of 8 characters
    2. At least one uppercase letter
    3. At least one lowercase letter
    4. At least one numeric digit
    5. At least one special character
    """

    # Initialize an empty list to collect any rule violations
    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")

    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter.")

    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter.")

    if not re.search(r"[0-9]", password):
        errors.append("Password must contain at least one digit.")

    if not re.search(r"[=_`/\\+!@#$%^&*(),.?\"':;{}|<>-]", password):
        errors.append("Password must contain at least one special character.")

    return (len(errors) == 0, errors)



# ----------------------------------------
# 2) PASSWORD STRENGTH
# ----------------------------------------

def password_strength(password: str) -> str:
    """
    Returns basic human-readable strength evaluation.
    """

    score = 0

    # Length contribution
    if len(password) >= 12:
        score += 2
    elif len(password) >= 8:
        score += 1

    # Character variety
    if re.search(r"[A-Z]", password): score += 1
    if re.search(r"[a-z]", password): score += 1
    if re.search(r"[0-9]", password): score += 1
    if re.search(r"[=_/\\+!@#$%^&*(),.?\":{}|<>-]", password): score += 1

    if score >= 5:
        return "Strong"
    elif score >= 3:
        return "Moderate"
    else:
        return "Weak"



# ----------------------------------------
# 3) HASHING
# ----------------------------------------

def hash_password(password: str) -> bytes:
    """
    Hash the password using bcrypt.
    Returns hashed bytes.
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())



# ----------------------------------------
# 4) VERIFY HASH
# ----------------------------------------

def verify_password(password: str, hashed: bytes) -> bool:
    """
    Checks if password matches the bcrypt hash.
    """
    return bcrypt.checkpw(password.encode("utf-8"), hashed)
