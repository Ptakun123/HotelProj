package com.example.aplikacja;

import android.os.Parcel;
import android.os.Parcelable;

import java.util.ArrayList;
import java.util.List;

public class Room implements Parcelable {
    public int capacity;
    public String city;
    public String country;
    public String hotel_name;
    public String hotel_id;
    public int hotel_stars;
    public int id_room;
    public double price_per_night;
    public ArrayList<String> imageURLs;
    public double total_price;
    private List<String> facilities;

    // Constructor
    public Room() {
    }

    // Parcelable constructor
    protected Room(Parcel in) {
        capacity = in.readInt();
        city = in.readString();
        country = in.readString();
        hotel_name = in.readString();
        hotel_id = in.readString();
        hotel_stars = in.readInt();
        id_room = in.readInt();
        price_per_night = in.readDouble();
        imageURLs = in.createStringArrayList();
        total_price = in.readDouble();
    }

    @Override
    public void writeToParcel(Parcel dest, int flags) {
        dest.writeInt(capacity);
        dest.writeString(city);
        dest.writeString(country);
        dest.writeString(hotel_name);
        dest.writeString(hotel_id);
        dest.writeInt(hotel_stars);
        dest.writeInt(id_room);
        dest.writeDouble(price_per_night);
        dest.writeStringList(imageURLs);
        dest.writeDouble(total_price);
    }

    @Override
    public int describeContents() {
        return 0;
    }

    public static final Creator<Room> CREATOR = new Creator<Room>() {
        @Override
        public Room createFromParcel(Parcel in) {
            return new Room(in);
        }

        @Override
        public Room[] newArray(int size) {
            return new Room[size];
        }
    };
    public int getIdRoom() {
        return id_room;
    }

    public int getCapacity() {
        return capacity;
    }

    public double getPricePerNight() {
        return price_per_night;
    }

    public List<String> getFacilities() {
        return facilities;
    }
}
