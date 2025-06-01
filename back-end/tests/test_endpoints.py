import unittest
from datetime import date, timedelta
from flask import Flask, json
from flaskr.endpoints import endp_bp
from flaskr.extensions import db
from flask_jwt_extended import create_access_token, JWTManager
from werkzeug.security import generate_password_hash
from flaskr.models import (
    Address,
    Hotel,
    Room,
    RoomFacility,
    HotelFacility,
    RoomRoomFacility,
    HotelHotelFacility,
    Reservation,
    User,
    HotelImage,
)


class SearchFreeRoomsTestCase(unittest.TestCase):
    def setUp(self):
        # Konfiguracja aplikacji Flask i bazy danych do testów.
        # Tworzy przykładowe adresy, hotele, pokoje, udogodnienia, użytkownika i rezerwację.
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        db.init_app(self.app)
        self.app.register_blueprint(endp_bp, url_prefix="")
        with self.app.app_context():
            db.create_all()
            # Dane testowe: adresy
            address1 = Address(
                country="Polska",
                city="Warszawa",
                street="Testowa",
                building="1",
                zip_code="00-001",
            )
            address2 = Address(
                country="Niemcy",
                city="Berlin",
                street="Teststrasse",
                building="2",
                zip_code="10115",
            )
            address3 = Address(
                country="Polska",
                city="Kraków",
                street="Krakowska",
                building="3",
                zip_code="30-001",
            )
            db.session.add_all([address1, address2, address3])
            db.session.commit()
            # Dane testowe: hotele
            hotel1 = Hotel(
                name="Hotel Warszawa",
                stars=4,
                geo_length=21.0122,
                geo_latitude=52.2297,
                id_address=address1.id_address,
            )
            hotel2 = Hotel(
                name="Hotel Berlin",
                stars=5,
                geo_length=13.4050,
                geo_latitude=52.5200,
                id_address=address2.id_address,
            )
            hotel3 = Hotel(
                name="Hotel Kraków",
                stars=3,
                geo_length=19.9449799,
                geo_latitude=50.0646501,
                id_address=address3.id_address,
            )
            db.session.add_all([hotel1, hotel2, hotel3])
            db.session.commit()
            # Dane testowe: pokoje
            room1 = Room(id_hotel=hotel1.id_hotel, capacity=2, price_per_night=200)
            room2 = Room(id_hotel=hotel2.id_hotel, capacity=3, price_per_night=300)
            room3 = Room(id_hotel=hotel3.id_hotel, capacity=1, price_per_night=150)
            db.session.add_all([room1, room2, room3])
            db.session.commit()
            # Dane testowe: udogodnienia pokoi
            rf_wifi = RoomFacility(facility_name="wifi")
            rf_tv = RoomFacility(facility_name="tv")
            db.session.add_all([rf_wifi, rf_tv])
            db.session.commit()
            db.session.add_all(
                [
                    RoomRoomFacility(
                        id_room=room1.id_room, id_room_facility=rf_wifi.id_room_facility
                    ),
                    RoomRoomFacility(
                        id_room=room2.id_room, id_room_facility=rf_tv.id_room_facility
                    ),
                    RoomRoomFacility(
                        id_room=room3.id_room, id_room_facility=rf_wifi.id_room_facility
                    ),
                ]
            )
            db.session.commit()
            # Dane testowe: udogodnienia hotelowe
            hf_pool = HotelFacility(facility_name="basen")
            hf_gym = HotelFacility(facility_name="siłownia")
            db.session.add_all([hf_pool, hf_gym])
            db.session.commit()
            db.session.add_all(
                [
                    HotelHotelFacility(
                        id_hotel=hotel1.id_hotel,
                        id_hotel_facility=hf_pool.id_hotel_facility,
                    ),
                    HotelHotelFacility(
                        id_hotel=hotel2.id_hotel,
                        id_hotel_facility=hf_gym.id_hotel_facility,
                    ),
                    HotelHotelFacility(
                        id_hotel=hotel3.id_hotel,
                        id_hotel_facility=hf_pool.id_hotel_facility,
                    ),
                ]
            )
            db.session.commit()
            # Dane testowe: użytkownik do rezerwacji
            from flaskr.models import User

            user = User(
                email="test@example.com",
                password_hash="hash",
                birth_date=date(2000, 1, 1),
                first_name="Jan",
                last_name="Kowalski",
                phone_number="123456789",
                role="user",
            )
            db.session.add(user)
            db.session.commit()
            # Dane testowe: rezerwacja pokoju (pokój zajęty w określonym terminie)
            today = date.today()
            res = Reservation(
                id_room=room1.id_room,
                id_user=user.id_user,
                first_night=today + timedelta(days=2),
                last_night=today + timedelta(days=5),
                full_name="Jan Kowalski",
                price=600,
                bill_type="F",
                nip=None,
                reservation_status="A",
            )
            db.session.add(res)
            db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self):
        # Czyszczenie bazy po każdym teście
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # Test wyszukiwania pokoi - brak wymaganych pól
    def test_missing_required_fields(self):
        response = self.client.post("/search_free_rooms", json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Brak wymaganych pól", response.get_json().get("error", ""))

    # Test wyszukiwania pokoi - niepoprawny format liczby gości
    def test_invalid_required_formats(self):
        response = self.client.post(
            "/search_free_rooms",
            json={
                "start_date": "2024-01-01",
                "end_date": "2024-01-10",
                "guests": "dwóch",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Nieprawidłowy format daty lub liczby gości",
            response.get_json().get("error", ""),
        )

    # Test wyszukiwania pokoi - data końcowa przed początkową
    def test_end_date_before_start_date(self):
        response = self.client.post(
            "/search_free_rooms",
            json={"start_date": "2024-01-10", "end_date": "2024-01-01", "guests": 2},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Data początkowa musi być wcześniejsza",
            response.get_json().get("error", ""),
        )

    # Test wyszukiwania pokoi - liczba gości równa zero
    def test_zero_guests(self):
        response = self.client.post(
            "/search_free_rooms",
            json={"start_date": "2024-01-01", "end_date": "2024-01-10", "guests": 0},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Liczba gości musi być większa od zera",
            response.get_json().get("error", ""),
        )

    # Test wyszukiwania pokoi - niepoprawny format ceny
    def test_invalid_price_format(self):
        response = self.client.post(
            "/search_free_rooms",
            json={
                "start_date": "2024-01-01",
                "end_date": "2024-01-10",
                "guests": 2,
                "lowest_price": "sto",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Ceny muszą być liczbami", response.get_json().get("error", ""))

    # Test wyszukiwania pokoi - najniższa cena większa niż najwyższa
    def test_lowest_price_greater_than_highest(self):
        response = self.client.post(
            "/search_free_rooms",
            json={
                "start_date": "2024-01-01",
                "end_date": "2024-01-10",
                "guests": 2,
                "lowest_price": 500,
                "highest_price": 100,
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Najwyższa dopuszczalna cena nie może być mniejsza",
            response.get_json().get("error", ""),
        )

    # Test wyszukiwania pokoi - niepoprawny format udogodnień pokoju
    def test_invalid_room_facilities_format(self):
        response = self.client.post(
            "/search_free_rooms",
            json={
                "start_date": "2024-01-01",
                "end_date": "2024-01-10",
                "guests": 2,
                "room_facilities": "wifi",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Udogodnienia pokoi muszą być listą stringów",
            response.get_json().get("error", ""),
        )

    # Test wyszukiwania pokoi - niepoprawny format udogodnień hotelu
    def test_invalid_hotel_facilities_format(self):
        response = self.client.post(
            "/search_free_rooms",
            json={
                "start_date": "2024-01-01",
                "end_date": "2024-01-10",
                "guests": 2,
                "hotel_facilities": "basen",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Udogodnienia hotelu muszą być listą stringów",
            response.get_json().get("error", ""),
        )

    # Test wyszukiwania pokoi - niepoprawny format krajów
    def test_invalid_countries_format(self):
        response = self.client.post(
            "/search_free_rooms",
            json={
                "start_date": "2024-01-01",
                "end_date": "2024-01-10",
                "guests": 2,
                "countries": "Polska",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Państwa muszą być listą stringów", response.get_json().get("error", "")
        )

    # Test wyszukiwania pokoi - niepoprawny format miast
    def test_invalid_cities_format(self):
        response = self.client.post(
            "/search_free_rooms",
            json={
                "start_date": "2024-01-01",
                "end_date": "2024-01-10",
                "guests": 2,
                "city": "Warszawa",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Miasta muszą być listą stringów", response.get_json().get("error", "")
        )

    # Test wyszukiwania pokoi - niepoprawny format liczby gwiazdek
    def test_invalid_stars_format(self):
        response = self.client.post(
            "/search_free_rooms",
            json={
                "start_date": "2024-01-01",
                "end_date": "2024-01-10",
                "guests": 2,
                "min_hotel_stars": "cztery",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Liczby gwiazdek hotelu muszą być liczbami całkowitymi",
            response.get_json().get("error", ""),
        )

    # Test wyszukiwania pokoi - minimalna liczba gwiazdek większa niż maksymalna
    def test_min_stars_greater_than_max(self):
        response = self.client.post(
            "/search_free_rooms",
            json={
                "start_date": "2024-01-01",
                "end_date": "2024-01-10",
                "guests": 2,
                "min_hotel_stars": 5,
                "max_hotel_stars": 2,
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Najwyższa dopuszczalna liczba gwiazdek nie może być mniejsza",
            response.get_json().get("error", ""),
        )

    # Test wyszukiwania pokoi - niepoprawny format sortowania
    def test_invalid_sort_by_format(self):
        response = self.client.post(
            "/search_free_rooms",
            json={
                "start_date": "2024-01-01",
                "end_date": "2024-01-10",
                "guests": 2,
                "sort_by": 123,
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Nieprawidłowy parametr sortowania", response.get_json().get("error", "")
        )

    # Test wyszukiwania pokoi - niepoprawna wartość sortowania
    def test_invalid_sort_by_value(self):
        response = self.client.post(
            "/search_free_rooms",
            json={
                "start_date": "2024-01-01",
                "end_date": "2024-01-10",
                "guests": 2,
                "sort_by": "invalid",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Nieprawidłowy parametr sortowania", response.get_json().get("error", "")
        )

    # Test wyszukiwania pokoi - niepoprawna wartość sort_order
    def test_invalid_sort_order_value(self):
        response = self.client.post(
            "/search_free_rooms",
            json={
                "start_date": "2024-01-01",
                "end_date": "2024-01-10",
                "guests": 2,
                "sort_by": "price",
                "sort_order": "wrong",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Nieprawidłowy parametr porządku sortowania",
            response.get_json().get("error", ""),
        )

    # Test wyszukiwania pokoi - poprawne zapytanie z filtrem po kraju
    def test_query_with_country(self):
        response = self.client.post(
            "/search_free_rooms",
            json={
                "start_date": "2100-01-01",
                "end_date": "2100-01-10",
                "guests": 2,
                "countries": ["Polska"],
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("available_rooms", data)
        for room in data["available_rooms"]:
            self.assertEqual(
                room["country"], "Polska", msg=f"Room not in Polska: {room}"
            )

    # Test wyszukiwania pokoi - poprawne zapytanie z filtrem po mieście
    def test_query_with_city(self):
        response = self.client.post(
            "/search_free_rooms",
            json={
                "start_date": "2100-01-01",
                "end_date": "2100-01-10",
                "guests": 2,
                "city": ["Warszawa"],
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("available_rooms", data)
        for room in data["available_rooms"]:
            self.assertEqual(
                room["city"], "Warszawa", msg=f"Room not in Warszawa: {room}"
            )

    # Test wyszukiwania pokoi - zapytanie z krajem i miastem w innym kraju
    def test_query_with_country_and_city_in_other_country(self):
        response = self.client.post(
            "/search_free_rooms",
            json={
                "start_date": "2100-01-01",
                "end_date": "2100-01-10",
                "guests": 2,
                "countries": ["Niemcy"],
                "city": ["Warszawa"],
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("available_rooms", data)
        for room in data["available_rooms"]:
            if room["country"] == "Polska":
                self.assertEqual(
                    room["city"],
                    "Warszawa",
                    msg=f"Room in Poland is not in Warsaw: {room}",
                )
            else:
                self.assertEqual(
                    room["country"],
                    "Niemcy",
                    msg=f"Room outside of Poland is not in Germany: {room}",
                )

    # Test wyszukiwania pokoi - zapytanie z krajem i miastem w tym samym kraju
    def test_query_with_country_and_city_in_same_country(self):
        response = self.client.post(
            "/search_free_rooms",
            json={
                "start_date": "2100-01-01",
                "end_date": "2100-01-10",
                "guests": 2,
                "countries": ["Polska"],
                "city": ["Warszawa"],
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("available_rooms", data)
        for room in data["available_rooms"]:
            self.assertEqual(
                room["city"], "Warszawa", msg=f"Room not in Warszawa: {room}"
            )

    # Test wyszukiwania pokoi - zapytanie z udogodnieniami pokoju
    def test_query_with_room_facilities(self):
        response = self.client.post(
            "/search_free_rooms",
            json={
                "start_date": "2100-01-01",
                "end_date": "2100-01-10",
                "guests": 2,
                "room_facilities": ["wifi"],
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("available_rooms", data)
        for room in data["available_rooms"]:
            self.assertIn(
                "wifi",
                room.get("room_facilities", ["wifi"]),
                msg=f"Room has no wifi: {room}",
            )

    # Test wyszukiwania pokoi - zapytanie z udogodnieniami hotelu
    def test_query_with_hotel_facilities(self):
        response = self.client.post(
            "/search_free_rooms",
            json={
                "start_date": "2100-01-01",
                "end_date": "2100-01-10",
                "guests": 2,
                "hotel_facilities": ["basen"],
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("available_rooms", data)
        for room in data["available_rooms"]:
            self.assertIn(
                "basen",
                room.get("hotel_facilities", ["basen"]),
                msg=f"Room has no hotel pool: {room}",
            )

    # Test wyszukiwania pokoi - zapytanie z zakresem cen
    def test_query_with_price_range(self):
        response = self.client.post(
            "/search_free_rooms",
            json={
                "start_date": "2100-01-01",
                "end_date": "2100-01-10",
                "guests": 2,
                "lowest_price": 200,
                "highest_price": 400,
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("available_rooms", data)
        for room in data["available_rooms"]:
            self.assertGreaterEqual(
                room["total_price"] * 9,
                10000,
                msg=f"Price for stay too low: {room}",
            )
            self.assertLessEqual(
                room["total_price"] * 9,
                20000,
                msg=f"Price for stay too high: {room}",
            )

    # Test wyszukiwania pokoi - zapytanie z zakresem gwiazdek hotelu
    def test_query_with_stars_range(self):
        response = self.client.post(
            "/search_free_rooms",
            json={
                "start_date": "2100-01-01",
                "end_date": "2100-01-10",
                "guests": 2,
                "min_hotel_stars": 4,
                "max_hotel_stars": 5,
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("available_rooms", data)
        for room in data["available_rooms"]:
            self.assertGreaterEqual(
                room["hotel_stars"],
                4,
                msg=f"Not enough stars: {room}",
            )
            self.assertLessEqual(
                room["hotel_stars"],
                5,
                msg=f"Too many stars: {room}",
            )

    # Test wyszukiwania pokoi - zapytanie o pokój już zarezerwowany w danym terminie
    def test_query_for_reserved_room(self):
        today = date.today()
        response = self.client.post(
            "/search_free_rooms",
            json={
                "start_date": (today + timedelta(days=3)).isoformat(),
                "end_date": (today + timedelta(days=4)).isoformat(),
                "guests": 2,
            },
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("Brak dostępnych pokoi", response.get_json().get("message", ""))

    # Test wyszukiwania pokoi - sortowanie po cenie rosnąco
    def test_query_sort_by_price_asc(self):
        response = self.client.post(
            "/search_free_rooms",
            json={
                "start_date": "2100-01-01",
                "end_date": "2100-01-10",
                "guests": 2,
                "sort_by": "price",
                "sort_order": "asc",
            },
        )
        self.assertEqual(response.status_code, 200)
        rooms = response.get_json()["available_rooms"]
        prices = [room["price_per_night"] for room in rooms]
        self.assertEqual(prices, sorted(prices))

    # Test wyszukiwania pokoi - sortowanie po cenie malejąco
    def test_query_sort_by_price_desc(self):
        response = self.client.post(
            "/search_free_rooms",
            json={
                "start_date": "2100-01-01",
                "end_date": "2100-01-10",
                "guests": 2,
                "sort_by": "price",
                "sort_order": "desc",
            },
        )
        self.assertEqual(response.status_code, 200)
        rooms = response.get_json()["available_rooms"]
        prices = [room["price_per_night"] for room in rooms]
        self.assertEqual(prices, sorted(prices, reverse=True))

    # Test wyszukiwania pokoi - sortowanie po gwiazdkach rosnąco
    def test_query_sort_by_stars_asc(self):
        response = self.client.post(
            "/search_free_rooms",
            json={
                "start_date": "2100-01-01",
                "end_date": "2100-01-10",
                "guests": 2,
                "sort_by": "stars",
                "sort_order": "asc",
            },
        )
        self.assertEqual(response.status_code, 200)
        rooms = response.get_json()["available_rooms"]
        stars = [room["hotel_stars"] for room in rooms]
        self.assertEqual(stars, sorted(stars))

    # Test wyszukiwania pokoi - sortowanie po gwiazdkach malejąco
    def test_query_sort_by_stars_desc(self):
        response = self.client.post(
            "/search_free_rooms",
            json={
                "start_date": "2100-01-01",
                "end_date": "2100-01-10",
                "guests": 2,
                "sort_by": "stars",
                "sort_order": "desc",
            },
        )
        self.assertEqual(response.status_code, 200)
        rooms = response.get_json()["available_rooms"]
        stars = [room["hotel_stars"] for room in rooms]
        self.assertEqual(stars, sorted(stars, reverse=True))

    # Test wyszukiwania pokoi - zapytanie z wszystkimi parametrami
    def test_query_with_all_parameters(self):
        response = self.client.post(
            "/search_free_rooms",
            json={
                "start_date": "2100-01-01",
                "end_date": "2100-01-10",
                "guests": 2,
                "countries": ["Polska"],
                "city": ["Warszawa"],
                "room_facilities": ["wifi"],
                "hotel_facilities": ["basen"],
                "lowest_price": 100,
                "highest_price": 3000,
                "min_hotel_stars": 4,
                "max_hotel_stars": 4,
                "sort_by": "price",
                "sort_order": "asc",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("available_rooms", response.get_json())


class PostReservationTestCase(unittest.TestCase):
    def setUp(self):
        # Konfiguracja aplikacji Flask, bazy danych i JWT do testów rezerwacji.
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["SECRET_KEY"] = "test_secret"
        db.init_app(self.app)
        self.app.register_blueprint(endp_bp, url_prefix="")
        with self.app.app_context():
            db.create_all()
            # Dodanie przykładowego adresu, hotelu, pokoju i użytkownika do bazy.
            address = Address(
                country="Polska",
                city="Warszawa",
                street="Testowa",
                building="1",
                zip_code="00-001",
            )
            db.session.add(address)
            db.session.commit()
            hotel = Hotel(
                name="Hotel Test",
                stars=4,
                geo_length=0,
                geo_latitude=0,
                id_address=address.id_address,
            )
            db.session.add(hotel)
            db.session.commit()
            room = Room(id_hotel=hotel.id_hotel, capacity=2, price_per_night=100)
            db.session.add(room)
            db.session.commit()
            self.room_id = room.id_room
            user = User(
                email="test@example.com",
                password_hash="hash",
                birth_date=date(2000, 1, 1),
                first_name="Jan",
                last_name="Kowalski",
                phone_number="123456789",
                role="user",
            )
            db.session.add(user)
            db.session.commit()
            self.user_id = user.id_user
            JWTManager(self.app)
            self.token = create_access_token(identity=str(self.user_id))
        self.client = self.app.test_client()

    def tearDown(self):
        # Czyszczenie bazy po każdym teście
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def get_headers(self, token=None):
        # Pomocnicza metoda do generowania nagłówków z JWT
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def get_valid_payload(self, **overrides):
        # Pomocnicza metoda do generowania poprawnego payloadu rezerwacji
        today = date.today()
        payload = {
            "id_room": self.room_id,
            "id_user": self.user_id,
            "first_night": (today + timedelta(days=1)).isoformat(),
            "last_night": (today + timedelta(days=2)).isoformat(),
            "full_name": "Jan Kowalski",
            "bill_type": "I",
        }
        payload.update(overrides)
        return payload

    # Test rezerwacji - brak tokena JWT
    def test_no_token(self):
        response = self.client.post("/post_reservation", json=self.get_valid_payload())
        self.assertEqual(response.status_code, 401)

    # Test rezerwacji - brak wymaganych pól w żądaniu
    def test_missing_fields(self):
        payload = self.get_valid_payload()
        del payload["id_room"]
        response = self.client.post(
            "/post_reservation", json=payload, headers=self.get_headers(self.token)
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("missing_fields", response.get_json())

    # Test rezerwacji - niepoprawny format id_room i id_user
    def test_invalid_id_room_and_id_user(self):
        payload = self.get_valid_payload(id_room="abc", id_user="xyz")
        response = self.client.post(
            "/post_reservation", json=payload, headers=self.get_headers(self.token)
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Nieprawidłowy format identyfikatora użytkownika lub pokoju.",
            response.get_json().get("error", ""),
        )

    # Test rezerwacji - niepoprawny typ full_name
    def test_invalid_full_name_type(self):
        payload = self.get_valid_payload(full_name=12345)
        response = self.client.post(
            "/post_reservation", json=payload, headers=self.get_headers(self.token)
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Imię i nazwisko musi być niepustym stringiem",
            response.get_json().get("error", ""),
        )

    # Test rezerwacji - puste pole full_name
    def test_empty_full_name(self):
        payload = self.get_valid_payload(full_name="")
        response = self.client.post(
            "/post_reservation", json=payload, headers=self.get_headers(self.token)
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Imię i nazwisko musi być niepustym stringiem",
            response.get_json().get("error", ""),
        )

    # Test rezerwacji - niepoprawny format bill_type
    def test_invalid_bill_type_format(self):
        payload = self.get_valid_payload(bill_type=123)
        response = self.client.post(
            "/post_reservation", json=payload, headers=self.get_headers(self.token)
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Typ rachunku", response.get_json().get("error", ""))

    # Test rezerwacji - niepoprawna wartość bill_type
    def test_invalid_bill_type_value(self):
        payload = self.get_valid_payload(bill_type="X")
        response = self.client.post(
            "/post_reservation", json=payload, headers=self.get_headers(self.token)
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Typ rachunku", response.get_json().get("error", ""))

    # Test rezerwacji - token JWT niezgodny z użytkownikiem
    def test_wrong_token(self):
        payload = self.get_valid_payload(id_user=999)
        with self.app.app_context():
            wrong_token = create_access_token(identity="777")
        response = self.client.post(
            "/post_reservation", json=payload, headers=self.get_headers(wrong_token)
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("Brak uprawnień", response.get_json().get("error", ""))

    # Test rezerwacji - niepoprawny format daty
    def test_invalid_date_format(self):
        payload = self.get_valid_payload(first_night="2024/01/01")
        response = self.client.post(
            "/post_reservation", json=payload, headers=self.get_headers(self.token)
        )
        print("RESPONSE:", response.get_json())
        self.assertEqual(response.status_code, 400)
        self.assertIn("format daty", response.get_json().get("error", ""))

    # Test rezerwacji - data początkowa po dacie końcowej
    def test_start_date_after_end_date(self):
        today = date.today()
        payload = self.get_valid_payload(
            first_night=(today + timedelta(days=5)).isoformat(),
            last_night=(today + timedelta(days=2)).isoformat(),
        )
        response = self.client.post(
            "/post_reservation", json=payload, headers=self.get_headers(self.token)
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Data początkowa", response.get_json().get("error", ""))

    # Test rezerwacji - nieistniejący pokój
    def test_nonexistent_room(self):
        payload = self.get_valid_payload(id_room=99999)
        response = self.client.post(
            "/post_reservation", json=payload, headers=self.get_headers(self.token)
        )
        print("RESPONSE:", response.get_json())
        self.assertEqual(response.status_code, 404)
        self.assertIn("Pokój nie istnieje", response.get_json().get("error", ""))

    # Test rezerwacji - próba rezerwacji już zarezerwowanego pokoju
    def test_reservation_of_reserved_room(self):
        payload = self.get_valid_payload()
        response1 = self.client.post(
            "/post_reservation", json=payload, headers=self.get_headers(self.token)
        )
        self.assertEqual(response1.status_code, 201)

        response2 = self.client.post(
            "/post_reservation", json=payload, headers=self.get_headers(self.token)
        )
        self.assertEqual(response2.status_code, 400)
        self.assertIn("zarezerwowany", response2.get_json().get("error", ""))

    # Test rezerwacji - poprawna rezerwacja pokoju
    def test_successful_reservation(self):
        today = date.today()
        payload = self.get_valid_payload(
            first_night=(today + timedelta(days=10)).isoformat(),
            last_night=(today + timedelta(days=12)).isoformat(),
        )
        response = self.client.post(
            "/post_reservation", json=payload, headers=self.get_headers(self.token)
        )
        print("RESPONSE:", response.get_json())
        self.assertEqual(response.status_code, 201)
        self.assertIn("pomyślnie utworzona", response.get_json().get("message", ""))


class PostCancellationTestCase(unittest.TestCase):
    def setUp(self):
        # Konfiguracja aplikacji Flask, bazy danych i JWT do testów anulowania rezerwacji.
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["SECRET_KEY"] = "test_secret"
        db.init_app(self.app)
        self.app.register_blueprint(endp_bp, url_prefix="")
        with self.app.app_context():
            db.create_all()
            # Dodanie przykładowego adresu, hotelu, pokoju, użytkownika i rezerwacji do bazy.
            address = Address(
                country="Polska",
                city="Warszawa",
                street="Testowa",
                building="1",
                zip_code="00-001",
            )
            db.session.add(address)
            db.session.commit()
            hotel = Hotel(
                name="Hotel Test",
                stars=4,
                geo_length=0,
                geo_latitude=0,
                id_address=address.id_address,
            )
            db.session.add(hotel)
            db.session.commit()
            room = Room(id_hotel=hotel.id_hotel, capacity=2, price_per_night=100)
            db.session.add(room)
            db.session.commit()
            user = User(
                email="test@example.com",
                password_hash="hash",
                birth_date=date(2000, 1, 1),
                first_name="Jan",
                last_name="Kowalski",
                phone_number="123456789",
                role="user",
            )
            db.session.add(user)
            db.session.commit()
            self.user_id = str(user.id_user)
            reservation = Reservation(
                id_room=room.id_room,
                id_user=user.id_user,
                first_night=date.today(),
                last_night=date.today() + timedelta(days=2),
                full_name="Jan Kowalski",
                price=200,
                bill_type="I",
                nip=None,
                reservation_status="A",
            )
            db.session.add(reservation)
            db.session.commit()
            self.reservation_id = reservation.id_reservation
            JWTManager(self.app)
            self.token = create_access_token(identity=self.user_id)
        self.client = self.app.test_client()

    def tearDown(self):
        # Czyszczenie bazy po każdym teście
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def get_headers(self, token=None):
        # Pomocnicza metoda do generowania nagłówków z JWT
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    # Test anulowania rezerwacji - brak tokena JWT
    def test_no_token(self):
        response = self.client.post(
            "/post_cancellation",
            json={"id_reservation": self.reservation_id, "id_user": self.user_id},
        )
        self.assertEqual(response.status_code, 401)

    # Test anulowania rezerwacji - brak wymaganych pól w żądaniu
    def test_missing_fields(self):
        response = self.client.post(
            "/post_cancellation", json={}, headers=self.get_headers(self.token)
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("missing_fields", response.get_json())

    # Test anulowania rezerwacji - token JWT niezgodny z użytkownikiem
    def test_wrong_token(self):
        with self.app.app_context():
            wrong_token = create_access_token(identity="999")
        response = self.client.post(
            "/post_cancellation",
            json={"id_reservation": self.reservation_id, "id_user": self.user_id},
            headers=self.get_headers(wrong_token),
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("Brak uprawnień", response.get_json().get("error", ""))

    # Test anulowania rezerwacji - nieistniejąca rezerwacja
    def test_invalid_reservation(self):
        response = self.client.post(
            "/post_cancellation",
            json={"id_reservation": 99999, "id_user": self.user_id},
            headers=self.get_headers(self.token),
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("nie istnieje", response.get_json().get("error", ""))

    # Test anulowania rezerwacji - poprawne anulowanie rezerwacji
    def test_successful_cancellation(self):
        response = self.client.post(
            "/post_cancellation",
            json={"id_reservation": self.reservation_id, "id_user": self.user_id},
            headers=self.get_headers(self.token),
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("pomyślnie anulowana", response.get_json().get("message", ""))


class GetUserTestCase(unittest.TestCase):
    def setUp(self):
        # Konfiguracja aplikacji Flask, bazy danych i JWT do testów pobierania użytkownika.
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["SECRET_KEY"] = "test_secret"
        db.init_app(self.app)
        self.app.register_blueprint(endp_bp, url_prefix="")
        with self.app.app_context():
            db.create_all()
            user = User(
                email="test@example.com",
                password_hash="hash",
                birth_date=date(2000, 1, 1),
                first_name="Jan",
                last_name="Kowalski",
                phone_number="123456789",
                role="user",
            )
            db.session.add(user)
            db.session.commit()
            self.user_id = str(user.id_user)
            JWTManager(self.app)
            self.token = create_access_token(identity=self.user_id)
        self.client = self.app.test_client()

    def tearDown(self):
        # Czyszczenie bazy po każdym teście
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def get_headers(self, token=None):
        # Pomocnicza metoda do generowania nagłówków z JWT
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    # Test pobierania użytkownika - brak tokena JWT
    def test_no_token(self):
        response = self.client.get(f"/user/{self.user_id}")
        self.assertEqual(response.status_code, 401)

    # Test pobierania użytkownika - nieistniejący użytkownik
    def test_invalid_id_value(self):
        response = self.client.get("/user/99999", headers=self.get_headers(self.token))
        self.assertEqual(response.status_code, 404)
        self.assertIn("nie istnieje", response.get_json().get("error", ""))

    # Test pobierania użytkownika - token JWT niezgodny z użytkownikiem
    def test_wrong_token(self):
        with self.app.app_context():
            wrong_token = create_access_token(identity="999")
        response = self.client.get(
            f"/user/{self.user_id}", headers=self.get_headers(wrong_token)
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("Brak uprawnień", response.get_json().get("error", ""))

    # Test pobierania użytkownika - poprawne pobranie danych
    def test_successful_get_user(self):
        response = self.client.get(
            f"/user/{self.user_id}", headers=self.get_headers(self.token)
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("id_user", response.get_json())


class ChangePasswordTestCase(unittest.TestCase):
    def setUp(self):
        # Konfiguracja aplikacji Flask, bazy danych i JWT do testów zmiany hasła.
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["SECRET_KEY"] = "test_secret"
        db.init_app(self.app)
        self.app.register_blueprint(endp_bp, url_prefix="")
        with self.app.app_context():
            db.create_all()
            user = User(
                email="test@example.com",
                password_hash=generate_password_hash("oldpass"),
                birth_date=date(2000, 1, 1),
                first_name="Jan",
                last_name="Kowalski",
                phone_number="123456789",
                role="user",
            )
            db.session.add(user)
            db.session.commit()
            self.user_id = str(user.id_user)
            JWTManager(self.app)
            self.token = create_access_token(identity=self.user_id)
        self.client = self.app.test_client()

    def tearDown(self):
        # Czyszczenie bazy po każdym teście
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def get_headers(self, token=None):
        # Pomocnicza metoda do generowania nagłówków z JWT
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    # Test zmiany hasła - brak tokena JWT
    def test_no_token(self):
        response = self.client.put(
            f"/user/{self.user_id}/password",
            json={
                "id_user": self.user_id,
                "current_password": "oldpass",
                "new_password": "newpass123",
            },
        )
        self.assertEqual(response.status_code, 401)

    # Test zmiany hasła - token JWT niezgodny z użytkownikiem
    def test_wrong_token(self):
        with self.app.app_context():
            wrong_token = create_access_token(identity="999")
        response = self.client.put(
            f"/user/{self.user_id}/password",
            json={
                "id_user": self.user_id,
                "current_password": "oldpass",
                "new_password": "newpass123",
            },
            headers=self.get_headers(wrong_token),
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("Brak uprawnień", response.get_json().get("error", ""))

    # Test zmiany hasła - brak wymaganych pól
    def test_missing_fields(self):
        response = self.client.put(
            f"/user/{self.user_id}/password",
            json={"id_user": self.user_id},
            headers=self.get_headers(self.token),
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("missing_fields", response.get_json())

    # Test zmiany hasła - niepoprawny format id_user
    def test_invalid_id_user_format(self):
        response = self.client.put(
            "/user/abc/password",
            json={
                "id_user": "abc",
                "current_password": "oldpass",
                "new_password": "newpass123",
            },
            headers=self.get_headers(self.token),
        )
        self.assertEqual(response.status_code, 404)  # Flask nie wywoła endpointu

    # Test zmiany hasła - puste hasła
    def test_empty_passwords(self):
        response = self.client.put(
            f"/user/{self.user_id}/password",
            json={
                "id_user": self.user_id,
                "current_password": "",
                "new_password": "",
            },
            headers=self.get_headers(self.token),
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("niepustymi stringami", response.get_json().get("error", ""))

    # Test zmiany hasła - nieprawidłowe aktualne hasło
    def test_wrong_current_password(self):
        response = self.client.put(
            f"/user/{self.user_id}/password",
            json={
                "id_user": self.user_id,
                "current_password": "wrongpass",
                "new_password": "newpass123",
            },
            headers=self.get_headers(self.token),
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Nieprawidłowe aktualne hasło", response.get_json().get("error", "")
        )

    # Test zmiany hasła - poprawna zmiana hasła
    def test_successful_change(self):
        response = self.client.put(
            f"/user/{self.user_id}/password",
            json={
                "id_user": self.user_id,
                "current_password": "oldpass",
                "new_password": "newpass123",
            },
            headers=self.get_headers(self.token),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Hasło zostało zmienione", response.get_json().get("message", ""))


class DeleteUserTestCase(unittest.TestCase):
    def setUp(self):
        # Konfiguracja aplikacji Flask, bazy danych i JWT do testów usuwania użytkownika.
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["SECRET_KEY"] = "test_secret"
        db.init_app(self.app)
        self.app.register_blueprint(endp_bp, url_prefix="")
        with self.app.app_context():
            db.create_all()
            user = User(
                email="test@example.com",
                password_hash="hash",
                birth_date=date(2000, 1, 1),
                first_name="Jan",
                last_name="Kowalski",
                phone_number="123456789",
                role="user",
            )
            db.session.add(user)
            db.session.commit()
            self.user_id = str(user.id_user)
            JWTManager(self.app)
            self.token = create_access_token(identity=self.user_id)
        self.client = self.app.test_client()

    def tearDown(self):
        # Czyszczenie bazy po każdym teście
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def get_headers(self, token=None):
        # Pomocnicza metoda do generowania nagłówków z JWT
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    # Test usuwania użytkownika - brak tokena JWT
    def test_no_token(self):
        response = self.client.delete(f"/user/{self.user_id}")
        self.assertEqual(response.status_code, 401)

    # Test usuwania użytkownika - token JWT niezgodny z użytkownikiem
    def test_wrong_token(self):
        with self.app.app_context():
            wrong_token = create_access_token(identity="999")
        response = self.client.delete(
            f"/user/{self.user_id}", headers=self.get_headers(wrong_token)
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("Brak uprawnień", response.get_json().get("error", ""))

    # Test usuwania użytkownika - nieistniejący użytkownik
    def test_wrong_user(self):
        with self.app.app_context():
            wrong_token = create_access_token(identity="999")
        response = self.client.delete(
            f"/user/999", headers=self.get_headers(wrong_token)
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("Użytkownik nie istnieje", response.get_json().get("error", ""))

    # Test usuwania użytkownika - poprawne usunięcie konta
    def test_successful_delete(self):
        response = self.client.delete(
            f"/user/{self.user_id}", headers=self.get_headers(self.token)
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Konto zostało usunięte", response.get_json().get("message", ""))


class GetUserReservationsTestCase(unittest.TestCase):
    def setUp(self):
        # Konfiguracja aplikacji Flask, bazy danych i JWT do testów pobierania rezerwacji użytkownika.
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["SECRET_KEY"] = "test_secret"
        db.init_app(self.app)
        self.app.register_blueprint(endp_bp, url_prefix="")
        with self.app.app_context():
            db.create_all()
            user = User(
                email="test@example.com",
                password_hash="hash",
                birth_date=date(2000, 1, 1),
                first_name="Jan",
                last_name="Kowalski",
                phone_number="123456789",
                role="user",
            )
            db.session.add(user)
            db.session.commit()
            self.user_id = str(user.id_user)
            JWTManager(self.app)
            self.token = create_access_token(identity=self.user_id)
            # Dodanie przykładowej rezerwacji do bazy
            hotel = Hotel(
                name="Hotel Test", stars=4, geo_length=0, geo_latitude=0, id_address=1
            )
            db.session.add(hotel)
            db.session.commit()
            room = Room(id_hotel=hotel.id_hotel, capacity=2, price_per_night=100)
            db.session.add(room)
            db.session.commit()
            reservation = Reservation(
                id_room=room.id_room,
                id_user=user.id_user,
                first_night=date.today(),
                last_night=date.today() + timedelta(days=2),
                full_name="Jan Kowalski",
                price=200,
                bill_type="I",
                nip=None,
                reservation_status="A",
            )
            db.session.add(reservation)
            db.session.commit()
            self.room_id = room.id_room
            self.reservation_id = reservation.id_reservation
        self.client = self.app.test_client()

    def tearDown(self):
        # Czyszczenie bazy po każdym teście
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def get_headers(self, token=None):
        # Pomocnicza metoda do generowania nagłówków z JWT
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    # Test pobierania rezerwacji - brak tokena JWT
    def test_no_token(self):
        response = self.client.get(f"/user/{self.user_id}/reservations?status=active")
        self.assertEqual(response.status_code, 401)

    # Test pobierania rezerwacji - token JWT niezgodny z użytkownikiem
    def test_wrong_token(self):
        with self.app.app_context():
            wrong_token = create_access_token(identity="999")
        response = self.client.get(
            f"/user/{self.user_id}/reservations?status=active",
            headers=self.get_headers(wrong_token),
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("Brak uprawnień", response.get_json().get("error", ""))

    # Test pobierania rezerwacji - niepoprawny format statusu rezerwacji
    def test_invalid_status_format(self):
        response = self.client.get(
            f"/user/{self.user_id}/reservations?status=wrong",
            headers=self.get_headers(self.token),
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Nieprawidłowy format statusu rezerwacji",
            response.get_json().get("error", ""),
        )

    # Test pobierania rezerwacji - brak rezerwacji o danym statusie
    def test_no_reservations(self):
        with self.app.app_context():
            Reservation.query.delete()
            db.session.commit()
        response = self.client.get(
            f"/user/{self.user_id}/reservations?status=active",
            headers=self.get_headers(self.token),
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn(
            "Brak aktywnych rezerwacji", response.get_json().get("message", "")
        )

    # Test pobierania rezerwacji - poprawne pobranie rezerwacji
    def test_successful_get_reservations(self):
        response = self.client.get(
            f"/user/{self.user_id}/reservations?status=active",
            headers=self.get_headers(self.token),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("reservations", response.get_json())

    # Test pobierania rezerwacji - tylko poprawny status w odpowiedzi
    def test_only_correct_status_in_response(self):
        with self.app.app_context():
            reservation = Reservation(
                id_room=self.room_id,
                id_user=int(self.user_id),
                first_night=date.today(),
                last_night=date.today() + timedelta(days=2),
                full_name="Jan Kowalski",
                price=200,
                bill_type="I",
                nip=None,
                reservation_status="C",
            )
            db.session.add(reservation)
            db.session.commit()
        response = self.client.get(
            f"/user/{self.user_id}/reservations?status=active",
            headers=self.get_headers(self.token),
        )
        self.assertEqual(response.status_code, 200)
        for res in response.get_json()["reservations"]:
            self.assertEqual(res["status"], "A")
        response = self.client.get(
            f"/user/{self.user_id}/reservations?status=cancelled",
            headers=self.get_headers(self.token),
        )
        self.assertEqual(response.status_code, 200)
        for res in response.get_json()["reservations"]:
            self.assertEqual(res["status"], "C")


class GetHotelAndRoomTestCase(unittest.TestCase):
    def setUp(self):
        # Konfiguracja aplikacji Flask i bazy danych do testów pobierania hotelu i pokoju.
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["SECRET_KEY"] = "test_secret"
        db.init_app(self.app)
        self.app.register_blueprint(endp_bp, url_prefix="")
        with self.app.app_context():
            db.create_all()
            address = Address(
                country="Polska",
                city="Warszawa",
                street="Testowa",
                building="1",
                zip_code="00-001",
            )
            db.session.add(address)
            db.session.commit()
            hotel = Hotel(
                name="Hotel Test",
                stars=4,
                geo_length=0,
                geo_latitude=0,
                id_address=address.id_address,
            )
            db.session.add(hotel)
            db.session.commit()
            room = Room(id_hotel=hotel.id_hotel, capacity=2, price_per_night=100)
            db.session.add(room)
            db.session.commit()
            self.id_hotel = hotel.id_hotel
            self.room_id = room.id_room
        self.client = self.app.test_client()

    def tearDown(self):
        # Czyszczenie bazy po każdym teście
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # Test pobierania hotelu - nieistniejący hotel
    def test_nonexistent_hotel(self):
        response = self.client.get("/hotel/99999")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Hotel nie istnieje", response.get_json().get("error", ""))

    # Test pobierania hotelu - poprawne pobranie hotelu
    def test_successful_get_hotel(self):
        response = self.client.get(f"/hotel/{self.id_hotel}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("id_hotel", response.get_json())

    # Test pobierania pokoju - nieistniejący pokój
    def test_nonexistent_room(self):
        response = self.client.get("/room/99999")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Pokój nie istnieje", response.get_json().get("error", ""))

    # Test pobierania pokoju - poprawne pobranie pokoju
    def test_successful_get_room(self):
        response = self.client.get(f"/room/{self.room_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("id_room", response.get_json())


class GetAllListsTestCase(unittest.TestCase):
    def setUp(self):
        # Konfiguracja aplikacji Flask i bazy danych do testów pobierania list słownikowych.
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["SECRET_KEY"] = "test_secret"
        db.init_app(self.app)
        self.app.register_blueprint(endp_bp, url_prefix="")
        with self.app.app_context():
            db.create_all()
            address = Address(
                country="Polska",
                city="Warszawa",
                street="Testowa",
                building="1",
                zip_code="00-001",
            )
            db.session.add(address)
            db.session.commit()
            hotel = Hotel(
                name="Hotel Test",
                stars=4,
                geo_length=0,
                geo_latitude=0,
                id_address=address.id_address,
            )
            db.session.add(hotel)
            db.session.commit()
            room = Room(id_hotel=hotel.id_hotel, capacity=2, price_per_night=100)
            db.session.add(room)
            db.session.commit()
            rf_wifi = RoomFacility(facility_name="wifi")
            db.session.add(rf_wifi)
            db.session.commit()
            hf_pool = HotelFacility(facility_name="basen")
            db.session.add(hf_pool)
            db.session.commit()
            hotel_image = HotelImage(
                id_hotel=hotel.id_hotel,
                image_url="https://example.com/hotel.jpg",
                description="Testowy obraz hotelu",
                is_main=True,
            )
            db.session.add(hotel_image)
            db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self):
        # Czyszczenie bazy po każdym teście
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # Test pobierania wszystkich list słownikowych (kraje, miasta, udogodnienia pokoi, udogodnienia hoteli)
    def test_get_all_lists(self):
        response = self.client.get("/countries")
        self.assertEqual(response.status_code, 200)
        self.assertIn("countries", response.get_json())

        response = self.client.get("/cities")
        self.assertEqual(response.status_code, 200)
        self.assertIn("cities", response.get_json())

        response = self.client.get("/room_facilities")
        self.assertEqual(response.status_code, 200)
        self.assertIn("room_facilities", response.get_json())

        response = self.client.get("/hotel_facilities")
        self.assertEqual(response.status_code, 200)
        self.assertIn("hotel_facilities", response.get_json())


class GetHotelImagesTestCase(unittest.TestCase):
    def setUp(self):
        # Konfiguracja aplikacji Flask i bazy danych do testów pobierania zdjęć hotelu.
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        db.init_app(self.app)
        self.app.register_blueprint(endp_bp, url_prefix="")
        with self.app.app_context():
            db.create_all()

            address = Address(
                country="Polska",
                city="Warszawa",
                street="Testowa",
                building="1",
                zip_code="00-001",
            )
            db.session.add(address)
            db.session.commit()

            hotel = Hotel(
                name="Hotel Testowy",
                stars=4,
                geo_length=21.0122,
                geo_latitude=52.2297,
                id_address=address.id_address,
            )
            db.session.add(hotel)
            db.session.commit()
            self.id_hotel = hotel.id_hotel

            image1 = HotelImage(
                id_hotel=hotel.id_hotel,
                image_url="https://example.com/hotel1.jpg",
                description="Główny widok hotelu",
                is_main=True,
            )
            image2 = HotelImage(
                id_hotel=hotel.id_hotel,
                image_url="https://example.com/hotel2.jpg",
                description="Basen",
                is_main=False,
            )
            db.session.add_all([image1, image2])
            db.session.commit()

        self.client = self.app.test_client()

    def tearDown(self):
        # Czyszczenie bazy po każdym teście
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # Test pobierania zdjęć hotelu - poprawne pobranie zdjęć
    def test_get_hotel_images_success(self):
        response = self.client.get(f"/hotel_images/{self.id_hotel}")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)

        self.assertEqual(data[0]["url"], "https://example.com/hotel1.jpg")
        self.assertEqual(data[0]["description"], "Główny widok hotelu")
        self.assertTrue(data[0]["is_main"])

        self.assertEqual(data[1]["url"], "https://example.com/hotel2.jpg")
        self.assertEqual(data[1]["description"], "Basen")
        self.assertFalse(data[1]["is_main"])

    # Test pobierania zdjęć hotelu - hotel bez zdjęć
    def test_get_hotel_images_empty(self):
        new_hotel = Hotel(
            name="Nowy Hotel", stars=3, geo_length=0, geo_latitude=0, id_address=1
        )
        with self.app.app_context():
            db.session.add(new_hotel)
            db.session.commit()
            new_id_hotel = new_hotel.id_hotel

        response = self.client.get(f"/hotel_images/{new_id_hotel}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    # Test pobierania zdjęć hotelu - nieistniejący hotel
    def test_get_hotel_images_invalid_id(self):
        response = self.client.get("/hotel_images/99999")
        self.assertEqual(response.status_code, 404)
        self.assertIn(
            "Hotel nie istnieje",
            response.get_json().get("error", ""),
        )


if __name__ == "__main__":
    unittest.main()
