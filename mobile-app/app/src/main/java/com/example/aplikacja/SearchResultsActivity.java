package com.example.aplikacja;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

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

    private RecyclerView recyclerView;
    private RoomAdapter adapter;
    private final OkHttpClient client = new OkHttpClient();
    private final ObjectMapper mapper = new ObjectMapper();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_search_results);

        recyclerView = findViewById(R.id.roomsRecyclerView);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));
        Intent intent = getIntent();
        HashMap<String, Object> json = new HashMap<>();

// Daty i liczba gości
        json.put("start_date", intent.getStringExtra("startDate"));
        json.put("end_date", intent.getStringExtra("endDate"));
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
        if (maxStars != null && !maxStars.isEmpty()){
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
        String country =(intent.getStringExtra("country"));
        if(country!= null && !country.isEmpty()) {
            countries.add(country);
            json.put("countries", countries);
        }
        // Kraje
        ArrayList<String> city = new ArrayList<>();
        String city_str=(intent.getStringExtra("city"));
        if(city_str!=null && !city_str.isEmpty()) {
            city.add(city_str);
            json.put("city", city);
        }
        ArrayList<String> roomFacilities = intent.getStringArrayListExtra("roomFacilities");
        ArrayList<String> hotelFacilities = intent.getStringArrayListExtra("hotelFacilities");

        json.put("room_facilities", roomFacilities != null ? roomFacilities : new ArrayList<>());
        json.put("hotel_facilities", hotelFacilities != null ? hotelFacilities : new ArrayList<>());
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

        // Wyślij zapytanie
        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(@NonNull Call call, @NonNull IOException e) {
                runOnUiThread(() -> Toast.makeText(SearchResultsActivity.this, "Błąd połączenia", Toast.LENGTH_SHORT).show());
                Log.d("My_app", "CHUUUJ");
            }

            @Override
            public void onResponse(@NonNull Call call, @NonNull Response response) throws IOException {
                if (!response.isSuccessful()) {
                    Log.d("My_app", "CHUUUJ");
                    runOnUiThread(() -> {
                        Toast.makeText(SearchResultsActivity.this, "Nie ma takich dostępnych pokoi", Toast.LENGTH_SHORT).show();
                        finish();
                        return;
                    });
                    return;
                }
                else {
                    String jsonResponse = response.body().string();
                    
                    JsonNode rootNode = mapper.readTree(jsonResponse);
                    JsonNode roomsNode = rootNode.get("available_rooms");
                    Room[] roomsArray = mapper.treeToValue(roomsNode, Room[].class);
                    List<Room> roomsList = Arrays.asList(roomsArray);
                    runOnUiThread(() -> {
                        adapter = new RoomAdapter(roomsList);
                        recyclerView.setAdapter(adapter);
                    });
                }
            }
        });
    }
}
