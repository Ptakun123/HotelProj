import os
from flask import Flask, jsonify
from datetime import timedelta
from sqlalchemy import text
from flask_cors import CORS
from flaskr.extensions import db
from flask_jwt_extended import JWTManager
from config import JWT_SECRET_KEY, SECRET_KEY, SQLALCHEMY_DATABASE_URI_ENV


def create_app(test_config=None):
    # Tworzy i konfiguruje aplikację Flask
    app = Flask(__name__, instance_relative_config=True)
    CORS(
        app,
        resources={r"/*": {"origins": "http://localhost:3000"}},
        supports_credentials=True,
    )

    # Konfiguracja podstawowa aplikacji
    app.config.from_mapping(
        SECRET_KEY=SECRET_KEY,
        SQLALCHEMY_DATABASE_URI=SQLALCHEMY_DATABASE_URI_ENV,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)  # Ważność tokenu JWT

    if test_config is None:
        # Ładowanie konfiguracji z pliku (jeśli istnieje)
        app.config.from_pyfile("config.py", silent=True)
    else:
        # Konfiguracja testowa
        app.config.from_mapping(test_config)

    # Tworzenie folderu instance (jeśli nie istnieje)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Inicjalizacja rozszerzeń
    jwt = JWTManager(app)
    db.init_app(app)

    # Rejestracja blueprintów
    from flaskr.authorization import auth_bp

    app.register_blueprint(auth_bp)

    from flaskr.endpoints import endp_bp

    app.register_blueprint(endp_bp)

    # Prosta trasa testowa sprawdzająca połączenie z bazą danych
    @app.route("/")
    def home():
        try:
            result = db.session.execute(text("SELECT 1"))
            return "Połączenie z bazą danych działa!"
        except Exception as e:
            return f"Nie udało się połączyć z bazą danych: {e}"

    # Trasa testowa do pobrania użytkowników z bazy
    @app.route("/test_db")
    def test_db():
        try:
            users = db.session.execute(text("SELECT * FROM users")).fetchall()
            if users:
                return f"Połączenie działa! Pierwszy użytkownik: {users}"
            return "Połączenie działa, ale nie ma danych w tabeli 'users'."
        except Exception as e:
            return f"Nie udało się połączyć z bazą danych: {e}"

    @app.route("/hello")
    def hello():
        return "Hello, World!"

    # Obsługa błędów JWT
    @jwt.unauthorized_loader
    def unauthorized_callback(reason):
        return (
            jsonify({"error": "Brak lub nieprawidłowy token JWT", "details": reason}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return jsonify({"error": "Nieprawidłowy token JWT", "details": reason}), 422

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Token JWT wygasł"}), 401

    return app


# Tworzenie instancji aplikacji
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
