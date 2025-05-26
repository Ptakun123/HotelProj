import os
from flask import Flask
from datetime import timedelta
from sqlalchemy import text
from flaskr.extensions import db
from flask_jwt_extended import JWTManager


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # Konfiguracja domyślna
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="postgresql://admin:securepassword@db:5432/hotel_db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    app.config["JWT_SECRET_KEY"] = (
        "tajny-klucz-123"  # Klucz do JWT (w produkcji użyj zmiennej środowiskowej!)
    )
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)  # Ważność tokenu

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize extensions
    jwt = JWTManager(app)
    db.init_app(app)

    # Register blueprints
    from flaskr.authorization import auth_bp

    app.register_blueprint(auth_bp)

    from flaskr.endpoints import endp_bp

    app.register_blueprint(endp_bp)

    # Routes
    @app.route("/")
    def home():
        try:
            result = db.session.execute(text("SELECT 1"))
            return "Połączenie z bazą danych działa!"
        except Exception as e:
            return f"Nie udało się połączyć z bazą danych: {e}"

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

    return app


# Create app instance
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
