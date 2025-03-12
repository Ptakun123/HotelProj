import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)

# Konfiguracja połączenia z PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:securepassword@localhost:5432/hotel_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Wyłączenie powiadomień o modyfikacjach


db = SQLAlchemy(app)

@app.route('/')
def home():
    try:
        # Wykonaj zapytanie do bazy, aby sprawdzić połączenie
        result = db.session.execute(text('SELECT 1'))  # Proste zapytanie
        return "Połączenie z bazą danych działa!"
    except Exception as e:
        return f"Nie udało się połączyć z bazą danych: {e}"

@app.route('/test_db')
def test_db():
    try:
        # Próbujemy pobrać dane z tabeli
        users = db.session.execute(text('SELECT * FROM users LIMIT 1')).fetchall()
        if users:
            return f"Połączenie działa! Pierwszy użytkownik: {users[0]}"
        else:
            return "Połączenie działa, ale nie ma danych w tabeli 'users'."
    except Exception as e:
        return f"Nie udało się połączyć z bazą danych: {e}"
    

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )

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

    # a simple page that says hello
    @app.route("/hello")
    def hello():
        return "Hello, World!"

    return app
