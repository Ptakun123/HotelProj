import re
from datetime import datetime

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(pattern, email):
        return False, "Niepoprawny format email"
    return True, None

def validate_password(password):
    if len(password) < 8:
        return False, "Hasło musi mieć co najmniej 8 znaków"
    if not any(char.isdigit() for char in password):
        return False, "Hasło musi zawierać co najmniej jedną cyfrę"
    if not any(char.isupper() for char in password):
        return False, "Hasło musi zawierać co najmniej jedną wielką literę"
    return True, None

def validate_birth_date(date_str):
    try:
        birth_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        if birth_date.year < 1900 or birth_date >= datetime.now().date():
            return False, "Nieprawidłowa data urodzenia"
        return True, birth_date 
    except ValueError:
        return False, "Data powinna być w formacie YYYY-MM-DD"