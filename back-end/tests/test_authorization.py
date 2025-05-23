import unittest
from datetime import date
from flask import Flask
from flaskr.authorization import auth_bp
from flaskr.extensions import db
from flaskr.models import User
from werkzeug.security import generate_password_hash
from flask_jwt_extended import JWTManager


class AuthorizationTestCase(unittest.TestCase):
    def setUp(self):
        # Tworzymy aplikację testową
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["JWT_SECRET_KEY"] = "test"
        db.init_app(self.app)
        JWTManager(self.app)
        self.app.register_blueprint(auth_bp, url_prefix="/auth")
        with self.app.app_context():
            db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register_success(self):
        payload = {
            "email": "test@example.com",
            "password": "StrongPass1",
            "birth_date": "2000-01-01",
            "first_name": "Jan",
            "last_name": "Kowalski",
            "phone_number": "123456789",
            "role": "user",
        }
        response = self.client.post("/auth/register", json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertIn(
            "Rejestracja zakończona pomyślnie", response.get_json().get("message", "")
        )

    def test_register_duplicate_email(self):
        with self.app.app_context():
            user = User(
                email="test@example.com",
                password_hash=generate_password_hash("StrongPass1"),
                birth_date=date(year=2000, month=1, day=1),
                first_name="Jan",
                last_name="Kowalski",
                phone_number="123456789",
                role="user",
            )
            db.session.add(user)
            db.session.commit()
        payload = {
            "email": "test@example.com",
            "password": "StrongPass1",
            "birth_date": "2000-01-01",
            "first_name": "Jan",
            "last_name": "Kowalski",
            "phone_number": "123456789",
            "role": "user",
        }
        response = self.client.post("/auth/register", json=payload)
        self.assertEqual(response.status_code, 409)
        self.assertIn(
            "Email jest już zarejestrowany", response.get_json().get("error", "")
        )

    def test_register_missing_fields(self):
        payload = {
            "email": "test@example.com",
            "password": "StrongPass1",
        }
        response = self.client.post("/auth/register", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Brakujące wymagane pola", response.get_json().get("error", ""))

    def test_register_invalid_email(self):
        payload = {
            "email": "invalidemail",
            "password": "StrongPass1",
            "birth_date": "2000-01-01",
            "first_name": "Jan",
            "last_name": "Kowalski",
            "phone_number": "123456789",
            "role": "user",
        }
        response = self.client.post("/auth/register", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Niepoprawny format email", response.get_data(as_text=True))

    def test_register_invalid_password(self):
        payload = {
            "email": "test2@example.com",
            "password": "short",
            "birth_date": "2000-01-01",
            "first_name": "Jan",
            "last_name": "Kowalski",
            "phone_number": "123456789",
            "role": "user",
        }
        response = self.client.post("/auth/register", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Hasło", response.get_json().get("error", ""))

    def test_register_invalid_birth_date(self):
        payload = {
            "email": "test3@example.com",
            "password": "StrongPass1",
            "birth_date": "1890-01-01",
            "first_name": "Jan",
            "last_name": "Kowalski",
            "phone_number": "123456789",
            "role": "user",
        }
        response = self.client.post("/auth/register", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("data urodzenia", response.get_json().get("error", ""))

    def test_login_success(self):
        with self.app.app_context():
            user = User(
                email="test@example.com",
                password_hash=generate_password_hash("StrongPass1"),
                birth_date=date(year=2000, month=1, day=1),
                first_name="Jan",
                last_name="Kowalski",
                phone_number="123456789",
                role="user",
            )
            db.session.add(user)
            db.session.commit()
        payload = {"email": "test@example.com", "password": "StrongPass1"}
        response = self.client.post("/auth/login", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.get_json())

    def test_login_missing_fields(self):
        payload = {"email": "test@example.com"}
        response = self.client.post("/auth/login", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Wymagane pola: email i hasło", response.get_json().get("error", "")
        )

    def test_login_wrong_password(self):
        with self.app.app_context():
            user = User(
                email="test@example.com",
                password_hash=generate_password_hash("StrongPass1"),
                birth_date=date(year=2000, month=1, day=1),
                first_name="Jan",
                last_name="Kowalski",
                phone_number="123456789",
                role="user",
            )
            db.session.add(user)
            db.session.commit()
        payload = {"email": "test@example.com", "password": "WrongPassword"}
        response = self.client.post("/auth/login", json=payload)
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Nieprawidłowy email lub hasło", response.get_json().get("error", "")
        )

    def test_login_nonexistent_user(self):
        payload = {"email": "notfound@example.com", "password": "StrongPass1"}
        response = self.client.post("/auth/login", json=payload)
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Nieprawidłowy email lub hasło", response.get_json().get("error", "")
        )


if __name__ == "__main__":
    unittest.main()
