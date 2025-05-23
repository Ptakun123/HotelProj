import unittest
from datetime import date
from flask import Flask
from flaskr.models import User, Address, Hotel, Room
from flaskr.extensions import db


class ModelsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        db.init_app(self.app)
        with self.app.app_context():
            db.create_all()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_user_password_hashing(self):
        user = User(
            email="test@example.com",
            first_name="Jan",
            last_name="Kowalski",
            phone_number="123456789",
            role="user",
            birth_date=date(2000, 1, 1),
        )
        user.set_password("StrongPass1")
        db.session.add(user)
        db.session.commit()
        self.assertTrue(user.check_password("StrongPass1"))
        self.assertFalse(user.check_password("WrongPass"))


if __name__ == "__main__":
    unittest.main()
