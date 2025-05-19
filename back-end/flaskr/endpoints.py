from flask import Blueprint, request, jsonify
from models import *
from datetime import timedelta, datetime
from extensions import db
from sqlalchemy.sql import text

endp_bp = Blueprint("endp", __name__)


@endp_bp.route("/get_free_rooms", methods=["GET"])
def get_free_rooms():
    try:
        data = request.get_json()

        required_fields = ["city", "start_date", "end_date", "guests"]

        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return (
                jsonify(
                    {"error": "Brak wymaganych pól", "missing_fields": missing_fields}
                ),
                400,
            )

        try:
            start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
            end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
            guests = int(data["guests"])
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
                "city": data["city"],
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
        data = request.get_json()

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
            reservation_status="U",
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
def post_cancellation():
    try:
        data = request.get_json()

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

        reservation = Reservation.query.filter_by(
            id_reservation=data["id_reservation"]
        ).first()
        if not reservation:
            return (
                jsonify({"error": "Wskazana rezerwacja nie istnieje"}),
                404,
            )
        reservation.reservation_status = "C"
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


@endp_bp.route("/post_payment", methods=["POST"])
def post_payment():
    try:
        data = request.get_json()

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

        reservation = Reservation.query.filter_by(
            id_reservation=data["id_reservation"]
        ).first()
        if not reservation:
            return (
                jsonify({"error": "Wskazana rezerwacja nie istnieje"}),
                404,
            )
        reservation.reservation_status = "P"
        db.session.commit()

        return jsonify({"message": "Rezerwacja została pomyślnie opłacona"}), 201

    except Exception as e:
        db.session.rollback()
        return (
            jsonify(
                {
                    "error": "Wystąpił błąd podczas opłacania rezerwacji",
                    "details": str(e),
                }
            ),
            500,
        )


@endp_bp.route("/user/<int:id_user>", methods=["GET"])
def get_user(id_user):
    if not isinstance(id_user, int):
        return (
            jsonify(
                {
                    "error": "Nieprawidłowy format identyfikatora użytkownika. Użyj liczby całkowitej"
                }
            ),
            400,
        )

    user = User.query.get(id_user)
    if not user:
        return jsonify({"error": "Użytkownik nie istnieje"}), 404

    user_data = {
        "id_user": user.id_user,
        "email": user.email,
        "birth_date": user.birth_date.isoformat(),
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone_number": user.phone_number,
    }
    return jsonify(user_data), 200


@endp_bp.route("/user/<int:id_user>/reservations", methods=["GET"])
def get_user_reservations(id_user):

    if not isinstance(id_user, int):
        return (
            jsonify(
                {
                    "error": "Nieprawidłowy format identyfikatora użytkownika. Użyj liczby całkowitej"
                }
            ),
            400,
        )

    status_arg = request.args.get("status")

    if status_arg not in {"unpaid", "paid", "cancelled"}:
        return (
            jsonify(
                {
                    "error": "Nieprawidłowy format statusu rezerwacji. Użyj 'unpaid' dla nieopłaconych, 'paid' dla opłaconych, lub 'cancelled' dla anulowanych"
                }
            ),
            400,
        )

    match status_arg:
        case "unpaid":
            status_string = "nieopłaconych"
            status = "U"
        case "paid":
            status_string = "opłaconych"
            status = "P"
        case "cancelled":
            status_string = "anulowanych"
            status = "C"

    query = Reservation.query.filter_by(id_user=id_user, status=status)
    reservations = query.all()

    if not reservations:
        return (
            jsonify(
                {"message": f"Brak {status_string} rezerwacji dla tego użytkownika"}
            ),
            404,
        )

    result = []
    for res in reservations:
        room = Room.query.get(res.id_room)
        hotel = Hotel.query.get(room.id_hotel)

        # Udogodnienia pokoju
        room_facilities = (
            db.session.query(RoomFacility.facility_name)
            .join(
                RoomRoomFacility,
                RoomRoomFacility.id_room_facility == RoomFacility.id_room_facility,
            )
            .filter(RoomRoomFacility.id_room == room.id_room)
            .all()
        )
        room_facilities = [f.facility_name for f in room_facilities]

        # Udogodnienia hotelu
        hotel_facilities = (
            db.session.query(HotelFacility.facility_name)
            .join(
                HotelHotelFacility,
                HotelHotelFacility.id_hotel_facility == HotelFacility.id_hotel_facility,
            )
            .filter(HotelHotelFacility.id_hotel == hotel.id_hotel)
            .all()
        )
        hotel_facilities = [f.facility_name for f in hotel_facilities]

        result.append(
            {
                "id_reservation": res.id_reservation,
                "first_night": res.first_night.isoformat(),
                "last_night": res.last_night.isoformat(),
                "full_name": res.full_name,
                "price": float(res.price),
                "bill_type": res.bill_type,
                "nip": res.nip,
                "status": res.status,
                "room": {
                    "id_room": room.id_room,
                    "capacity": room.capacity,
                    "price_per_night": float(room.price_per_night),
                    "facilities": room_facilities,
                },
                "hotel": (
                    {
                        "id_hotel": hotel.id_hotel,
                        "name": hotel.name,
                        "stars": hotel.stars,
                        "facilities": hotel_facilities,
                    }
                ),
            }
        )

    return jsonify({"reservations": result}), 200


@endp_bp.route("/hotel/<int:id_hotel>", methods=["GET"])
def get_hotel(id_hotel):

    if not isinstance(id_hotel, int):
        return (
            jsonify(
                {
                    "error": "Nieprawidłowy format identyfikatora hotelu. Użyj liczby całkowitej"
                }
            ),
            400,
        )

    hotel = Hotel.query.get(id_hotel)
    if not hotel:
        return jsonify({"error": "Hotel nie istnieje"}), 404

    # Dane adresowe
    address = Address.query.get(hotel.id_address)

    # Udogodnienia hotelu
    facilities = (
        db.session.query(HotelFacility.facility_name)
        .join(
            HotelHotelFacility,
            HotelHotelFacility.id_hotel_facility == HotelFacility.id_hotel_facility,
        )
        .filter(HotelHotelFacility.id_hotel == hotel.id_hotel)
        .all()
    )
    facilities = [f.facility_name for f in hotel_facilities]

    hotel_data = {
        "id_hotel": hotel.id_hotel,
        "name": hotel.name,
        "stars": hotel.stars,
        "geo_length": hotel.geo_length,
        "geo_latitude": hotel.geo_latitude,
        "address": {
            "country": address.country,
            "city": address.city,
            "street": address.street,
            "building": address.building,
            "zip_code": address.zip_code,
        },
        "facilities": facilities,
    }
    return jsonify(hotel_data), 200


@endp_bp.route("/room/<int:id_room>", methods=["GET"])
def get_room(id_room):

    if not isinstance(id_room, int):
        return (
            jsonify(
                {
                    "error": "Nieprawidłowy format identyfikatora pokoju. Użyj liczby całkowitej"
                }
            ),
            400,
        )

    room = Room.query.get(id_room)
    if not room:
        return jsonify({"error": "Pokój nie istnieje"}), 404

    # Udogodnienia pokoju
    facilities = (
        db.session.query(RoomFacility.facility_name)
        .join(
            RoomRoomFacility,
            RoomRoomFacility.id_room_facility == RoomFacility.id_room_facility,
        )
        .filter(RoomRoomFacility.id_room == room.id_room)
        .all()
    )
    facilities = [f.facility_name for f in facilities]

    room_data = {
        "id_room": room.id_room,
        "capacity": room.capacity,
        "price_per_night": float(room.price_per_night),
        "id_hotel": room.id_hotel,
        "facilities": facilities,
    }
    return jsonify(room_data), 200
