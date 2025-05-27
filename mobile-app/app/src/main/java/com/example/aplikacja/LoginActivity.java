package com.example.aplikacja;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class LoginActivity extends AppCompatActivity implements View.OnClickListener {
    EditText email_view;
    ObjectMapper mapper;
    EditText password_view;
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        mapper = new ObjectMapper();
        setContentView(R.layout.login_activity);
        email_view = findViewById(R.id.email);
        password_view = findViewById(R.id.haslo);

        Button log_in = findViewById(R.id.log_in);
        Button register = findViewById(R.id.register);
        log_in.setOnClickListener(this);
        register.setOnClickListener(this);
    }

    @Override
    public void onClick(View v) {
        if(v.getId()==R.id.log_in){
            String email = email_view.getText().toString();
            String password = password_view.getText().toString();
            Log.d("My_app", email);
            if(email == null || password == null || email.length() ==0 || password.length() ==0){
                String result ="Wprowadź poprawne email i hasło";
                Toast.makeText(this,result, Toast.LENGTH_SHORT).show();
                return;
            }

            Map<String, String> dane = new HashMap<>();
            dane.put("email", email);
            dane.put("password", password);
            String json = null;
            try {
                json = mapper.writeValueAsString(dane);
            } catch (JsonProcessingException e) {
                throw new RuntimeException(e);
            }
            MediaType JSON = MediaType.get("application/json; charset=utf-8");
            RequestBody body = RequestBody.create(json, JSON);

            OkHttpClient client = new OkHttpClient();
            Request request = new Request.Builder().url("http://10.0.2.2:5000/login").post(body).build();

            client.newCall(request).enqueue(new Callback() {
                @Override
                public void onFailure(@NonNull Call call, @NonNull IOException e) {
                    e.printStackTrace();
                }

                @Override
                public void onResponse(@NonNull Call call, @NonNull Response response) throws IOException {
                    if(!response.isSuccessful()){

                        JsonNode error = mapper.readTree(response.body().string());
                        runOnUiThread(() -> {
                            Toast.makeText(LoginActivity.this, error.get("error").asText(), Toast.LENGTH_SHORT).show();
                        });
                    }
                    else{ //Udane logowanie
                        assert response.body() != null;
                        JsonNode data = mapper.readTree(response.body().string());
                        UserAndTokens userAndTokens = new UserAndTokens(data);
                        Log.d("My_app", "Zalogowano " + userAndTokens.getFirst_name() + " " + userAndTokens.getLast_name());
                        Intent intent = new Intent(LoginActivity.this, MainActivity.class);
                        intent.putExtra("User_data", userAndTokens);
                        startActivity(intent);
                    }
                }
            });

        }
        if(v.getId() == R.id.register){
            Intent intent = new Intent(this, RegisterActivity.class);
            startActivity(intent);
        }
    }
}
