package com.example.aplikacja;

// Aktywność wyświetlająca wyniki wyszukiwania pokoi na podstawie filtrów przekazanych przez Intent.
// Pobiera dane z backendu, pobiera zdjęcia hoteli i przekazuje wybrany pokój do szczegółów oferty.
import android.content.Intent;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.bumptech.glide.Glide;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class SearchResultsActivity extends AppCompatActivity {

    // RecyclerView do prezentacji listy pokoi
    private RecyclerView recyclerView;
    // Adapter do obsługi listy pokoi
    private RoomAdapter adapter;
    // Klient HTTP do komunikacji z backendem
    private final OkHttpClient client = new OkHttpClient();
    // Mapper do obsługi JSON
    private final ObjectMapper mapper = new ObjectMapper();
    // Przechowywane daty pobytu
    String startDate, endDate;
    // Dane użytkownika przekazane z poprzedniej aktywności
    private UserAndTokens userAndTokens;
    // Lista pokoi do wyświetlenia
    List<Room> roomsList;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_search_results);

        recyclerView = findViewById(R.id.roomsRecyclerView);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));
        Intent intent = getIntent();
        HashMap<String, Object> json = new HashMap<>();
        userAndTokens = intent.getExtras().getParcelable("User_data");
// Daty i liczba gości
        startDate = intent.getStringExtra("startDate");
        json.put("start_date", startDate);
        endDate = intent.getStringExtra("endDate");
        json.put("end_date", endDate);
        json.put("guests", intent.getIntExtra("guests", 1));

// Ceny i gwiazdki
        String minPrice = intent.getStringExtra("minPrice");
        if (minPrice != null && !minPrice.isEmpty()) {
            json.put("lowest_price", Integer.parseInt(minPrice));
        }
        String maxPrice = intent.getStringExtra("maxPrice");
        if (maxPrice != null && !maxPrice.isEmpty()) {
            json.put("highest_price", Integer.parseInt(maxPrice));
        }
        String minStars = intent.getStringExtra("minStars");
        if (minStars != null && !minStars.isEmpty()) {
            json.put("min_hotel_stars", Integer.parseInt(minStars));
        }
        String maxStars = intent.getStringExtra("maxStars");
        if (maxStars != null && !maxStars.isEmpty()) {
            json.put("max_hotel_stars", Integer.parseInt(maxStars));
        }

// Sortowanie
        String sort_by = intent.getStringExtra("sortBy");
        if (sort_by != null && !sort_by.isEmpty()) {
            json.put("sort_by", sort_by);
        }
        String sort_order = intent.getStringExtra("sortOrder");
        if (sort_order != null && !sort_order.isEmpty()) {
            json.put("sort_order", intent.getStringExtra("sortOrder"));
        }

// Kraje
        ArrayList<String> countries = new ArrayList<>();
        String country = (intent.getStringExtra("country"));
        if (country != null && !country.isEmpty()) {
            countries.add(country);
            json.put("countries", countries);
        }
        // Kraje
        ArrayList<String> city = new ArrayList<>();
        String city_str = (intent.getStringExtra("city"));

        if (city_str != null && !city_str.isEmpty()) {
            if(city_str != "Dowolne miasto") {
                city.add(city_str);
                json.put("city", city);
            }
        }
        ArrayList<String> roomFacilities = intent.getStringArrayListExtra("roomFacilities");
        ArrayList<String> hotelFacilities = intent.getStringArrayListExtra("hotelFacilities");

        json.put("room_facilities", roomFacilities != null ? roomFacilities : new ArrayList<>());
        json.put("hotel_facilities", hotelFacilities != null ? hotelFacilities : new ArrayList<>());
        // Przygotowanie zapytania do backendu
        String jsonStr;
        try {
            jsonStr = mapper.writeValueAsString(json);
        } catch (JsonProcessingException e) {
            throw new RuntimeException(e);
        }
        RequestBody body = RequestBody.create(jsonStr, MediaType.parse("application/json"));
        Log.d("My_app", jsonStr);
        Request request = new Request.Builder()
                .url("http://10.0.2.2:5000/search_free_rooms")
                .post(body)
                .build();

        // Wyślij zapytanie o dostępne pokoje
        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(@NonNull Call call, @NonNull IOException e) {
                runOnUiThread(() -> Toast.makeText(SearchResultsActivity.this, "Błąd połączenia", Toast.LENGTH_SHORT).show());
            }

            @Override
            public void onResponse(@NonNull Call call, @NonNull Response response) throws IOException {
                if (!response.isSuccessful()) {
                    runOnUiThread(() -> {
                        Toast.makeText(SearchResultsActivity.this, "Nie ma takich dostępnych pokoi", Toast.LENGTH_SHORT).show();
                        finish();
                        return;
                    });
                    return;
                } else {
                    // Odbierz i sparsuj listę pokoi
                    String jsonResponse = response.body().string();

                    JsonNode rootNode = mapper.readTree(jsonResponse);
                    JsonNode roomsNode = rootNode.get("available_rooms");
                    Room[] roomsArray = mapper.treeToValue(roomsNode, Room[].class);
                    roomsList = Arrays.asList(roomsArray);
                    // Dla każdego pokoju pobierz zdjęcia hotelu
                    for (int i = 0; i < roomsList.size(); ++i) {
                        roomsList.get(i).imageURLs = new ArrayList<>();
                        String id_hotel = roomsList.get(i).id_hotel;
                        Request imgRequest = new Request.Builder().url("http://10.0.2.2:5000/hotel_images/" + id_hotel).build();
                        int finalI = i;
                        client.newCall(imgRequest).enqueue(new Callback() {
                            @Override
                            public void onFailure(@NonNull Call call, @NonNull IOException e) {
                                runOnUiThread(() -> Toast.makeText(SearchResultsActivity.this, "Błąd zdjęć", Toast.LENGTH_SHORT).show());
                            }

                            @Override
                            public void onResponse(@NonNull Call call, @NonNull Response response2) throws IOException {
                                if(!response2.isSuccessful()){
                                    runOnUiThread(() -> Toast.makeText(SearchResultsActivity.this, "Błąd zdjęć2", Toast.LENGTH_SHORT).show());
                                }
                                else {
                                    ObjectMapper mapper = new ObjectMapper();
                                    JsonNode rootNode = mapper.readTree(response2.body().string());
                                    Log.d("My_app", rootNode.toString());// ← Twój JSON jako string
                                    for (JsonNode node : rootNode) {
                                        String url = node.get("url").asText();
                                        Log.d("My_app", url);
                                        String fixedUrl = url.replace("localhost", "10.0.2.2");
                                        Log.d("My_app", fixedUrl);
                                        roomsList.get(finalI).imageURLs.add(fixedUrl);
                                    }
                                }
                                // Po pobraniu zdjęć do ostatniego pokoju ustaw adapter
                                if(finalI == roomsList.size()-1){
                                    runOnUiThread(() -> {
                                        adapter = new RoomAdapter(roomsList, room -> {
                                            // Obsługa kliknięcia w pokój - przejście do szczegółów oferty
                                            Intent intent = new Intent(SearchResultsActivity.this, SingleOfferActivity.class);
                                            intent.putExtra("Room_info", room);
                                            intent.putExtra("User_info", userAndTokens);
                                            intent.putExtra("Start_date", startDate);
                                            intent.putExtra("End_date", endDate);
                                            startActivity(intent);
                                        });
                                        recyclerView.setAdapter(adapter);
                                    });
                                }
                            }
                        });
                    }

                }
            }
        });
    }

}
