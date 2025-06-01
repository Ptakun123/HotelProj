package com.example.aplikacja;
import android.os.Parcel;
import android.os.Parcelable;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

public class Reservation implements Parcelable {

    public String id_reservation;
    public String first_night;
    public String last_night;
    public String full_name;
    public double price;
    public String bill_type;
    public String status;
    public String id_room;
    public String capacity;
    public double price_per_night;
    public List<String> room_facilities = new ArrayList<>();
    public String id_hotel;
    public String hotel_name;
    public String stars;
    public List<String> hotel_facilities = new ArrayList<>();

    // Konstruktor domyślny
    public Reservation() {}

    public String getLast_night() {
        return last_night;
    }

    public String getFull_name() {
        return full_name;
    }

    public double getPrice() {
        return price;
    }

    public String getId_reservation() {
        return id_reservation;
    }

    public String getFirst_night() {
        return first_night;
    }

    public String getBill_type() {
        return bill_type;
    }

    public String getStatus() {
        return status;
    }

    public String getId_room() {
        return id_room;
    }

    public String getCapacity() {
        return capacity;
    }

    public double getPrice_per_night() {
        return price_per_night;
    }

    public List<String> getRoom_facilities() {
        return room_facilities;
    }

    public String getId_hotel() {
        return id_hotel;
    }

    public String getHotel_name() {
        return hotel_name;
    }

    public String getStars() {
        return stars;
    }

    public List<String> getHotel_facilities() {
        return hotel_facilities;
    }

    // Parcel constructor
    protected Reservation(Parcel in) {
        id_reservation = in.readString();
        first_night = in.readString();
        last_night = in.readString();
        full_name = in.readString();
        price = in.readDouble();
        bill_type = in.readString();
        status = in.readString();
        id_room = in.readString();
        capacity = in.readString();
        price_per_night = in.readDouble();
        room_facilities = in.createStringArrayList();
        id_hotel = in.readString();
        hotel_name = in.readString();
        stars = in.readString();
        hotel_facilities = in.createStringArrayList();
    }

    @Override
    public void writeToParcel(Parcel dest, int flags) {
        dest.writeString(id_reservation);
        dest.writeString(first_night);
        dest.writeString(last_night);
        dest.writeString(full_name);
        dest.writeDouble(price);
        dest.writeString(bill_type);
        dest.writeString(status);
        dest.writeString(id_room);
        dest.writeString(capacity);
        dest.writeDouble(price_per_night);
        dest.writeStringList(room_facilities);
        dest.writeString(id_hotel);
        dest.writeString(hotel_name);
        dest.writeString(stars);
        dest.writeStringList(hotel_facilities);
    }

    @Override
    public int describeContents() {
        return 0;
    }

    public static final Creator<Reservation> CREATOR = new Creator<Reservation>() {
        @Override
        public Reservation createFromParcel(Parcel in) {
            return new Reservation(in);
        }

        @Override
        public Reservation[] newArray(int size) {
            return new Reservation[size];
        }
    };

    public static Reservation fromJson(JSONObject obj) throws JSONException {
        Reservation res = new Reservation();
        res.id_reservation = obj.getString("id_reservation");
        res.full_name = obj.getString("full_name");
        res.first_night = obj.getString("first_night");
        res.last_night = obj.getString("last_night");
        res.price = obj.getDouble("price");
        res.bill_type = obj.getString("bill_type");
        res.status = obj.getString("status");

        // ROOM
        JSONObject roominfo = obj.getJSONObject("room");
        res.id_room = roominfo.getString("id_room");
        res.capacity = roominfo.getString("capacity");
        res.price_per_night = roominfo.getDouble("price_per_night");

        JSONArray roomFacilitiesArray = roominfo.getJSONArray("facilities");
        for (int i = 0; i < roomFacilitiesArray.length(); i++) {
            res.room_facilities.add(roomFacilitiesArray.getString(i));
        }

        // HOTEL
        JSONObject hotelinfo = obj.getJSONObject("hotel");
        res.id_hotel = hotelinfo.getString("id_hotel");
        res.hotel_name = hotelinfo.getString("name");
        res.stars = hotelinfo.getString("stars");

        JSONArray hotelFacilitiesArray = hotelinfo.getJSONArray("facilities");
        for (int i = 0; i < hotelFacilitiesArray.length(); i++) {
            res.hotel_facilities.add(hotelFacilitiesArray.getString(i));
        }

        return res;
    }
}