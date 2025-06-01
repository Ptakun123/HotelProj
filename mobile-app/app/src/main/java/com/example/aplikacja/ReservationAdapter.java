package com.example.aplikacja;

// Adapter do wyświetlania listy rezerwacji użytkownika w RecyclerView.
// Pozwala na anulowanie rezerwacji bezpośrednio z listy.
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.List;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class ReservationAdapter extends RecyclerView.Adapter<ReservationAdapter.ViewHolder> {

    // Kontekst aktywności/fragmentu
    private final Context context;
    // Lista rezerwacji do wyświetlenia
    private final List<Reservation> reservations;
    // Dane użytkownika (tokeny, id)
    UserAndTokens userAndTokens;

    public ReservationAdapter(Context context, List<Reservation> reservations, UserAndTokens userAndTokens) {
        this.context = context;
        this.reservations = reservations;
        this.userAndTokens = userAndTokens;
    }

    // ViewHolder przechowujący referencje do widoków pojedynczego elementu listy
    public static class ViewHolder extends RecyclerView.ViewHolder {
        TextView textHotelName, textReservationDates, textReservationPrice;
        Button buttonCancel;

        public ViewHolder(View itemView) {
            super(itemView);
            textHotelName = itemView.findViewById(R.id.textHotelName);
            textReservationDates = itemView.findViewById(R.id.textReservationDates);
            textReservationPrice = itemView.findViewById(R.id.textReservationPrice);
            buttonCancel = itemView.findViewById(R.id.buttonCancel);
        }
    }

    @NonNull
    @Override
    public ReservationAdapter.ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        // Tworzy widok pojedynczej rezerwacji
        View view = LayoutInflater.from(context).inflate(R.layout.item_reservation, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull ReservationAdapter.ViewHolder holder, int position) {
        // Przypisuje dane rezerwacji do widoku
        Reservation reservation = reservations.get(position);

        holder.textHotelName.setText(reservation.getHotel_name());
        holder.textReservationDates.setText(reservation.getFirst_night() + " - " + reservation.getLast_night());
        holder.textReservationPrice.setText("Cena: " + reservation.getPrice() + " PLN");

        // Obsługa przycisku anulowania rezerwacji
        holder.buttonCancel.setOnClickListener(v -> {
            new AlertDialog.Builder(context)
                    .setTitle("Anuluj rezerwację")
                    .setMessage("Czy na pewno chcesz anulować tę rezerwację?")
                    .setPositiveButton("Tak", (dialog, which) -> {
                        cancelReservation(Integer.parseInt(reservation.getId_reservation()), position);
                    })
                    .setNegativeButton("Nie", null)
                    .show();
        });
    }

    @Override
    public int getItemCount() {
        // Zwraca liczbę rezerwacji
        return reservations.size();
    }

    // Wysyła żądanie anulowania rezerwacji do backendu i usuwa ją z listy po sukcesie
    private void cancelReservation(int reservationId, int position) {
        OkHttpClient client = new OkHttpClient();

        JSONObject json = new JSONObject();
        try {
            json.put("id_reservation", reservationId);
            json.put("id_user", userAndTokens.user_id);
        } catch (JSONException e) {
            e.printStackTrace();
            return;
        }

        RequestBody body = RequestBody.create(json.toString(), MediaType.get("application/json"));
        Request request = new Request.Builder()
                .url("http://10.0.2.2:5000/post_cancellation")
                .addHeader("Authorization", "Bearer " + userAndTokens.access_token)
                .post(body)
                .build();

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                // Obsługa błędu sieci
                ((Activity) context).runOnUiThread(() ->
                        Toast.makeText(context, "Błąd sieci: " + e.getMessage(), Toast.LENGTH_SHORT).show()
                );
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                ((Activity) context).runOnUiThread(() -> {
                    if (response.isSuccessful()) {
                        // Usunięcie rezerwacji z listy po anulowaniu
                        reservations.remove(position);
                        notifyItemRemoved(position);
                        Toast.makeText(context, "Rezerwacja anulowana", Toast.LENGTH_SHORT).show();
                    } else {
                        Toast.makeText(context, "Błąd anulowania: " + response.code(), Toast.LENGTH_SHORT).show();
                    }
                });
            }
        });
    }
}