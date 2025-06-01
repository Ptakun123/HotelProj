package com.example.aplikacja;

// Aktywność wyświetlająca szczegóły wybranej oferty pokoju hotelowego.
// Pozwala na rezerwację pokoju oraz wyświetla lokalizację hotelu na mapie.
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.viewpager2.widget.ViewPager2;

import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.OnMapReadyCallback;
import com.google.android.gms.maps.SupportMapFragment;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.MarkerOptions;

import org.json.JSONObject;

import java.io.IOException;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class SingleOfferActivity extends AppCompatActivity implements OnMapReadyCallback {

    // Dane pokoju i użytkownika przekazane przez Intent
    private Room room;
    private UserAndTokens user;
    String stardDate, endDate;
    // Obiekt mapy Google
    private GoogleMap mMap;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.single_offer_activity);

        // Odbierz dane z Intent
        Intent intent = getIntent();
        room = intent.getParcelableExtra("Room_info");
        user = intent.getParcelableExtra("User_info");
        stardDate = intent.getStringExtra("Start_date");
        endDate = intent.getStringExtra("End_date");

        // Znajdź widoki
        TextView tvHotelName = findViewById(R.id.tvHotelName);
        TextView tvLocation = findViewById(R.id.tvLocation);
        TextView tvStars = findViewById(R.id.tvStars);
        TextView tvCapacity = findViewById(R.id.tvCapacity);
        TextView tvPrice = findViewById(R.id.tvPrice);
        TextView tvTotalPrice = findViewById(R.id.tvTotalPrice);
        TextView tvStayDates = findViewById(R.id.tvStayDates);
        Button btnReserve = findViewById(R.id.btnReserve);
        EditText etFullName = findViewById(R.id.etFullName);
        CheckBox cbInvoice = findViewById(R.id.cbInvoice);
        EditText etNip = findViewById(R.id.etNip);

        // Obsługa widoczności pola NIP w zależności od wyboru faktury
        cbInvoice.setOnCheckedChangeListener((buttonView, isChecked) -> {
            if(isChecked)
                etNip.setVisibility(ViewPager2.VISIBLE);
            if (!isChecked) {
                etNip.setVisibility(ViewPager2.GONE);
                etNip.setText(""); // opcjonalnie czyści pole NIP
            }
        });

        // Inicjalizacja mapy Google
        SupportMapFragment mapFragment = (SupportMapFragment) getSupportFragmentManager()
                .findFragmentById(R.id.mapFragment);
        if (mapFragment != null) {
            mapFragment.getMapAsync(this);
        }

        // Wypełnij widoki danymi pokoju i hotelu
        if (room != null) {
            tvHotelName.setText(room.hotel_name);
            tvLocation.setText(room.city + ", " + room.country);
            tvStars.setText("⭐ " + room.hotel_stars);
            tvCapacity.setText("Pojemność: " + room.capacity + " osób");
            tvPrice.setText("Cena za noc: " + room.price_per_night + " zł");
            tvTotalPrice.setText("Cena całkowita: " + room.total_price + " zł");
            tvStayDates.setText("Od: " + stardDate+" Do: "+endDate);
        }

        // Ustaw adapter do wyświetlania zdjęć pokoju
        ViewPager2 viewPager = findViewById(R.id.viewPagerImages);
        if (room != null && room.imageURLs != null && !room.imageURLs.isEmpty()) {
            ImagePagerAdapter adapter = new ImagePagerAdapter(this, room.imageURLs);
            viewPager.setAdapter(adapter);
        }

        // Obsługa przycisku rezerwacji
        btnReserve.setOnClickListener(v -> {
            String fullName = etFullName.getText().toString().trim();
            boolean wantsInvoice = cbInvoice.isChecked();
            String billType = wantsInvoice ? "I" : "R";

            if (fullName.isEmpty()) {
                Toast.makeText(this, "Podaj imię i nazwisko", Toast.LENGTH_SHORT).show();
                return;
            }

            // Przygotowanie danych rezerwacji do wysłania
            JSONObject reservationJson = new JSONObject();
            try {
                reservationJson.put("id_room", room.id_room);
                reservationJson.put("id_user", user.user_id);
                reservationJson.put("first_night", stardDate);  // np. "2025-06-10"
                reservationJson.put("last_night", endDate);    // np. "2025-06-12"
                reservationJson.put("full_name", fullName);
                reservationJson.put("bill_type", billType);
                if(billType == "I") {
                    String nip =etNip.getText().toString();
                    reservationJson.put("nip", nip);
                }
            } catch (Exception e) {
                e.printStackTrace();
                Toast.makeText(this, "Błąd przy tworzeniu danych", Toast.LENGTH_SHORT).show();
                return;
            }

            // Wyślij żądanie rezerwacji do backendu
            sendReservationRequest(reservationJson.toString(), user.access_token);
        });
    }

    // Wysyła żądanie rezerwacji do backendu
    private void sendReservationRequest(String jsonBody, String jwtToken) {
        OkHttpClient client = new OkHttpClient();

        MediaType JSON = MediaType.get("application/json; charset=utf-8");
        RequestBody body = RequestBody.create(jsonBody, JSON);

        Request request = new Request.Builder()
                .url("http://10.0.2.2:5000/post_reservation") // Zmień na właściwy URL
                .post(body)
                .addHeader("Authorization", "Bearer " + jwtToken)
                .addHeader("Accept", "application/json")
                .build();
        Log.d("My_app", request.toString());
        Log.d("My_app", jsonBody.toString());
        client.newCall(request).enqueue(new okhttp3.Callback() {
            @Override
            public void onFailure(okhttp3.Call call, IOException e) {
                runOnUiThread(() -> Toast.makeText(SingleOfferActivity.this, "Błąd sieci: " + e.getMessage(), Toast.LENGTH_LONG).show());
            }

            @Override
            public void onResponse(okhttp3.Call call, Response response) throws IOException {
                runOnUiThread(() -> {
                    if (response.isSuccessful()) {
                        Toast.makeText(SingleOfferActivity.this, "Rezerwacja zakończona sukcesem", Toast.LENGTH_LONG).show();
                        finish();
                    } else {
                        try {
                            Toast.makeText(SingleOfferActivity.this, "Błąd rezerwacji: " + response.body().string(), Toast.LENGTH_LONG).show();
                        } catch (IOException e) {
                            throw new RuntimeException(e);
                        }
                    }
                });
            }
        });
    }

    // Callback po przygotowaniu mapy Google
    public void onMapReady(GoogleMap googleMap) {
        mMap = googleMap;

        if (room != null) {
            fetchHotelLocation(Integer.parseInt(room.id_hotel));
        }
    }

    // Pobiera lokalizację hotelu z backendu i ustawia marker na mapie
    private void fetchHotelLocation(int hotelId) {
        OkHttpClient client = new OkHttpClient();
        String url = "http://10.0.2.2:5000/hotel/" + hotelId;

        Request request = new Request.Builder()
                .url(url)
                .get()
                .build();

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                runOnUiThread(() ->
                        Toast.makeText(SingleOfferActivity.this, "Błąd pobierania lokalizacji hotelu", Toast.LENGTH_SHORT).show());
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                if (!response.isSuccessful()) {
                    runOnUiThread(() ->
                            Toast.makeText(SingleOfferActivity.this, "Błąd serwera przy pobieraniu lokalizacji hotelu", Toast.LENGTH_SHORT).show());
                    return;
                }

                String responseData = response.body().string();
                try {
                    JSONObject jsonObject = new JSONObject(responseData);
                    double latitude = jsonObject.getDouble("geo_latitude");
                    double longitude = jsonObject.getDouble("geo_length");

                    runOnUiThread(() -> {
                        LatLng hotelLocation = new LatLng(latitude, longitude);
                        mMap.addMarker(new MarkerOptions().position(hotelLocation).title(room.hotel_name));
                        mMap.moveCamera(CameraUpdateFactory.newLatLngZoom(hotelLocation, 15f));
                    });
                } catch (Exception e) {
                    e.printStackTrace();
                    runOnUiThread(() ->
                            Toast.makeText(SingleOfferActivity.this, "Błąd parsowania lokalizacji hotelu", Toast.LENGTH_SHORT).show());
                }
            }
        });
    }
}
