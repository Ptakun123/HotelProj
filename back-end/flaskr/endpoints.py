from flask import Blueprint, request, jsonify
from models import *
from datetime import timedelta, datetime
from extensions import db
from sqlalchemy.sql import text

endp_bp = Blueprint("endp", __name__)


@endp_bp.route("/search_free_rooms", methods=["POST"])
def search_free_rooms():
    try:
        data = request.get_json()

        # Required fields
        required_fields = ["start_date", "end_date", "guests"]
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

        # Optional filters
        try:
            lowest_price = float(data["lowest_price"])
            highest_price = float(data["highest_price"])
        except ValueError:
            return (
                jsonify({"error": "Ceny muszą być liczbami"}),
                400,
            )

        room_facilities = data.get("room_facilities")
        hotel_facilities = data.get("hotel_facilities")
        countries = data.get("countries")
        cities = data.get("city")

        if room_facilities and not (
            isinstance(room_facilities, list)
            and all(isinstance(f, str) for f in room_facilities)
        ):
            return (
                jsonify({"error": "Udogodnienia pokoi muszą być listą stringów"}),
                400,
            )
        if hotel_facilities and not (
            isinstance(hotel_facilities, list)
            and all(isinstance(f, str) for f in hotel_facilities)
        ):
            return (
                jsonify({"error": "Udogodnienia hotelu muszą być listą stringów"}),
                400,
            )
        if countries and not (
            isinstance(countries, list) and all(isinstance(c, str) for c in countries)
        ):
            return (
                jsonify({"error": "Państwa muszą być listą stringów"}),
                400,
            )
        if cities and not (
            isinstance(cities, list) and all(isinstance(c, str) for c in cities)
        ):
            return (
                jsonify({"error": "Miasta muszą być listą stringów"}),
                400,
            )

        try:
            min_hotel_stars = int(data["min_hotel_stars"])
            max_hotel_stars = int(data["max_hotel_stars"])
        except ValueError:
            return (
                jsonify(
                    {"error": "Liczby gwiazdek hotelu muszą być liczbami całkowitymi"}
                ),
                400,
            )

        if min_hotel_stars not in range(1, 6) or max_hotel_stars not in range(1, 6):
            return (
                jsonify(
                    {
                        "error": "Liczby gwiazdek hotelu muszą należeć do przedziału od 1 do 5"
                    }
                ),
                400,
            )

        # Build base query
        nights = (end_date - start_date).days
        query_str = """
            SELECT r.id_room, r.capacity, r.price_per_night, h.name AS hotel_name, a.city, a.country, h.stars
            FROM rooms r
            JOIN hotels h ON r.id_hotel = h.id_hotel
            JOIN addresses a ON h.id_address = a.id_address
        """
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "guests": guests,
        }
        where_clauses = [
            "r.capacity >= :guests",
            "r.id_room NOT IN (SELECT id_room FROM reservations WHERE (first_night, last_night) OVERLAPS (:start_date, :end_date))",
        ]

        # City/country logic
        if cities:
            where_clauses.append("a.city IN :cities")
            params["cities"] = tuple(cities)
        elif countries:
            where_clauses.append("a.country IN :countries")
            params["countries"] = tuple(countries)

        # Hotel stars
        if min_hotel_stars is not None:
            where_clauses.append("h.stars >= :min_hotel_stars")
            params["min_hotel_stars"] = min_hotel_stars
        if max_hotel_stars is not None:
            where_clauses.append("h.stars <= :max_hotel_stars")
            params["max_hotel_stars"] = max_hotel_stars

        # Price range for the whole stay
        if lowest_price is not None:
            where_clauses.append("(r.price_per_night * :nights) >= :lowest_price")
            params["lowest_price"] = lowest_price
            params["nights"] = nights
        if highest_price is not None:
            where_clauses.append("(r.price_per_night * :nights) <= :highest_price")
            params["highest_price"] = highest_price
            params["nights"] = nights

        # Room facilities
        if room_facilities:
            query_str += """
                JOIN rooms_room_facilities rrf ON rrf.id_room = r.id_room
                JOIN room_facilities rf ON rrf.id_room_facility = rf.id_room_facility
            """
            where_clauses.append("rf.facility_name IN :room_facilities")
            params["room_facilities"] = tuple(room_facilities)
            # Ensure all required facilities are present
            group_by = " GROUP BY r.id_room, r.capacity, r.price_per_night, h.name, a.city, a.country, h.stars"
            having = (
                f" HAVING COUNT(DISTINCT rf.facility_name) = {len(room_facilities)}"
            )
        else:
            group_by = ""
            having = ""

        # Hotel facilities
        if hotel_facilities:
            query_str += """
                JOIN hotels_hotel_facilities hhf ON hhf.id_hotel = h.id_hotel
                JOIN hotel_facilities hf ON hhf.id_hotel_facility = hf.id_hotel_facility
            """
            where_clauses.append("hf.facility_name IN :hotel_facilities")
            params["hotel_facilities"] = tuple(hotel_facilities)
            # Ensure all required hotel facilities are present
            if group_by == "":
                group_by = " GROUP BY r.id_room, r.capacity, r.price_per_night, h.name, a.city, a.country, h.stars"
            having += (
                f" AND COUNT(DISTINCT hf.facility_name) = {len(hotel_facilities)}"
                if having
                else f" HAVING COUNT(DISTINCT hf.facility_name) = {len(hotel_facilities)}"
            )

        # Finalize query
        if where_clauses:
            query_str += " WHERE " + " AND ".join(where_clauses)
        query_str += group_by
        query_str += having

        query = db.session.execute(text(query_str), params)

        rooms = [
            {
                "id_room": row.id_room,
                "capacity": row.capacity,
                "price_per_night": float(row.price_per_night),
                "hotel_name": row.hotel_name,
                "city": row.city,
                "country": row.country,
                "hotel_stars": row.stars,
            }
            for row in query
        ]

        if not rooms:
            return (
                jsonify({"message": "Brak dostępnych pokoi dla podanych kryteriów"}),
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
            reservation_status="A",
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

    if status_arg not in {"active", "cancelled"}:
        return (
            jsonify(
                {
                    "error": "Nieprawidłowy format statusu rezerwacji. Użyj 'active' dla aktywnych lub 'cancelled' dla anulowanych"
                }
            ),
            400,
        )

    match status_arg:
        case "active":
            status_string = "aktywnych"
            status = "A"
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
                "status": res.reservation_status,
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
    facilities = [f.facility_name for f in facilities]

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
