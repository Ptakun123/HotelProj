import re
from datetime import datetime

def validate_email(email):
    """Basic email validation"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Password requirements check"""
    if len(password) < 8:
        return "Password must be at least 8 characters"
    if not any(char.isdigit() for char in password):
        return "Password must contain at least one number"
    if not any(char.isupper() for char in password):
        return "Password must contain at least one uppercase letter"
    return None

def validate_birth_date(date_str):
    try:
        birth_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        if birth_date.year < 1900 or birth_date >= datetime.now().date():
            return "Invalid birth date"
        return None
    except ValueError:
        return "Date format should be YYYY-MM-DD"