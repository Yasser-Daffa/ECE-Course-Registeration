import re  # For pattern matching
import bcrypt

#from PyQt6 import QtWidgets, QtCore

def is_valid_password(password):
    """
    Validates a password using regex rules and length.
    Keeps prompting the user until all conditions are satisfied.
    """

    while True:
        # 1. Length check
        if len(password) >= 8:
            print("✅ Password length is sufficient.")
            length_ok = True
        else:
            print("❌ Password must be at least 8 characters long.")
            length_ok = False

        # 2. Character rules
        uppercase_ok = bool(re.search(r'[A-Z]', password))
        lowercase_ok = bool(re.search(r'[a-z]', password))
        digit_ok = bool(re.search(r'[0-9]', password))
        special_ok = bool(re.search(r'[=_/\\+!@#$%^&*(),.?\":{}|<>-]', password))

        # Print messages for each rule
        print("✅" if uppercase_ok else "❌", "Password must contain at least one uppercase letter.")
        print("✅" if lowercase_ok else "❌", "Password must contain at least one lowercase letter.")
        print("✅" if digit_ok else "❌", "Password must contain at least one digit.")
        print("✅" if special_ok else "❌", "Password must contain at least one special character.")

        # 3. If all rules are satisfied, return the password
        if length_ok and uppercase_ok and lowercase_ok and digit_ok and special_ok:
            while True:
                confirm_password = input("Please re-enter your password for confirmation: ")
                if confirm_password == password:
                    print("✅ Password confirmed.")
                    break
                else:
                    print("❌ Passwords do not match. Please try again.")
            return password

        # 4. Otherwise, prompt user again
        password = input("\nPlease re-enter a valid password: ")


def check_password_strength(password):
    """
    Evaluates password strength based on length and character variety.
    """

    score = 0

    # Length contribution
    if len(password) >= 12:
        score += 2
    elif len(password) >= 8:
        score += 1

    # Character variety contribution
    if re.search(r'[A-Z]', password): score += 1
    if re.search(r'[a-z]', password): score += 1
    if re.search(r'[0-9]', password): score += 1
    if re.search(r'[=_/\\+!@#$%^&*(),.?\":{}|<>-]', password): score += 1

    # Determine strength
    if score >= 6:
        return "Strong password."
    elif 4 <= score < 6:
        return "Moderate password — consider adding more variety or length."
    else:
        return "Weak password — too short or missing key elements."
    
def hash_pass(password) -> bytes:
    """
    Hashes a password using bcrypt.
    Returns the hashed password as bytes.
    """
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password

def main(password):
    valid_password = is_valid_password(password)
    print("\nPassword Strength:", check_password_strength(valid_password))
    hashed_password = hash_pass(password)
    print("Hashed Password:", hashed_password)
    return hashed_password



# Main program
password = input("Enter password to validate: ")
main(password)



# Check if the input password matches the hashed password to login after registration
def verify_password(password, hashed_password) -> bool:
    """
    Verifies a password against a given bcrypt hash.
    Returns True if the password matches the hash, False otherwise.
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

Check_password_match = input("Re-enter your password to login: ")
hashed_password = hash_pass(password)
if verify_password(Check_password_match, hashed_password):
    print("welcome")