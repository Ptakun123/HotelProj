from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash
from models import User, db
from datetime import timedelta, datetime
from validators import validate_birth_date, validate_email, validate_password

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    # Lista obowiązkowych pól
    required_fields = [
        'email', 'password', 'username',
        'birth_date', 'first_name', 'last_name'
    ]
    
    # Sprawdzenie obecności wszystkich pól
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
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Nazwa użytkownika jest zajęta"}), 409

    # Rejestracja użytkownika
    try:
        new_user = User(
            email=data['email'],
            username=data['username'],
            password_hash=generate_password_hash(data['password']),
            birth_date=birth_date,
            first_name=data['first_name'].strip(),
            last_name=data['last_name'].strip()
        )
        
        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "message": "Rejestracja zakończona pomyślnie",
            "user": {
                "id": new_user.id,
                "username": new_user.username,
                "email": new_user.email,
                "first_name": new_user.first_name,
                "last_name": new_user.last_name,
                "birth_date": new_user.birth_date.isoformat()
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Błąd podczas rejestracji",
            "details": str(e)
        }), 500
    
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()

    if not user or not user.check_password(data.get('password')):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(
        identity=user.id,
        expires_delta=timedelta(hours=1)
    )
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer"
    }), 200