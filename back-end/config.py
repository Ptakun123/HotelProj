import os
from dotenv import load_dotenv

load_dotenv()

# Konfiguracja Mailera
SMTP_SERVER = "smtp.sendgrid.net"
SMTP_PORT = 465
SMTP_USERNAME = "apikey"
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = "uaim_proj_hotel@outlook.com"
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

# Konfiguracja Flask
SQLALCHEMY_DATABASE_URI_ENV = os.getenv("SQLALCHEMY_DATABASE_URI")
SECRET_KEY = os.getenv("SECRET_KEY")
