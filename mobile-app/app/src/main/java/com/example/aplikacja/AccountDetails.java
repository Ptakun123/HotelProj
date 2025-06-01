package com.example.aplikacja;

// Klasa odpowiedzialna za wyświetlanie szczegółów konta użytkownika oraz jego aktywnych rezerwacji.
// Pozwala na zmianę hasła oraz anulowanie rezerwacji.
import android.content.DialogInterface;
import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class AccountDetails extends AppCompatActivity {
    // Wyświetla informacje o użytkowniku
    private TextView userInfo;
    // RecyclerView do prezentacji listy rezerwacji
    private RecyclerView reservationsRecycler;
    // Adapter do obsługi listy rezerwacji
    private ReservationAdapter adapter;
    // Lista rezerwacji użytkownika
    private List<Reservation> reservationList = new ArrayList<>();
    // Dane użytkownika przekazane z poprzedniej aktywności
    private UserAndTokens userData;
    // Klient HTTP do komunikacji z backendem
    private OkHttpClient client = new OkHttpClient();

    private Button changepassword;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_user_details);

        userInfo = findViewById(R.id.userInfo);

        reservationsRecycler = findViewById(R.id.reservationsRecycler);
        reservationsRecycler.setLayoutManager(new LinearLayoutManager(this));

        // Pobranie danych użytkownika przekazanych przez Intent
        userData = getIntent().getParcelableExtra("User_details");

        adapter = new ReservationAdapter(this, reservationList, userData);
        reservationsRecycler.setAdapter(adapter);

        changepassword = findViewById(R.id.change_password);
        // Obsługa przycisku zmiany hasła
        changepassword.setOnClickListener( v -> {
            Intent intent1 = new Intent(this, ChangePassword.class);
            intent1.putExtra("User_details", userData);
            startActivity(intent1);
        });

        if (userData != null) {
            displayUserInfo();
            // Pobranie aktywnych rezerwacji użytkownika z serwera
            fetchReservations(userData.user_id, userData.access_token);
        }
    }

    // Wyświetla podstawowe informacje o użytkowniku
    private void displayUserInfo() {
        String info = "Imię: " + userData.first_name + "\n" +
                "Nazwisko: " + userData.last_name + "\n" +
                "Email: " + userData.email;
        userInfo.setText(info);
    }

    // Pobiera z serwera aktywne rezerwacje użytkownika
    private void fetchReservations(int userId, String token) {
        String url = "http://10.0.2.2:5000/user/" + userId + "/reservations?status=active";

        Request request = new Request.Builder()
                .url(url)
                .addHeader("Authorization", "Bearer " + token)
                .build();

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                // Obsługa błędu sieci
                runOnUiThread(() -> Toast.makeText(AccountDetails.this, "Błąd sieci: " + e.getMessage(), Toast.LENGTH_SHORT).show());
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                if (!response.isSuccessful()) {
                    // Obsługa przypadku braku rezerwacji
                    if(response.code() == 404)
                    runOnUiThread(() -> Toast.makeText(AccountDetails.this, "Nie masz rezerwacji", Toast.LENGTH_SHORT).show());
                    return;
                }

                String responseBody = response.body().string();
                try {
                    JSONObject json = new JSONObject(responseBody);
                    JSONArray reservations = json.getJSONArray("reservations");

                    reservationList.clear();
                    for (int i = 0; i < reservations.length(); i++) {
                        JSONObject obj = reservations.getJSONObject(i);
                        Reservation reservation = Reservation.fromJson(obj);
                        reservationList.add(reservation);
                    }

                    // Odświeżenie widoku listy rezerwacji
                    runOnUiThread(() -> adapter.notifyDataSetChanged());

                } catch (JSONException e) {
                    runOnUiThread(() -> Toast.makeText(AccountDetails.this, "Błąd JSON: " + e.getMessage(), Toast.LENGTH_SHORT).show());
                }
            }
        });
    }

    // Wyświetla okno dialogowe z potwierdzeniem anulowania rezerwacji
    private void confirmCancellation(Reservation reservation) {
        new AlertDialog.Builder(this)
                .setTitle("Potwierdzenie")
                .setMessage("Czy na pewno chcesz anulować rezerwację?")
                .setPositiveButton("Tak", (dialog, which) -> cancelReservation(reservation))
                .setNegativeButton("Nie", null)
                .show();
    }

    // Wysyła żądanie anulowania rezerwacji do backendu
    private void cancelReservation(Reservation reservation) {
        String url = "http://10.0.2.2:5000/post_cancellation";

        JSONObject json = new JSONObject();
        try {
            json.put("id_reservation", reservation.getId_reservation());
            json.put("id_user", userData.user_id);
        } catch (JSONException e) {
            Toast.makeText(this, "Błąd JSON: " + e.getMessage(), Toast.LENGTH_SHORT).show();
            return;
        }

        RequestBody body = RequestBody.create(
                json.toString(),
                MediaType.parse("application/json")
        );

        Request request = new Request.Builder()
                .url(url)
                .post(body)
                .addHeader("Authorization", "Bearer " + userData.access_token)
                .build();

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                // Obsługa błędu anulowania rezerwacji
                runOnUiThread(() ->
                        Toast.makeText(AccountDetails.this, "Błąd anulowania: " + e.getMessage(), Toast.LENGTH_SHORT).show());
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                String message;
                if (response.isSuccessful()) {
                    message = "Rezerwacja anulowana";
                    // Po anulowaniu odśwież listę rezerwacji
                    fetchReservations(userData.user_id, userData.access_token); // reload list
                } else {
                    message = "Błąd: " + response.code();
                }

                runOnUiThread(() ->
                        Toast.makeText(AccountDetails.this, message, Toast.LENGTH_SHORT).show());
            }
        });
    }
}
