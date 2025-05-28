package com.example.aplikacja;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import java.util.List;

public class RoomAdapter extends RecyclerView.Adapter<RoomAdapter.RoomViewHolder> {
    private List<Room> roomList;

    public RoomAdapter(List<Room> roomList) {
        this.roomList = roomList;
    }

    public static class RoomViewHolder extends RecyclerView.ViewHolder {
        TextView hotelName, hotelLocation, roomCapacity, price;
        ImageView roomImage;

        public RoomViewHolder(View itemView) {
            super(itemView);
            hotelName = itemView.findViewById(R.id.hotelName);
            hotelLocation = itemView.findViewById(R.id.hotelLocation);
            roomCapacity = itemView.findViewById(R.id.roomCapacity);
            price = itemView.findViewById(R.id.price);
            roomImage = itemView.findViewById(R.id.roomImage);
        }
    }

    @NonNull
    @Override
    public RoomViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View v = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_room, parent, false);
        return new RoomViewHolder(v);
    }

    @Override
    public void onBindViewHolder(@NonNull RoomViewHolder holder, int position) {
        Room room = roomList.get(position);
        holder.hotelName.setText(room.hotel_name + " ★" + room.hotel_stars);
        holder.hotelLocation.setText(room.city + ", " + room.country);
        holder.roomCapacity.setText("Dla " + room.capacity + " osób");
        holder.price.setText("Cena: " + room.total_price + " zł");
        holder.roomImage.setImageResource(R.drawable.sample_room); // tymczasowe zdjęcie
    }

    @Override
    public int getItemCount() {
        return roomList.size();
    }
}
