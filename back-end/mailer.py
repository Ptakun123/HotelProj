import datetime
import ssl
from config import (
    SMTP_SERVER,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_PASSWORD,
    FROM_EMAIL,
    TIMEZONE,
)
from smtplib import SMTP_SSL
from zoneinfo import ZoneInfo
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flaskr.models import Reservation


context = ssl.create_default_context()


def send_email(receiver_email: str, email: dict):
    # Create a MIME message
    message = MIMEMultipart()
    message["From"] = FROM_EMAIL
    message["To"] = receiver_email
    message["Subject"] = email["subject"]

    # Add the email body
    message.attach(MIMEText(email["body"], "plain"))

    # Send the email
    with SMTP_SSL(SMTP_SERVER, SMTP_PORT, context) as server:
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(FROM_EMAIL, receiver_email, message.as_string())


def get_confirmation_email(reservation: Reservation) -> dict:
    pass


def get_cancellation_email(reservation: Reservation) -> dict:
    pass
