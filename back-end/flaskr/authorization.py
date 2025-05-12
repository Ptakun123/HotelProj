from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from models import User
from datetime import timedelta, datetime
from validators import validate_birth_date, validate_email, validate_password
from extensions import db
import hashlib

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    # Lista obowiązkowych pól
    required_fields = [
        'email', 'password', 
        'birth_date', 'first_name', 'last_name',
        'phone_number', 'role'
    ]
    
    data = request.get_json()
    
    if not data or any(field not in data for field in required_fields):
        missing = [f for f in required_fields if f not in data]
        return jsonify({
            "error": "Brakujące wymagane pola",
            "missing": missing
        }), 400

    # Walidacja emaila
    is_valid_email, email_error = validate_email(data['email'])
    if not is_valid_email:
        return jsonify({"error": email_error}), 400

    # Walidacja hasła
    is_valid_pass, pass_error = validate_password(data['password'])
    if not is_valid_pass:
        return jsonify({"error": pass_error}), 400

    # Walidacja daty urodzenia
    is_valid_date, date_result = validate_birth_date(data['birth_date'])
    if not is_valid_date:
        return jsonify({"error": date_result}), 400
    birth_date = date_result  # Poprawnie sparsowana data

    # Sprawdzenie unikalności
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email jest już zarejestrowany"}), 409

    # Rejestracja użytkownika
    try:
        new_user = User(
            email=data['email'],
            password_hash=hashlib.sha256(data['password'].encode('utf-8')).hexdigest(),
            birth_date=birth_date,
            first_name=data['first_name'].strip(),
            last_name=data['last_name'].strip(),
            phone_number=data['phone_number'],
            role=data['role']
        )
        
        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "message": "Rejestracja zakończona pomyślnie",
            "user": {
                "id_user": new_user.id_user,
                "email": new_user.email,
                "first_name": new_user.first_name,
                "last_name": new_user.last_name
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Błąd podczas rejestracji", "details": str(e)}), 500
    
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Walidacja danych wejściowych
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Wymagane pola: email i hasło"}), 400

    try:
        # Znajdź użytkownika po emailu
        user = User.query.filter_by(email=data['email']).first()
        
        # Sprawdź czy użytkownik istnieje i hasło jest poprawne
        if not user or not user.check_password(data['password']):
            return jsonify({"error": "Nieprawidłowy email lub hasło"}), 401
        
        # Generuj tokeny JWT
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name
            }
        }), 200

    except Exception as e:
        return jsonify({"error": "Błąd podczas logowania", "details": str(e)}), 500