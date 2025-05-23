import unittest
from datetime import date, datetime
from flaskr.models import User, Reservation, Hotel, Address
from mailer import (
    get_confirmation_email,
    get_cancellation_email,
    generate_invoice_attachment,
)


class MailerTestCase(unittest.TestCase):
    def setUp(self):
        self.user = User(
            email="test@example.com",
            first_name="Jan",
            last_name="Kowalski",
            phone_number="123456789",
            role="user",
            birth_date=date(2000, 1, 1),
        )
        self.hotel = Hotel(name="Hotel Testowy")
        self.address = Address(
            country="Polska",
            city="Warszawa",
            street="Marszałkowska",
            building="1A",
            zip_code="00-001",
        )
        self.reservation = Reservation(
            id_reservation=1,
            id_room=1,
            id_user=1,
            first_night=datetime(2024, 6, 1),
            last_night=datetime(2024, 6, 5),
            full_name="Jan Kowalski",
            price=500.0,
            bill_type="F",
            nip="1234567890",
            reservation_status="A",
        )

    def test_get_confirmation_email_content(self):
        email = get_confirmation_email(
            self.user, self.reservation, self.hotel, self.address
        )
        self.assertIn("Potwierdzenie rezerwacji hotelowej", email["subject"])
        self.assertIn(self.hotel.name, email["subject"])
        self.assertIn("Twoja rezerwacja została potwierdzona", email["body"])
        self.assertIn(self.address.city, email["body"])
        self.assertEqual(email["receiver_email"], self.user.email)
        self.assertIsNotNone(email["attachment"])

    def test_get_cancellation_email_content(self):
        email = get_cancellation_email(self.user, self.reservation, self.hotel)
        self.assertIn("Potwierdzenie anulowania rezerwacji hotelowej", email["subject"])
        self.assertIn(self.hotel.name, email["subject"])
        self.assertIn("Twoja rezerwacja została anulowana", email["body"])
        self.assertEqual(email["receiver_email"], self.user.email)

    def test_generate_invoice_attachment_faktura(self):
        attachment = generate_invoice_attachment(self.reservation, self.user)
        self.assertIn("faktura", attachment.get_filename())
        payload = attachment.get_payload(decode=True).decode("utf-8")
        self.assertIn("Faktura VAT", payload)
        self.assertIn(self.user.email, payload)
        self.assertIn(self.reservation.nip, payload)

    def test_generate_invoice_attachment_paragon(self):
        self.reservation.bill_type = "P"
        self.reservation.nip = None
        attachment = generate_invoice_attachment(self.reservation, self.user)
        self.assertIn("paragon", attachment.get_filename())
        payload = attachment.get_payload(decode=True).decode("utf-8")
        self.assertIn("Paragon", payload)
        self.assertIn(self.user.email, payload)


if __name__ == "__main__":
    unittest.main()
