package com.example.aplikacja;

// Aktywność rejestracji nowego użytkownika. Wysyła dane do backendu i obsługuje walidację formularza.
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.util.Patterns;
import android.widget.Toast;
import android.view.View;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.textfield.TextInputEditText;

import java.io.IOException;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.HashMap;
import java.util.Map;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class RegisterActivity extends AppCompatActivity {

    // Pola formularza rejestracji
    private TextInputEditText emailInput, passwordInput, birthDateInput,
            firstNameInput, lastNameInput, phoneNumberInput;
    private MaterialButton registerButton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.register_activity);

        // Inicjalizacja pól formularza
        emailInput = findViewById(R.id.email_input);
        passwordInput = findViewById(R.id.password_input);
        birthDateInput = findViewById(R.id.birth_date_input);
        firstNameInput = findViewById(R.id.first_name_input);
        lastNameInput = findViewById(R.id.last_name_input);
        phoneNumberInput = findViewById(R.id.phone_number_input);
        registerButton = findViewById(R.id.register_button);

        // Obsługa kliknięcia przycisku rejestracji
        registerButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                // Pobranie i przygotowanie danych z formularza
                String email = emailInput.getText().toString().trim();
                String password = passwordInput.getText().toString();
                String birthDate = birthDateInput.getText().toString().trim();
                String firstName = firstNameInput.getText().toString().trim();
                String lastName = lastNameInput.getText().toString().trim();
                String phoneNumber = phoneNumberInput.getText().toString().trim();
                ObjectMapper mapper = new ObjectMapper();

                // Prosta walidacja pól formularza
                if (email.isEmpty() || password.isEmpty() || birthDate.isEmpty() || firstName.isEmpty() || lastName.isEmpty() || phoneNumber.isEmpty()) {
                    Toast.makeText(RegisterActivity.this, "Wszystkie pola muszą być niepuste", Toast.LENGTH_SHORT).show();
                    return;
                }
                if(!Patterns.EMAIL_ADDRESS.matcher(email).matches()){
                    Toast.makeText(RegisterActivity.this, "Nieprawidłowy format email", Toast.LENGTH_SHORT).show();
                    return;
                }
                // Walidacja formatu daty urodzenia
                SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
                sdf.setLenient(false);
                try {
                    sdf.parse(birthDate);
                } catch (ParseException e) {
                    Toast.makeText(RegisterActivity.this, "Nieprawidłowy format daty", Toast.LENGTH_SHORT).show();
                    return;
                }
                // Przygotowanie danych do wysłania do backendu
                Map<String, String> dane = new HashMap<>();
                dane.put("email", email);
                dane.put("password", password);
                dane.put("birth_date", birthDate);
                dane.put("first_name", firstName);
                dane.put("last_name", lastName);
                dane.put("phone_number", phoneNumber);
                dane.put("role", "U");
                String json = null;
                try {
                    json = mapper.writeValueAsString(dane);
                } catch (JsonProcessingException e) {
                    throw new RuntimeException(e);
                }
                MediaType JSON = MediaType.get("application/json; charset=utf-8");
                RequestBody body = RequestBody.create(json, JSON);
                OkHttpClient client = new OkHttpClient();
                Request request = new Request.Builder().url("http://10.0.2.2:5000/register").post(body).build();
                // Wysłanie żądania rejestracji do backendu
                client.newCall(request).enqueue(new Callback() {
                    @Override
                    public void onFailure(@NonNull Call call, @NonNull IOException e) {
                        // Obsługa błędu połączenia
                        e.printStackTrace();
                    }

                    @Override
                    public void onResponse(@NonNull Call call, @NonNull Response response) throws IOException {
                        if(!response.isSuccessful()){
                            // Obsługa błędu rejestracji (np. email zajęty)
                            JsonNode error = mapper.readTree(response.body().string());
                            runOnUiThread(() -> {
                                Toast.makeText(RegisterActivity.this, error.get("error").asText(), Toast.LENGTH_SHORT).show();
                            });
                        }
                        else{
                            // Sukces rejestracji
                            assert response.body() != null;
                            Log.d("My_app", "Zarejestrowano ");
                            runOnUiThread(() -> {
                            Toast.makeText(RegisterActivity.this, "Pomyślnie zarejestrowano", Toast.LENGTH_SHORT).show();
                            });
                            finish();
                        }
                    }
                });


            }
        });
    }
}
