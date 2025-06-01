package com.example.aplikacja;

// Aktywność pozwalająca użytkownikowi zmienić swoje hasło.
import android.content.Intent;
import android.os.Bundle;
import android.os.Parcelable;
import android.text.TextUtils;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

import org.json.JSONObject;

import java.io.IOException;

public class ChangePassword extends AppCompatActivity {

    // Dane użytkownika przekazane przez Intent
    private UserAndTokens user;

    // Pola do wprowadzania starego i nowego hasła
    private EditText oldPasswordEditText;
    private EditText newPasswordEditText;
    private Button changePasswordButton;

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.change_password);

        // Inicjalizacja pól widoku
        oldPasswordEditText = findViewById(R.id.oldPasswordEditText);
        newPasswordEditText = findViewById(R.id.newPasswordEditText);
        changePasswordButton = findViewById(R.id.changePasswordButton);

        // Pobierz obiekt UserAndTokens z intencji
        Intent intent = getIntent();
        user = intent.getParcelableExtra("User_details");
        if (user == null) {
            Toast.makeText(this, "Brak danych użytkownika", Toast.LENGTH_SHORT).show();
            finish();
            return;
        }

        // Obsługa kliknięcia przycisku zmiany hasła
        changePasswordButton.setOnClickListener(v -> {
            String oldPass = oldPasswordEditText.getText().toString().trim();
            String newPass = newPasswordEditText.getText().toString().trim();

            // Walidacja pól wejściowych
            if (TextUtils.isEmpty(oldPass)) {
                oldPasswordEditText.setError("Wprowadź stare hasło");
                return;
            }
            if (TextUtils.isEmpty(newPass)) {
                newPasswordEditText.setError("Wprowadź nowe hasło");
                return;
            }
            if (newPass.length() < 6) {
                newPasswordEditText.setError("Hasło musi mieć co najmniej 6 znaków");
                return;
            }

            // Wywołanie metody zmieniającej hasło (API call)
            changePassword(oldPass, newPass);
        });
    }

    // Wysyła żądanie zmiany hasła do backendu
    private void changePassword(String oldPassword, String newPassword) {
        OkHttpClient client = new OkHttpClient();

        try {
            JSONObject json = new JSONObject();
            json.put("current_password", oldPassword);
            json.put("new_password", newPassword);

            MediaType JSON = MediaType.get("application/json; charset=utf-8");
            RequestBody body = RequestBody.create(json.toString(), JSON);

            String url = "http://10.0.2.2:5000/user/" + user.user_id + "/password";

            Request request = new Request.Builder()
                    .url(url)
                    .put(body)
                    .addHeader("Authorization", "Bearer " + user.access_token)
                    .build();

            client.newCall(request).enqueue(new Callback() {
                @Override
                public void onFailure(Call call, IOException e) {
                    // Obsługa błędu połączenia
                    runOnUiThread(() ->
                            Toast.makeText(ChangePassword.this,
                                    "Błąd połączenia: " + e.getMessage(),
                                    Toast.LENGTH_LONG).show());
                }

                @Override
                public void onResponse(Call call, Response response) throws IOException {
                    String responseBody = response.body().string();

                    runOnUiThread(() -> {
                        if (response.isSuccessful()) {
                            // Sukces - hasło zmienione
                            Toast.makeText(ChangePassword.this,
                                    "Hasło zostało zmienione pomyślnie!",
                                    Toast.LENGTH_LONG).show();
                            finish();
                        } else {
                            // Błąd zmiany hasła
                            Toast.makeText(ChangePassword.this,
                                    "Błąd zmiany hasła: " + responseBody,
                                    Toast.LENGTH_LONG).show();
                        }
                    });
                }
            });

        } catch (Exception e) {
            e.printStackTrace();
            Toast.makeText(this, "Błąd: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }
}
