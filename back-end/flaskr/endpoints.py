from flask import Blueprint, request, jsonify
from models import User, Hotel, Reservation
from datetime import timedelta, datetime
from extensions import db
from sqlalchemy.sql import text

endp_bp = Blueprint("endp", __name__)


@endp_bp.route("/get_free_rooms", methods=["GET"])
def get_free_rooms():
    try:
        # Pobranie parametrów z zapytania
        city = request.args.get("city")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        guests = request.args.get("guests")

        # Walidacja parametrów
        if not city or not start_date or not end_date or not guests:
            return (
                jsonify(
                    {
                        "error": "Brak wymaganych parametrów: city, start_date, end_date, guests"
                    }
                ),
                400,
            )

        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            guests = int(guests)
        except ValueError:
            return (
                jsonify(
                    {
                        "error": "Nieprawidłowy format daty lub liczby gości. Użyj formatu YYYY-MM-DD dla dat i liczby całkowitej dla liczby gości"
                    }
                ),
                400,
            )

        if start_date >= end_date:
            return (
                jsonify(
                    {"error": "Data początkowa musi być wcześniejsza niż data końcowa"}
                ),
                400,
            )

        if guests <= 0:
            return jsonify({"error": "Liczba gości musi być większa od zera"}), 400

        # Zapytanie do bazy danych
        query = db.session.execute(
            text(
                """
            SELECT r.id_room, r.capacity, r.price_per_night, h.name AS hotel_name, a.city
            FROM rooms r
            JOIN hotels h ON r.id_hotel = h.id_hotel
            JOIN addresses a ON h.id_address = a.id_address
            WHERE a.city = :city
              AND r.capacity >= :guests
              AND r.id_room NOT IN (
                  SELECT id_room
                  FROM reservations
                  WHERE (first_night, last_night) OVERLAPS (:start_date, :end_date)
              )
            """
            ),
            {
                "city": city,
                "start_date": start_date,
                "end_date": end_date,
                "guests": guests,
            },
        )

        # Przetworzenie wyników
        rooms = [
            {
                "id_room": row.id_room,
                "capacity": row.capacity,
                "price_per_night": float(row.price_per_night),
                "hotel_name": row.hotel_name,
                "city": row.city,
            }
            for row in query
        ]

        if not rooms:
            return (
                jsonify(
                    {
                        "message": "Brak dostępnych pokoi w podanym mieście, terminie i dla podanej liczby gości"
                    }
                ),
                404,
            )

        return jsonify({"available_rooms": rooms}), 200

    except Exception as e:
        return (
            jsonify(
                {
                    "error": "Wystąpił błąd podczas przetwarzania zapytania",
                    "details": str(e),
                }
            ),
            500,
        )


@endp_bp.route("/post_reservation", methods=["POST"])
def post_reservation():
    try:
        # Pobranie danych z żądania
        data = request.get_json()

        # Walidacja danych wejściowych
        required_fields = [
            "id_room",
            "id_user",
            "first_night",
            "last_night",
            "full_name",
            "price",
            "bill_type",
        ]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return (
                jsonify(
                    {"error": "Brak wymaganych pól", "missing_fields": missing_fields}
                ),
                400,
            )

        try:
            first_night = datetime.strptime(data["first_night"], "%Y-%m-%d").date()
            last_night = datetime.strptime(data["last_night"], "%Y-%m-%d").date()
        except ValueError:
            return (
                jsonify(
                    {"error": "Nieprawidłowy format daty. Użyj formatu YYYY-MM-DD"}
                ),
                400,
            )

        if first_night >= last_night:
            return (
                jsonify(
                    {"error": "Data początkowa musi być wcześniejsza niż data końcowa"}
                ),
                400,
            )

        # Sprawdzenie, czy pokój jest dostępny w podanym terminie
        query = db.session.execute(
            text(
                """
                SELECT 1
                FROM reservations
                WHERE id_room = :id_room
                  AND (first_night, last_night) OVERLAPS (:first_night, :last_night)
                """
            ),
            {
                "id_room": data["id_room"],
                "first_night": first_night,
                "last_night": last_night,
            },
        ).fetchone()

        if query:
            return (
                jsonify({"error": "Pokój jest już zarezerwowany w podanym terminie"}),
                400,
            )

        # Utworzenie nowej rezerwacji
        new_reservation = Reservation(
            id_room=data["id_room"],
            id_user=data["id_user"],
            first_night=first_night,
            last_night=last_night,
            full_name=data["full_name"],
            price=data["price"],
            bill_type=data["bill_type"],
            nip=data.get("nip"),  # Pole opcjonalne
        )

        db.session.add(new_reservation)
        db.session.commit()

        return jsonify({"message": "Rezerwacja została pomyślnie utworzona"}), 201

    except Exception as e:
        db.session.rollback()
        return (
            jsonify(
                {
                    "error": "Wystąpił błąd podczas tworzenia rezerwacji",
                    "details": str(e),
                }
            ),
            500,
        )


@endp_bp.route("/post_cancellation", methods=["POST"])
def post_reservation():
    try:
        # Pobranie danych z żądania
        data = request.get_json()

        # Walidacja danych wejściowych
        required_fields = [
            "id_reservation",
        ]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return (
                jsonify(
                    {"error": "Brak wymaganych pól", "missing_fields": missing_fields}
                ),
                400,
            )

        query = db.session.execute(
            text(
                """
                DELETE 
                FROM reservations 
                WHERE id_reservation = :id_reservation
                """
            ),
            {"id_reservation": data["id_reservation"]},
        )

        if query.rowcount == 0:
            return (
                jsonify({"error": "Wskazana rejestracja nie istnieje"}),
                404,
            )

        db.session.commit()

        return jsonify({"message": "Rezerwacja została pomyślnie anulowana"}), 201

    except Exception as e:
        db.session.rollback()
        return (
            jsonify(
                {
                    "error": "Wystąpił błąd podczas anulowania rezerwacji",
                    "details": str(e),
                }
            ),
            500,
        )
