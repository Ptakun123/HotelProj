package com.example.aplikacja;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.bumptech.glide.Glide;

import java.util.List;

public class RoomAdapter extends RecyclerView.Adapter<RoomAdapter.RoomViewHolder> {

    private List<Room> roomList;
    private OnItemClickListener listener;

    // Interfejs do obsługi kliknięcia
    public interface OnItemClickListener {
        void onItemClick(Room room);
    }

    // Konstruktor z listenerem
    public RoomAdapter(List<Room> roomList, OnItemClickListener listener) {
        this.roomList = roomList;
        this.listener = listener;
    }

    public static class RoomViewHolder extends RecyclerView.ViewHolder {
        TextView hotelName, hotelLocation, roomCapacity, price, price_per_night;
        ImageView roomImage;

        public RoomViewHolder(View itemView) {
            super(itemView);
            hotelName = itemView.findViewById(R.id.hotelName);
            hotelLocation = itemView.findViewById(R.id.hotelLocation);
            roomCapacity = itemView.findViewById(R.id.roomCapacity);
            price = itemView.findViewById(R.id.price);
            price_per_night = itemView.findViewById(R.id.price_per_night);
            roomImage = itemView.findViewById(R.id.roomImage);
        }

        // metoda pomocnicza do przypisania kliknięcia
        public void bind(Room room, OnItemClickListener listener) {
            itemView.setOnClickListener(v -> {
                if (listener != null) {
                    listener.onItemClick(room);
                }
            });
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
        holder.price.setText("Cena całkowita: " + room.total_price + " zł");
        holder.price_per_night.setText("Cena za noc " + room.price_per_night + "zł");
        holder.roomImage.setImageResource(R.drawable.sample_room); // tymczasowe zdjęcie
        Glide.with(holder.itemView.getContext()).load(room.imageURLs.get(0)).into(holder.roomImage);

        // przypisz listener do konkretnego pokoju
        holder.bind(room, listener);
    }

    @Override
    public int getItemCount() {
        return roomList.size();
    }
}
