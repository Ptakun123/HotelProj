from flask_sqlalchemy import SQLAlchemy
import hashlib

from extensions import db

class Hotel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.Text, nullable=False)
    price_per_night = db.Column(db.Float, nullable=False)
    amenities = db.Column(db.Text)  # Lista udogodnień
    image_url = db.Column(db.Text)  # Ścieżka do zdjęcia hotelu

class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(2), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    street = db.Column(db.String(50), nullable=False)
    building = db.Column(db.String(5), nullable=False)
    zip_code = db.Column(db.String(15), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(64), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(19), nullable=False)
    role = db.Column(db.String(10), nullable=False)

    def set_password(self, password):
        # Generowanie hasha SHA-256 (64 znaki hex)
        sha256_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        self.password_hash = sha256_hash

    def check_password(self, password):
        # Weryfikacja hasha SHA-256
        sha256_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        return self.password_hash == sha256_hash

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    capacity = db.Column(db.SmallInteger, nullable=False)
    price_per_night = db.Column(db.Numeric(6, 2), nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_night = db.Column(db.Date, nullable=False)
    last_night = db.Column(db.Date, nullable=False)
    full_name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    bill_type = db.Column(db.String(1), nullable=False)
    NIP = db.Column(db.String(20))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class HotelFacility(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    facility_name = db.Column(db.String(50), unique=True, nullable=False)

class RoomFacility(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    facility_name = db.Column(db.String(50), unique=True, nullable=False)

class HotelHotelFacility(db.Model):
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), primary_key=True)
    hotel_facility_id = db.Column(db.Integer, db.ForeignKey('hotel_facility.id'), primary_key=True)

class RoomRoomFacility(db.Model):
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), primary_key=True)
    room_facility_id = db.Column(db.Integer, db.ForeignKey('room_facility.id'), primary_key=True)