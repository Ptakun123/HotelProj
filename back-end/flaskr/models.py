from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from flaskr.extensions import db


class Address(db.Model):
    __tablename__ = "addresses"  # Określenie nazwy tabeli
    id_address = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(2), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    street = db.Column(db.String(50), nullable=False)
    building = db.Column(db.String(5), nullable=False)
    zip_code = db.Column(db.String(15), nullable=False)


class Hotel(db.Model):
    __tablename__ = "hotels"  # Określenie nazwy tabeli
    id_hotel = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    geo_length = db.Column(db.Float, nullable=False)
    geo_latitude = db.Column(db.Float, nullable=False)
    stars = db.Column(db.SmallInteger, nullable=False)
    id_address = db.Column(
        db.Integer, db.ForeignKey("addresses.id_address"), nullable=False
    )

class HotelImage(db.Model):
    __tablename__ = "hotel_images"
    id_image = db.Column(db.Integer, primary_key=True)
    id_hotel = db.Column(db.Integer, db.ForeignKey("hotels.id_hotel"), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(100))
    is_main = db.Column(db.Boolean, default=False)


class User(db.Model):
    __tablename__ = "users"  # Określenie nazwy tabeli
    id_user = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(19), nullable=False)
    role = db.Column(db.String(10), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Room(db.Model):
    __tablename__ = "rooms"  # Określenie nazwy tabeli
    id_room = db.Column(db.Integer, primary_key=True)
    capacity = db.Column(db.SmallInteger, nullable=False)
    price_per_night = db.Column(db.Numeric(6, 2), nullable=False)
    id_hotel = db.Column(db.Integer, db.ForeignKey("hotels.id_hotel"), nullable=False)


class Reservation(db.Model):
    __tablename__ = "reservations"  # Określenie nazwy tabeli
    id_reservation = db.Column(db.Integer, primary_key=True)
    first_night = db.Column(db.Date, nullable=False)
    last_night = db.Column(db.Date, nullable=False)
    full_name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    bill_type = db.Column(db.String(1), nullable=False)
    nip = db.Column(db.String(20), nullable=True)
    reservation_status = db.Column(db.String(1), nullable=False)
    id_room = db.Column(db.Integer, db.ForeignKey("rooms.id_room"), nullable=False)
    id_user = db.Column(db.Integer, db.ForeignKey("users.id_user"), nullable=False)


class HotelFacility(db.Model):
    __tablename__ = "hotel_facilities"  # Określenie nazwy tabeli
    id_hotel_facility = db.Column(db.Integer, primary_key=True)
    facility_name = db.Column(db.String(50), unique=True, nullable=False)


class RoomFacility(db.Model):
    __tablename__ = "room_facilities"  # Określenie nazwy tabeli
    id_room_facility = db.Column(db.Integer, primary_key=True)
    facility_name = db.Column(db.String(50), unique=True, nullable=False)


class HotelHotelFacility(db.Model):
    __tablename__ = "hotels_hotel_facilities"  # Określenie nazwy tabeli
    id_hotel = db.Column(db.Integer, db.ForeignKey("hotels.id_hotel"), primary_key=True)
    id_hotel_facility = db.Column(
        db.Integer,
        db.ForeignKey("hotel_facilities.id_hotel_facility"),
        primary_key=True,
    )


class RoomRoomFacility(db.Model):
    __tablename__ = "rooms_room_facilities"  # Określenie nazwy tabeli
    id_room = db.Column(db.Integer, db.ForeignKey("rooms.id_room"), primary_key=True)
    id_room_facility = db.Column(
        db.Integer, db.ForeignKey("room_facilities.id_room_facility"), primary_key=True
    )
