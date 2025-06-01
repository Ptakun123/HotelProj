import ssl
from config import (
    SMTP_SERVER,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_PASSWORD,
    FROM_EMAIL,
)
from smtplib import SMTP_SSL
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flaskr.models import Reservation, User, Hotel, Address

# Kontekst SSL do bezpiecznego połączenia SMTP
context = ssl.create_default_context()


def send_email(email: dict):
    # Tworzenie wiadomości MIME
    message = MIMEMultipart()
    message["From"] = FROM_EMAIL
    message["To"] = email["receiver_email"]
    message["Subject"] = email["subject"]

    # Dodanie treści wiadomości
    message.attach(MIMEText(email["body"], "plain"))

    # Wysyłka wiadomości przez SMTP z użyciem SSL
    with SMTP_SSL(SMTP_SERVER, SMTP_PORT, context) as server:
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(FROM_EMAIL, email["receiver_email"], message.as_string())


def get_confirmation_email(
    user: User, reservation: Reservation, hotel: Hotel, address: Address
) -> dict:
    # Generuje treść maila potwierdzającego rezerwację
    receiver_email = user.email
    subject = f"Potwierdzenie rezerwacji hotelowej w obiekcie {hotel.name}"
    body = (
        f"Szanowny/a {user.first_name} {user.last_name},\n\n"
        f"Twoja rezerwacja została potwierdzona.\n"
        f"Hotel: {hotel.name}\n"
        f"Adres: {address.street} {address.building}, {address.zip_code} {address.city}, {address.country}\n"
        f"Numer rezerwacji: {reservation.id_reservation}\n"
        f"Termin pobytu: {reservation.first_night.strftime('%Y-%m-%d')} - {reservation.last_night.strftime('%Y-%m-%d')}\n"
        f"Zapłacona kwota: {reservation.price} PLN\n"
        f"Typ dokumentu: {'Faktura' if reservation.bill_type == 'F' else 'Paragon'}\n\n"
        f"W załączniku znajdziesz dokument potwierdzający rezerwację.\n\n"
        f"Pozdrawiamy,\nZespół Hotelu"
    )
    attachment = generate_invoice_attachment(reservation, user)
    return {
        "receiver_email": receiver_email,
        "subject": subject,
        "body": body,
        "attachment": attachment,
    }


def get_cancellation_email(user: User, reservation: Reservation, hotel: Hotel) -> dict:
    # Generuje treść maila potwierdzającego anulowanie rezerwacji
    receiver_email = user.email
    subject = f"Potwierdzenie anulowania rezerwacji hotelowej w obiekcie {hotel.name}"
    body = (
        f"Szanowny/a {user.first_name} {user.last_name},\n\n"
        f"Twoja rezerwacja została anulowana.\n"
        f"Hotel: {hotel.name}\n"
        f"Numer rezerwacji: {reservation.id_reservation}\n"
        f"Termin pobytu: {reservation.first_night.strftime('%Y-%m-%d')} - {reservation.last_night.strftime('%Y-%m-%d')}\n"
        f"Kwota: {reservation.price} PLN\n"
        f"Typ dokumentu: {'Faktura' if reservation.bill_type == 'F' else 'Paragon'}\n\n"
        f"Pozdrawiamy,\nZespół Hotelu"
    )
    return {"receiver_email": receiver_email, "subject": subject, "body": body}


def generate_invoice_attachment(reservation: Reservation, user: User) -> MIMEBase:
    # Generuje załącznik z fakturą lub paragonem na podstawie danych rezerwacji
    if reservation.bill_type == "F":
        doc_type = "Faktura VAT"
        filename = f"faktura_{reservation.id_reservation}.txt"
    else:
        doc_type = "Paragon"
        filename = f"paragon_{reservation.id_reservation}.txt"

    content = (
        f"{doc_type}\n"
        f"Numer: {reservation.id_reservation}\n"
        f"Data: {reservation.first_night.strftime('%Y-%m-%d')} - {reservation.last_night.strftime('%Y-%m-%d')}\n"
        f"Imię i nazwisko: {reservation.full_name}\n"
        f"Email: {user.email}\n"
        f"Kwota: {reservation.price} PLN\n"
    )
    if reservation.bill_type == "F" and reservation.nip:
        content += f"NIP: {reservation.nip}\n"

    attachment = MIMEBase("application", "octet-stream")
    attachment.set_payload(content.encode("utf-8"))
    encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", f'attachment; filename="{filename}"')
    return attachment
