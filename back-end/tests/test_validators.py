import unittest
from flaskr.validators import validate_email, validate_password, validate_birth_date


class ValidatorsTestCase(unittest.TestCase):

    # Test poprawnego adresu email
    def test_validate_email_correct(self):
        valid, msg = validate_email("test@example.com")
        self.assertTrue(valid)
        self.assertIsNone(msg)

    # Test niepoprawnego adresu email
    def test_validate_email_incorrect(self):
        valid, msg = validate_email("testexample.com")
        self.assertFalse(valid)
        self.assertIsNotNone(msg)

    # Test poprawnego hasła
    def test_validate_password_correct(self):
        valid, msg = validate_password("StrongPass1")
        self.assertTrue(valid)
        self.assertIsNone(msg)

    # Test hasła zbyt krótkiego
    def test_validate_password_too_short(self):
        valid, msg = validate_password("Abc1")
        self.assertFalse(valid)
        self.assertIn("co najmniej 8 znaków", msg)

    # Test hasła bez cyfry
    def test_validate_password_no_digit(self):
        valid, msg = validate_password("Abcdefgh")
        self.assertFalse(valid)
        self.assertIn("co najmniej jedną cyfrę", msg)

    # Test hasła bez wielkiej litery
    def test_validate_password_no_upper(self):
        valid, msg = validate_password("abcdefgh1")
        self.assertFalse(valid)
        self.assertIn("co najmniej jedną wielką literę", msg)

    # Test poprawnej daty urodzenia
    def test_validate_birth_date_correct(self):
        valid, result = validate_birth_date("2000-01-01")
        self.assertTrue(valid)
        self.assertIsNotNone(result)

    # Test daty urodzenia w przyszłości
    def test_validate_birth_date_future(self):
        from datetime import datetime, timedelta

        future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        valid, msg = validate_birth_date(future_date)
        self.assertFalse(valid)
        self.assertIn("Nieprawidłowa data urodzenia", msg)

    # Test zbyt starej daty urodzenia
    def test_validate_birth_date_too_old(self):
        valid, msg = validate_birth_date("1899-12-31")
        self.assertFalse(valid)
        self.assertIn("Nieprawidłowa data urodzenia", msg)

    # Test niepoprawnego formatu daty urodzenia
    def test_validate_birth_date_wrong_format(self):
        valid, msg = validate_birth_date("01-01-2000")
        self.assertFalse(valid)
        self.assertIn("formacie YYYY-MM-DD", msg)


if __name__ == "__main__":
    unittest.main()
