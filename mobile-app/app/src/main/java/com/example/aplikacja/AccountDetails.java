package com.example.aplikacja;

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
    private TextView userInfo;
    private RecyclerView reservationsRecycler;
    private ReservationAdapter adapter;
    private List<Reservation> reservationList = new ArrayList<>();
    private UserAndTokens userData;
    private OkHttpClient client = new OkHttpClient();

    private Button changepassword;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_user_details);

        userInfo = findViewById(R.id.userInfo);

        reservationsRecycler = findViewById(R.id.reservationsRecycler);
        reservationsRecycler.setLayoutManager(new LinearLayoutManager(this));

        userData = getIntent().getParcelableExtra("User_details");

        adapter = new ReservationAdapter(this, reservationList, userData);
        reservationsRecycler.setAdapter(adapter);
        changepassword = findViewById(R.id.change_password);
        changepassword.setOnClickListener( v -> {
            Intent intent1 = new Intent(this, ChangePassword.class);
            intent1.putExtra("User_details", userData);
            startActivity(intent1);
        });
        if (userData != null) {
            displayUserInfo();
            fetchReservations(userData.user_id, userData.access_token);
        }
    }

    private void displayUserInfo() {
        String info = "Imię: " + userData.first_name + "\n" +
                "Nazwisko: " + userData.last_name + "\n" +
                "Email: " + userData.email;
        userInfo.setText(info);
    }

    private void fetchReservations(int userId, String token) {
        String url = "http://10.0.2.2:5000/user/" + userId + "/reservations?status=active";

        Request request = new Request.Builder()
                .url(url)
                .addHeader("Authorization", "Bearer " + token)
                .build();

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                runOnUiThread(() -> Toast.makeText(AccountDetails.this, "Błąd sieci: " + e.getMessage(), Toast.LENGTH_SHORT).show());
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                if (!response.isSuccessful()) {
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

                    runOnUiThread(() -> adapter.notifyDataSetChanged());

                } catch (JSONException e) {
                    runOnUiThread(() -> Toast.makeText(AccountDetails.this, "Błąd JSON: " + e.getMessage(), Toast.LENGTH_SHORT).show());
                }
            }
        });
    }

    private void confirmCancellation(Reservation reservation) {
        new AlertDialog.Builder(this)
                .setTitle("Potwierdzenie")
                .setMessage("Czy na pewno chcesz anulować rezerwację?")
                .setPositiveButton("Tak", (dialog, which) -> cancelReservation(reservation))
                .setNegativeButton("Nie", null)
                .show();
    }

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
                runOnUiThread(() ->
                        Toast.makeText(AccountDetails.this, "Błąd anulowania: " + e.getMessage(), Toast.LENGTH_SHORT).show());
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                String message;
                if (response.isSuccessful()) {
                    message = "Rezerwacja anulowana";
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
