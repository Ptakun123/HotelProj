package com.example.aplikacja;

import android.content.DialogInterface;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.android.material.datepicker.MaterialDatePicker;
import com.google.android.material.dialog.MaterialAlertDialogBuilder;

import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.Locale;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

public class MainActivity extends AppCompatActivity implements View.OnClickListener {
    Button chooseDestination;
    Button chooseDate;
    EditText guests, minPrice, maxPrice, minStars, maxStars;
    String[] countries, cities;
    String chosencountry, chosencity, startDate, endDate;
    UserAndTokens userAndTokens;
    int nights;
    ObjectMapper mapper;
    Button chooseRoomFacilities;
    Button chooseHotelFacilities;
    String[] roomFacilities, hotelFacilities;
    boolean[] selectedRoomFacilities, selectedHotelFacilities;
    private String selectedSortBy = null;
    private String selectedSortOrder = null;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Intent intent =getIntent();
        mapper = new ObjectMapper();
        userAndTokens = intent.getExtras().getParcelable("User_data");
        TextView hello = findViewById(R.id.hello);
        chooseDestination = findViewById(R.id.chooseDestination);
        chooseDestination.setOnClickListener(this);
        chooseDate = findViewById(R.id.chooseDate);
        chooseDate.setOnClickListener(this);
        hello.setText("Witaj " + userAndTokens.getFirst_name() + " " + userAndTokens.getLast_name());
        chooseRoomFacilities = findViewById(R.id.chooseRoomFacilities);
        chooseHotelFacilities = findViewById(R.id.chooseHotelFacilities);
        guests = findViewById(R.id.guestsInput);
        minPrice = findViewById(R.id.price_from);
        maxPrice = findViewById(R.id.price_to);
        minStars = findViewById(R.id.editStarsFrom);
        maxStars = findViewById(R.id.editStarsTo);
        Button btnToggleFilters = findViewById(R.id.btnToggleFilters);
        View additionalFiltersContainer = findViewById(R.id.additionalFiltersContainer);

        btnToggleFilters.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (additionalFiltersContainer.getVisibility() == View.GONE) {
                    additionalFiltersContainer.setVisibility(View.VISIBLE);
                    btnToggleFilters.setText("Ukryj dodatkowe filtry");
                } else {
                    additionalFiltersContainer.setVisibility(View.GONE);
                    btnToggleFilters.setText("Dodatkowe filtry");
                }
            }
        });

        chooseRoomFacilities.setOnClickListener(this);
        chooseHotelFacilities.setOnClickListener(this);
        Button btnSortBy = findViewById(R.id.btnSortBy);
        Button btnSortOrder = findViewById(R.id.btnSortOrder);
        Button search = findViewById(R.id.search);
        Button my_account = findViewById(R.id.my_account);
        my_account.setOnClickListener(v ->{
            Intent intent1 = new Intent(this, AccountDetails.class);
            intent1.putExtra("User_details", userAndTokens);
            startActivity(intent1);
        });
        search.setOnClickListener(v -> {
            if (startDate == null || endDate == null || guests.getText().length()==0) {
                Toast.makeText(this, "Musisz wybrać termin oraz liczbę gości", Toast.LENGTH_SHORT).show();
                return;
            }
            String minStarsStr = minStars.getText().toString().trim();
            String maxStarsStr = maxStars.getText().toString().trim();
            String minPriceStr = minPrice.getText().toString().trim();
            String maxPriceStr = maxPrice.getText().toString().trim();
            String guestsStr = guests.getText().toString().trim();

// goście - wymagane
            if (guestsStr.isEmpty()) {
                Toast.makeText(this, "Musisz podać liczbę gości", Toast.LENGTH_SHORT).show();
                return;
            }

            int intMinStars = -1, intMaxStars = -1, intMinPrice = -1, intMaxPrice = -1, intGuests;

            try {
                intGuests = Integer.parseInt(guestsStr);
            } catch (NumberFormatException e) {
                Toast.makeText(this, "Nieprawidłowa liczba gości", Toast.LENGTH_SHORT).show();
                return;
            }

// gwiazdki - jeśli podane, parsuj
            if (!minStarsStr.isEmpty()) {
                try {
                    intMinStars = Integer.parseInt(minStarsStr);
                    if (intMinStars < 1 || intMinStars > 5) {
                        Toast.makeText(this, "Minimalna liczba gwiazdek musi być 1–5", Toast.LENGTH_SHORT).show();
                        return;
                    }
                } catch (NumberFormatException e) {
                    Toast.makeText(this, "Nieprawidłowa minimalna liczba gwiazdek", Toast.LENGTH_SHORT).show();
                    return;
                }
            }
            if (!maxStarsStr.isEmpty()) {
                try {
                    intMaxStars = Integer.parseInt(maxStarsStr);
                    if (intMaxStars < 1 || intMaxStars > 5) {
                        Toast.makeText(this, "Maksymalna liczba gwiazdek musi być 1–5", Toast.LENGTH_SHORT).show();
                        return;
                    }
                } catch (NumberFormatException e) {
                    Toast.makeText(this, "Nieprawidłowa maksymalna liczba gwiazdek", Toast.LENGTH_SHORT).show();
                    return;
                }
            }

// ceny - jeśli podane, parsuj
            if (!minPriceStr.isEmpty()) {
                try {
                    intMinPrice = Integer.parseInt(minPriceStr);
                    if (intMinPrice < 0) {
                        Toast.makeText(this, "Minimalna cena nie może być ujemna", Toast.LENGTH_SHORT).show();
                        return;
                    }
                } catch (NumberFormatException e) {
                    Toast.makeText(this, "Nieprawidłowa minimalna cena", Toast.LENGTH_SHORT).show();
                    return;
                }
            }
            if (!maxPriceStr.isEmpty()) {
                try {
                    intMaxPrice = Integer.parseInt(maxPriceStr);
                    if (intMaxPrice < 0) {
                        Toast.makeText(this, "Maksymalna cena nie może być ujemna", Toast.LENGTH_SHORT).show();
                        return;
                    }
                } catch (NumberFormatException e) {
                    Toast.makeText(this, "Nieprawidłowa maksymalna cena", Toast.LENGTH_SHORT).show();
                    return;
                }
            }

// Sprawdzenie czy min <= max dla gwiazdek
            if (intMinStars != -1 && intMaxStars != -1 && intMinStars > intMaxStars) {
                Toast.makeText(this, "Minimalna liczba gwiazdek nie może być większa niż maksymalna", Toast.LENGTH_SHORT).show();
                return;
            }

// Sprawdzenie czy min <= max dla ceny
            if (intMinPrice != -1 && intMaxPrice != -1 && intMinPrice > intMaxPrice) {
                Toast.makeText(this, "Minimalna cena nie może być większa niż maksymalna", Toast.LENGTH_SHORT).show();
                return;
            }



            Intent intent1 = new Intent(MainActivity.this, SearchResultsActivity.class);

            // Wysyłanie danych podstawowych
            intent1.putExtra("country", chosencountry);
            intent1.putExtra("city", chosencity);
            intent1.putExtra("startDate", startDate);
            intent1.putExtra("endDate", endDate);
            intent1.putExtra("guests", Integer.parseInt(guests.getText().toString()));

            // Zakres ceny
            if(intMinPrice !=-1) {
                String minPricewhole = Integer.toString(intMaxPrice * nights);
                intent1.putExtra("minPrice", minPricewhole);
            }
            if(intMaxPrice!= -1) {
                String maxPricewhole = Integer.toString(intMinPrice * nights);
                intent1.putExtra("maxPrice",maxPricewhole);
            }



            // Zakres gwiazdek
            intent1.putExtra("minStars", minStars.getText().toString());
            intent1.putExtra("maxStars", maxStars.getText().toString());

            // Sortowanie
            intent1.putExtra("sortBy", selectedSortBy);
            intent1.putExtra("sortOrder", selectedSortOrder);

            // Wybrane udogodnienia pokoju
            if (roomFacilities != null && selectedRoomFacilities != null) {
                ArrayList<String> selectedRoom = new ArrayList<>();
                for (int i = 0; i < roomFacilities.length; i++) {
                    if (selectedRoomFacilities[i]) {
                        selectedRoom.add(roomFacilities[i]);
                    }
                }
                intent1.putStringArrayListExtra("roomFacilities", selectedRoom);
            }

            // Wybrane udogodnienia hotelu
            if (hotelFacilities != null && selectedHotelFacilities != null) {
                ArrayList<String> selectedHotel = new ArrayList<>();
                for (int i = 0; i < hotelFacilities.length; i++) {
                    if (selectedHotelFacilities[i]) {
                        selectedHotel.add(hotelFacilities[i]);
                    }
                }
                intent1.putStringArrayListExtra("hotelFacilities", selectedHotel);
            }

            // Przekazanie danych użytkownika
            intent1.putExtra("User_data", userAndTokens);

            startActivity(intent1);
        });
        btnSortBy.setOnClickListener(v -> {
            String[] options = {"price", "stars"};
            new MaterialAlertDialogBuilder(this)
                    .setTitle("Sortuj według")
                    .setItems(options, (dialog, which) -> {
                        selectedSortBy = options[which];
                        btnSortBy.setText("Sortuj: " + selectedSortBy);
                    })
                    .show();
        });

        btnSortOrder.setOnClickListener(v -> {
            String[] options = {"asc", "desc"};
            new MaterialAlertDialogBuilder(this)
                    .setTitle("Kierunek sortowania")
                    .setItems(options, (dialog, which) -> {
                        selectedSortOrder = options[which];
                        btnSortOrder.setText("Kierunek: " + selectedSortOrder);
                    })
                    .show();
        });

    }

    @Override
    public void onClick(View v) {
        if (v.getId() == R.id.chooseRoomFacilities) {
            OkHttpClient client = new OkHttpClient();
            Request request = new Request.Builder().url("http://10.0.2.2:5000/room_facilities").build();
            client.newCall(request).enqueue(new Callback() {
                @Override
                public void onFailure(@NonNull Call call, @NonNull IOException e) {
                    runOnUiThread(() -> Toast.makeText(MainActivity.this, "Błąd połączenia", Toast.LENGTH_SHORT).show());
                }

                @Override
                public void onResponse(@NonNull Call call, @NonNull Response response) throws IOException {
                    String body = response.body().string();
                    JsonNode data = mapper.readTree(body);
                    roomFacilities = mapper.convertValue(data.get("room_facilities"), String[].class);
                    selectedRoomFacilities = new boolean[roomFacilities.length];

                    runOnUiThread(() -> new MaterialAlertDialogBuilder(MainActivity.this)
                            .setTitle("Wybierz udogodnienia pokoju")
                            .setMultiChoiceItems(roomFacilities, selectedRoomFacilities, (dialog, which, isChecked) -> {
                                selectedRoomFacilities[which] = isChecked;
                            })
                            .setPositiveButton("OK", (dialog, which) -> {
                                StringBuilder selected = new StringBuilder();
                                for (int i = 0; i < roomFacilities.length; i++) {
                                    if (selectedRoomFacilities[i]) {
                                        selected.append(roomFacilities[i]).append(", ");
                                    }
                                }
                                if (selected.length() > 0) {
                                    selected.setLength(selected.length() - 2); // usuń przecinek
                                }
                                chooseRoomFacilities.setText(selected.toString());
                            })
                            .setNegativeButton("Anuluj", null)
                            .show());
                }
            });
        }

        if (v.getId() == R.id.chooseHotelFacilities) {
            OkHttpClient client = new OkHttpClient();
            Request request = new Request.Builder().url("http://10.0.2.2:5000/hotel_facilities").build();
            client.newCall(request).enqueue(new Callback() {
                @Override
                public void onFailure(@NonNull Call call, @NonNull IOException e) {
                    runOnUiThread(() -> Toast.makeText(MainActivity.this, "Błąd połączenia", Toast.LENGTH_SHORT).show());
                }

                @Override
                public void onResponse(@NonNull Call call, @NonNull Response response) throws IOException {
                    String body = response.body().string();
                    JsonNode data = mapper.readTree(body);
                    hotelFacilities = mapper.convertValue(data.get("hotel_facilities"), String[].class);
                    selectedHotelFacilities = new boolean[hotelFacilities.length];

                    runOnUiThread(() -> new MaterialAlertDialogBuilder(MainActivity.this)
                            .setTitle("Wybierz udogodnienia hotelu")
                            .setMultiChoiceItems(hotelFacilities, selectedHotelFacilities, (dialog, which, isChecked) -> {
                                selectedHotelFacilities[which] = isChecked;
                            })
                            .setPositiveButton("OK", (dialog, which) -> {
                                StringBuilder selected = new StringBuilder();
                                for (int i = 0; i < hotelFacilities.length; i++) {
                                    if (selectedHotelFacilities[i]) {
                                        selected.append(hotelFacilities[i]).append(", ");
                                    }
                                }
                                if (selected.length() > 0) {
                                    selected.setLength(selected.length() - 2);
                                }
                                chooseHotelFacilities.setText(selected.toString());
                            })
                            .setNegativeButton("Anuluj", null)
                            .show());
                }
            });
        }

        if(v.getId() == R.id.chooseDate){ //wybieranie daty
            MaterialDatePicker.Builder<androidx.core.util.Pair<Long, Long>> builder =
                    MaterialDatePicker.Builder.dateRangePicker();

            builder.setTitleText("Wybierz zakres dat");

            MaterialDatePicker<androidx.core.util.Pair<Long, Long>> picker = builder.build();

            picker.show(getSupportFragmentManager(), "DATE_RANGE");

            picker.addOnPositiveButtonClickListener(selection -> {
                Long start = selection.first;
                Long end = selection.second;

                SimpleDateFormat sdf = new SimpleDateFormat("YYYY-MM-dd", Locale.getDefault());
                startDate = sdf.format(new Date(start));
                endDate = sdf.format(new Date(end));
                nights = (int) ((end-start)/86400000);
                Toast.makeText(this, "Wybrano: " +startDate + " – " + endDate , Toast.LENGTH_LONG).show();
                chooseDate.setText(startDate +" - " + endDate);
            });
        }
        if (v.getId() == R.id.chooseDestination) {
            OkHttpClient client = new OkHttpClient();
            Request request = new Request.Builder().url("http://10.0.2.2:5000/countries").build();
            client.newCall(request).enqueue(new Callback() {
                @Override
                public void onFailure(@NonNull Call call, @NonNull IOException e) {
                    e.printStackTrace();
                    runOnUiThread(() ->
                            Toast.makeText(MainActivity.this, "Błąd połączenia z serwerem", Toast.LENGTH_SHORT).show()
                    );
                }

                @Override
                public void onResponse(@NonNull Call call, @NonNull Response response) throws IOException {
                    if (!response.isSuccessful()) {
                        String body = response.body().string();
                        JsonNode error = mapper.readTree(body);
                        runOnUiThread(() ->
                                Toast.makeText(MainActivity.this, error.get("error").asText(), Toast.LENGTH_SHORT).show()
                        );
                    } else {
                        String body = response.body().string();
                        JsonNode data = mapper.readTree(body);
                        countries = data.get("countries").traverse(mapper).readValueAs(String[].class);

                        runOnUiThread(() -> {
                            final int[] wybrana = {-1};
                            new MaterialAlertDialogBuilder(MainActivity.this)
                                    .setTitle("Wybierz kraj")
                                    .setSingleChoiceItems(countries, wybrana[0], (dialog, which) -> {
                                        wybrana[0] = which;
                                    })
                                    .setPositiveButton("OK", (dialog, which) -> {
                                        if (wybrana[0] != -1) {
                                            chosencountry = countries[wybrana[0]];

                                            // 2. Wczytanie miast po kraju
                                            Request cityRequest = new Request.Builder()
                                                    .url("http://10.0.2.2:5000/cities?country=" + chosencountry)
                                                    .build();
                                            client.newCall(cityRequest).enqueue(new Callback() {
                                                @Override
                                                public void onFailure(@NonNull Call call, @NonNull IOException e) {
                                                    e.printStackTrace();
                                                    runOnUiThread(() ->
                                                            Toast.makeText(MainActivity.this, "Błąd pobierania miast", Toast.LENGTH_SHORT).show()
                                                    );
                                                }

                                                @Override
                                                public void onResponse(@NonNull Call call, @NonNull Response response) throws IOException {
                                                    if (!response.isSuccessful()) {
                                                        String body = response.body().string();
                                                        JsonNode error = mapper.readTree(body);
                                                        runOnUiThread(() ->
                                                                Toast.makeText(MainActivity.this, error.get("error").asText(), Toast.LENGTH_SHORT).show()
                                                        );
                                                    } else {
                                                        String body = response.body().string();
                                                        JsonNode cityData = mapper.readTree(body);
                                                        cities = cityData.get("cities").traverse(mapper).readValueAs(String[].class);
                                                        ArrayList<String> cities_full = new ArrayList<>();
                                                        cities_full.add("Dowolne miasto");
                                                        for(int i=0; i<cities.length; ++i)
                                                            cities_full.add(cities[i]);
                                                        cities = cities_full.toArray(new String[0]);
                                                        runOnUiThread(() -> {
                                                            final int[] wybraneMiasto = {-1};
                                                            new MaterialAlertDialogBuilder(MainActivity.this)
                                                                    .setTitle("Wybierz miasto")
                                                                    .setSingleChoiceItems(cities, wybraneMiasto[0], (dialog1, which1) -> {
                                                                        wybraneMiasto[0] = which1;
                                                                    })
                                                                    .setPositiveButton("OK", (dialog1, which1) -> {
                                                                        if (wybraneMiasto[0] != -1) {
                                                                            chosencity = cities[wybraneMiasto[0]];
                                                                            chooseDestination.setText(chosencountry + " " + chosencity);
                                                                        }
                                                                    })
                                                                    .setNegativeButton("Anuluj", null)
                                                                    .show();
                                                        });
                                                    }
                                                }
                                            });
                                        }
                                    })
                                    .setNegativeButton("Anuluj", null)
                                    .show();
                        });
                    }
                }
            });
        }
    }
}

